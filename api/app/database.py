from __future__ import annotations

import asyncpg

from api.app.core.config import get_settings
from api.app.core.database import SessionLocal, engine, get_db_session

settings = get_settings()
_asyncpg_pool: asyncpg.Pool | None = None


async def get_asyncpg_pool() -> asyncpg.Pool:
    global _asyncpg_pool
    if _asyncpg_pool is None:
        _asyncpg_pool = await asyncpg.create_pool(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            min_size=1,
            max_size=5,
        )
    return _asyncpg_pool


__all__ = ["engine", "SessionLocal", "get_db_session", "get_asyncpg_pool"]
