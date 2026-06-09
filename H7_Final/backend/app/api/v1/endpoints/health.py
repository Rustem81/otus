"""Health check endpoints.

Provides:
- GET /health — full health check with dependency status and version
- GET /health/live — lightweight liveness probe (no dependency checks)
"""

from __future__ import annotations

import httpx
import structlog
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.redis import get_redis

router = APIRouter(tags=["system"])
logger = structlog.get_logger()
settings = get_settings()


async def _check_postgres(db: AsyncSession) -> str:
    """Check PostgreSQL connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:
        logger.error("health_check_postgres_unavailable", error=str(exc))
        return "down"


async def _check_redis(redis: Redis) -> str:
    """Check Redis connectivity."""
    try:
        await redis.ping()
        return "ok"
    except Exception as exc:
        logger.error("health_check_redis_unavailable", error=str(exc))
        return "down"


async def _check_mock_server() -> str:
    """Check mock server connectivity via HTTP GET to /v1/api/ping."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.P2P_MOCK_BASE_URL}/ping")
            if response.status_code == 200:
                return "ok"
            return "down"
    except Exception as exc:
        logger.error("health_check_mock_server_unavailable", error=str(exc))
        return "down"


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """Full health check with dependency status.

    Returns "ok" (all deps up) or "degraded" (some deps down).
    Always HTTP 200 — external monitors check the status field.
    """
    dependencies = {
        "postgres": await _check_postgres(db),
        "redis": await _check_redis(redis),
        "mock_server": await _check_mock_server(),
    }

    status = "ok" if all(v == "ok" for v in dependencies.values()) else "degraded"

    return {
        "status": status,
        "version": settings.APP_VERSION,
        "dependencies": dependencies,
    }


@router.get("/health/live")
async def liveness() -> dict:
    """Lightweight liveness probe — no dependency checks."""
    return {"status": "ok"}
