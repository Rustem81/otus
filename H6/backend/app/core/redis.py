from __future__ import annotations

from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()

redis_client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis() -> AsyncGenerator[Redis, None]:
    """FastAPI dependency — yields the shared Redis client."""
    yield redis_client
