from redis.asyncio import Redis

from api.app.core.config import get_settings

settings = get_settings()
redis_client = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


async def get_redis() -> Redis:
    return redis_client
