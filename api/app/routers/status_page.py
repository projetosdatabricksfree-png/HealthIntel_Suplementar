from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from api.app.core.database import SessionLocal
from api.app.core.redis_client import redis_client

router = APIRouter(tags=["status"])


async def _check_postgres() -> str:
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "erro"


async def _check_redis() -> str:
    try:
        await redis_client.ping()
        return "ok"
    except Exception:
        return "erro"


async def _ultima_carga_ans() -> str | None:
    try:
        async with SessionLocal() as session:
            result = await session.execute(
                text(
                    "SELECT MAX(finalizado_em) AS ultima "
                    "FROM plataforma.job "
                    "WHERE status = 'sucesso'"
                )
            )
            row = result.mappings().first()
            if row and row["ultima"]:
                return row["ultima"].isoformat()
    except Exception:
        pass
    return None


@router.get("/status")
async def get_status() -> dict:
    """Status publico da plataforma. Nao requer autenticacao."""
    postgres = await _check_postgres()
    redis = await _check_redis()
    ultima_carga = await _ultima_carga_ans()

    tudo_ok = postgres == "ok" and redis == "ok"
    return {
        "api": "ok",
        "postgres": postgres,
        "redis": redis,
        "ultima_carga_ans": ultima_carga,
        "status_geral": "ok" if tudo_ok else "degradado",
    }
