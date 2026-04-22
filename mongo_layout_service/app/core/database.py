from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from mongo_layout_service.app.core.config import get_settings


@lru_cache
def get_mongo_client() -> AsyncIOMotorClient:
    settings = get_settings()
    return AsyncIOMotorClient(settings.mongo_dsn)


def get_database() -> AsyncIOMotorDatabase:
    settings = get_settings()
    return get_mongo_client()[settings.mongo_db]
