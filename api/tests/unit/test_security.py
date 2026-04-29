from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Request

from api.app.core.security import gerar_hash_sha256, hash_ip
from api.app.middleware import rate_limit


def test_gerar_hash_sha256_deve_ser_deterministico() -> None:
    assert gerar_hash_sha256("abc") == gerar_hash_sha256("abc")


def test_hash_ip_deve_retornar_none_sem_ip() -> None:
    assert hash_ip(None) is None


def _criar_request_rate_limit(path: str = "/v1/operadoras") -> Request:
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "query_string": b"",
            "headers": [],
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 12345),
        }
    )
    request.state.chave_api_id = "chave_teste"
    request.state.limite_rpm = 10
    return request


class _RedisIndisponivel:
    async def incrby(self, chave: str, peso: int) -> int:
        raise RuntimeError("redis indisponivel")

    async def expire(self, chave: str, ttl: int) -> None:
        raise AssertionError("expire nao deve ser chamado")


@pytest.mark.asyncio
async def test_rate_limit_deve_falhar_aberto_apenas_quando_configurado(monkeypatch) -> None:
    request = _criar_request_rate_limit()
    monkeypatch.setattr(rate_limit, "redis_client", _RedisIndisponivel())
    monkeypatch.setattr(
        rate_limit,
        "settings",
        SimpleNamespace(app_rate_limit_rpm=60, rate_limit_falha_aberta=True),
    )

    await rate_limit.aplicar_rate_limit(request)

    assert request.state.rate_limit_status == "indisponivel_fail_open"


@pytest.mark.asyncio
async def test_rate_limit_deve_falhar_fechado_fora_de_local(monkeypatch) -> None:
    request = _criar_request_rate_limit()
    monkeypatch.setattr(rate_limit, "redis_client", _RedisIndisponivel())
    monkeypatch.setattr(
        rate_limit,
        "settings",
        SimpleNamespace(app_rate_limit_rpm=60, rate_limit_falha_aberta=False),
    )

    with pytest.raises(HTTPException) as exc:
        await rate_limit.aplicar_rate_limit(request)

    assert exc.value.status_code == 503
    assert exc.value.detail["codigo"] == "RATE_LIMIT_INDISPONIVEL"
