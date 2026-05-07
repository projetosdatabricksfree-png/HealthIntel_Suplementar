from __future__ import annotations

import asyncio
import hashlib
import random
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import httpx
from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal
from ingestao.app.config import get_settings


def _nome_arquivo(url: str, dataset_codigo: str, competencia: str) -> str:
    nome = Path(urlparse(url).path).name
    if nome:
        return nome
    return f"{dataset_codigo}_{competencia}.dat"


async def _baixar_com_retry(url: str, settings) -> tuple[bytes, int]:
    """Retorna (conteudo, tentativas_usadas)."""
    timeout = httpx.Timeout(
        connect=settings.ans_http_connect_timeout_seconds,
        read=settings.ans_http_read_timeout_seconds,
        write=settings.ans_http_write_timeout_seconds,
        pool=settings.ans_http_pool_timeout_seconds,
    )
    headers = {"User-Agent": settings.ans_http_user_agent}
    max_retries = settings.ans_http_max_retries
    backoff_base = settings.ans_http_backoff_seconds
    ultimo_erro: Exception | None = None

    for tentativa in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(
                timeout=timeout, follow_redirects=True, headers=headers
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content, tentativa
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            ultimo_erro = exc
            if tentativa < max_retries:
                espera = backoff_base * (2 ** (tentativa - 1)) + random.uniform(0, 1)
                await asyncio.sleep(espera)

    raise RuntimeError(
        f"download falhou apos {max_retries} tentativas: {url}"
    ) from ultimo_erro


async def baixar_arquivo(dataset_codigo: str, competencia: str, url: str) -> dict[str, str]:
    """Baixa uma fonte ANS para landing local com hash estavel do conteudo e retry automatico."""

    settings = get_settings()
    destino_dir = Path(settings.ingestao_landing_path) / dataset_codigo / str(competencia)
    destino_dir.mkdir(parents=True, exist_ok=True)

    nome_arquivo = _nome_arquivo(url, dataset_codigo, str(competencia))
    destino = destino_dir / nome_arquivo

    job_id = str(uuid.uuid4())
    iniciado_em = datetime.now(tz=UTC)

    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                INSERT INTO plataforma.job (id, dag_id, nome_job, fonte_ans, status,
                    iniciado_em, registro_processado, registro_com_falha)
                VALUES (:id, 'landing', :nome_job, :fonte_ans, 'iniciado',
                    :iniciado_em, 0, 0)
                """
            ),
            {
                "id": job_id,
                "nome_job": f"baixar_{nome_arquivo}",
                "fonte_ans": dataset_codigo,
                "iniciado_em": iniciado_em,
            },
        )
        await session.commit()

    try:
        if destino.exists() and settings.ans_allow_landing_cache:
            conteudo = destino.read_bytes()
            tentativas = 0
        else:
            conteudo, tentativas = await _baixar_com_retry(url, settings)
            destino.write_bytes(conteudo)

        resultado = {
            "dataset_codigo": dataset_codigo,
            "competencia": str(competencia),
            "url": url,
            "path": str(destino),
            "arquivo_origem": nome_arquivo,
            "hash_arquivo": hashlib.sha256(conteudo).hexdigest(),
            "tentativas_http": str(tentativas),
        }

        async with SessionLocal() as session:
            await session.execute(
                text(
                    """
                    UPDATE plataforma.job
                    SET status = 'sucesso', finalizado_em = :fim, registro_processado = 1
                    WHERE id = :id
                    """
                ),
                {"id": job_id, "fim": datetime.now(tz=UTC)},
            )
            await session.commit()

        return resultado

    except Exception as exc:
        async with SessionLocal() as session:
            await session.execute(
                text(
                    """
                    UPDATE plataforma.job
                    SET status = 'erro', finalizado_em = :fim,
                        registro_com_falha = 1, mensagem_erro = :msg
                    WHERE id = :id
                    """
                ),
                {"id": job_id, "fim": datetime.now(tz=UTC), "msg": str(exc)[:500]},
            )
            await session.commit()
        raise
