from __future__ import annotations

import hashlib
from pathlib import Path

import httpx
from sqlalchemy import text

from ingestao.app.carregar_postgres import SessionLocal
from ingestao.app.config import get_settings

SEM_PARSER = {"pdf", "xls", "xlsx", "json", "xml", "desconhecido"}


def _landing_path(fonte: dict, competencia: str | None = None) -> Path:
    settings = get_settings()
    snapshot = competencia or "snapshot"
    nome = fonte.get("nome_arquivo") or Path(str(fonte["url"])).name
    return (
        Path(settings.ingestao_landing_path)
        / "ans"
        / str(fonte["familia"])
        / str(fonte["dataset_codigo"])
        / snapshot
        / "raw"
        / nome
    )


async def _registrar_arquivo(fonte: dict, payload: dict) -> None:
    sql = text(
        """
        insert into plataforma.arquivo_fonte_ans (
            fonte_id, dataset_codigo, familia, url, caminho_landing, nome_arquivo,
            hash_arquivo, tamanho_bytes, last_modified_origem, baixado_em, status,
            erro_mensagem, tentativa, updated_at
        ) values (
            :fonte_id, :dataset_codigo, :familia, :url, :caminho_landing, :nome_arquivo,
            :hash_arquivo, :tamanho_bytes, :last_modified_origem, now(), :status,
            :erro_mensagem, :tentativa, now()
        )
        on conflict do nothing
        """
    )
    async with SessionLocal() as session:
        await session.execute(
            sql,
            {
                "fonte_id": fonte.get("id"),
                "dataset_codigo": fonte["dataset_codigo"],
                "familia": fonte["familia"],
                "url": fonte["url"],
                "caminho_landing": payload.get("caminho_landing"),
                "nome_arquivo": payload.get("nome_arquivo") or fonte.get("nome_arquivo"),
                "hash_arquivo": payload.get("hash_arquivo"),
                "tamanho_bytes": payload.get("tamanho_bytes"),
                "last_modified_origem": fonte.get("last_modified"),
                "status": payload["status"],
                "erro_mensagem": payload.get("erro_mensagem"),
                "tentativa": payload.get("tentativa", 1),
            },
        )
        await session.commit()


async def _hash_ja_baixado(hash_arquivo: str) -> bool:
    sql = text(
        """
        select 1
        from plataforma.arquivo_fonte_ans
        where hash_arquivo = :hash_arquivo
          and status in ('baixado', 'carregado', 'baixado_sem_parser')
        limit 1
        """
    )
    async with SessionLocal() as session:
        result = await session.execute(sql, {"hash_arquivo": hash_arquivo})
        return result.scalar_one_or_none() is not None


async def baixar_fonte_ans(fonte: dict, *, competencia: str | None = None) -> dict:
    settings = get_settings()
    destino = _landing_path(fonte, competencia)
    destino.parent.mkdir(parents=True, exist_ok=True)
    timeout = httpx.Timeout(
        connect=settings.ans_http_connect_timeout_seconds,
        read=settings.ans_http_read_timeout_seconds,
        write=settings.ans_http_write_timeout_seconds,
        pool=settings.ans_http_pool_timeout_seconds,
    )
    headers = {"User-Agent": settings.ans_http_user_agent}
    sha = hashlib.sha256()
    tamanho = 0

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            follow_redirects=True,
        ) as client:
            async with client.stream("GET", str(fonte["url"])) as response:
                response.raise_for_status()
                with destino.open("wb") as arquivo:
                    async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        arquivo.write(chunk)
                        sha.update(chunk)
                        tamanho += len(chunk)
    except httpx.HTTPError as exc:
        payload = {
            "status": "erro_download",
            "erro_mensagem": str(exc),
            "nome_arquivo": fonte.get("nome_arquivo"),
            "tamanho_bytes": tamanho or fonte.get("tamanho_bytes"),
        }
        await _registrar_arquivo(fonte, payload)
        return {**payload, "dataset_codigo": fonte["dataset_codigo"], "familia": fonte["familia"]}

    hash_arquivo = sha.hexdigest()
    status = "baixado_sem_parser" if str(fonte.get("tipo_arquivo")) in SEM_PARSER else "baixado"
    if await _hash_ja_baixado(hash_arquivo):
        status = "ignorado_duplicata"

    payload = {
        "status": status,
        "caminho_landing": str(destino),
        "nome_arquivo": fonte.get("nome_arquivo") or destino.name,
        "hash_arquivo": hash_arquivo,
        "tamanho_bytes": tamanho,
        "tentativa": 1,
    }
    await _registrar_arquivo(fonte, payload)
    return {
        **payload,
        "dataset_codigo": fonte["dataset_codigo"],
        "familia": fonte["familia"],
        "url": fonte["url"],
    }
