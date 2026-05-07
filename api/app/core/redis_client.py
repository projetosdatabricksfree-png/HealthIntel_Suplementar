from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import UTC, datetime

from redis.asyncio import Redis
from sqlalchemy import text

from api.app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_FAILURE_THRESHOLD = 3
_RESET_TIMEOUT_S = 300  # circuito permanece aberto 5 min antes de tentar novamente

_cb_failures: int = 0
_cb_opened_at: float = 0.0
_cb_lock = asyncio.Lock()

redis_client = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


def _circuit_open() -> bool:
    if _cb_failures < _FAILURE_THRESHOLD:
        return False
    return (time.monotonic() - _cb_opened_at) < _RESET_TIMEOUT_S


async def _log_circuit_event(evento: str, mensagem: str) -> None:
    """Registra abertura/fechamento do circuit breaker em plataforma.job."""
    try:
        from api.app.core.database import SessionLocal  # evita import circular no topo

        async with SessionLocal() as session:
            await session.execute(
                text(
                    """
                    INSERT INTO plataforma.job (id, dag_id, nome_job, fonte_ans, status,
                        iniciado_em, finalizado_em, registro_processado, registro_com_falha,
                        mensagem_erro)
                    VALUES (:id, 'api_redis', :evento, 'redis', :status,
                        :ts, :ts, 0, 0, :msg)
                    """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "evento": evento,
                    "status": "alerta" if evento == "circuit_opened" else "sucesso",
                    "ts": datetime.now(tz=UTC),
                    "msg": mensagem,
                },
            )
            await session.commit()
    except Exception:
        pass  # nunca propagar falha de log de infra


async def _record_failure() -> None:
    global _cb_failures, _cb_opened_at
    async with _cb_lock:
        _cb_failures += 1
        if _cb_failures == _FAILURE_THRESHOLD:
            _cb_opened_at = time.monotonic()
            msg = f"circuit breaker aberto apos {_FAILURE_THRESHOLD} falhas consecutivas"
            logger.error("redis:%s", msg)
            asyncio.ensure_future(_log_circuit_event("circuit_opened", msg))


async def _record_success() -> None:
    global _cb_failures, _cb_opened_at
    async with _cb_lock:
        was_open = _cb_failures >= _FAILURE_THRESHOLD
        _cb_failures = 0
        _cb_opened_at = 0.0
        if was_open:
            msg = "circuit breaker resetado — Redis respondeu com sucesso"
            logger.info("redis:%s", msg)
            asyncio.ensure_future(_log_circuit_event("circuit_reset", msg))


async def cache_get(key: str) -> str | None:
    """Get com circuit breaker. Retorna None silenciosamente se Redis estiver fora."""
    if _circuit_open():
        return None
    try:
        value = await redis_client.get(key)
        await _record_success()
        return value
    except Exception:
        await _record_failure()
        return None


async def cache_set(key: str, value: str, ex: int | None = None) -> None:
    """Set com circuit breaker. Silencioso se Redis estiver fora."""
    if _circuit_open():
        return
    try:
        await redis_client.set(key, value, ex=ex)
        await _record_success()
    except Exception:
        await _record_failure()


async def cache_delete(key: str) -> None:
    if _circuit_open():
        return
    try:
        await redis_client.delete(key)
    except Exception:
        await _record_failure()


def is_circuit_open() -> bool:
    return _circuit_open()


async def get_redis() -> Redis:
    return redis_client
