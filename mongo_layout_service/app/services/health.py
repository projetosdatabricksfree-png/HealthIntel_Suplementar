from typing import Any

from mongo_layout_service.app.core.config import get_settings
from mongo_layout_service.app.core.database import get_database

settings = get_settings()


async def obter_prontidao() -> dict[str, Any]:
    await get_database().command("ping")
    return {
        "status": "ok",
        "servico": "layout-registry",
        "ambiente": settings.app_env,
        "dependencias": {"mongo": {"status": "ok", "database": settings.mongo_db}},
    }
