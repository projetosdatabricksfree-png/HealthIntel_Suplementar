from typing import Any

import httpx
from sqlalchemy import text

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client

settings = get_settings()


async def verificar_postgres() -> dict[str, str]:
    async with SessionLocal() as session:
        await session.execute(text("select 1"))
    return {"status": "ok"}


async def verificar_redis() -> dict[str, str]:
    await redis_client.ping()
    return {"status": "ok"}


async def verificar_layout_service() -> dict[str, str]:
    async with httpx.AsyncClient(
        base_url=settings.layout_service_url,
        timeout=5.0,
        headers={"X-Service-Token": settings.layout_service_token},
    ) as client:
        response = await client.get("/prontidao")
    response.raise_for_status()
    return {"status": "ok"}


async def obter_prontidao() -> dict[str, Any]:
    dependencias: dict[str, dict[str, str]] = {}
    verificacoes = {
        "postgres": verificar_postgres,
        "redis": verificar_redis,
        "layout_service": verificar_layout_service,
    }

    pronto = True
    for nome, verificacao in verificacoes.items():
        try:
            dependencias[nome] = await verificacao()
        except Exception as exc:  # pragma: no cover - exercitado via rota
            pronto = False
            dependencias[nome] = {"status": "erro", "mensagem": str(exc)}

    return {
        "status": "ok" if pronto else "indisponivel",
        "ambiente": settings.app_env,
        "versao": settings.app_versao,
        "dependencias": dependencias,
    }
