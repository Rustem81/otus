from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.database import async_session, engine
from app.core.exceptions import AppException
from app.core.redis import redis_client
from app.middleware.csrf import CSRFMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.tasks.polling import start_polling_task, stop_polling_task

logger = logging.getLogger(__name__)
settings = get_settings()
cors_origins = [
    origin.strip()
    for origin in settings.BACKEND_CORS_ORIGINS.split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle for DB engine and Redis."""
    logger.info("Starting up — checking DB and Redis connections")
    # Verify DB is reachable
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    # Verify Redis is reachable
    await redis_client.ping()
    logger.info("DB and Redis connections OK")

    # Start polling task
    await start_polling_task()

    yield

    # Shutdown
    logger.info("Shutting down — disposing DB engine and closing Redis")
    await stop_polling_task()
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(
    title="MEXC P2P Aggregator",
    version="0.1.0",
    description="Read-only P2P advertisement monitoring for MEXC",
    lifespan=lifespan,
)

# --- Security middleware (order matters: last added = first executed) ---
app.add_middleware(CSRFMiddleware)
app.add_middleware(RateLimitMiddleware)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Exception handler ---
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "detail": exc.detail},
    )


# --- API router ---
app.include_router(api_v1_router)


# --- Health check ---
@app.get("/health", tags=["system"])
async def health() -> dict:
    """Check DB and Redis connectivity, return aggregated status."""
    result: dict = {"status": "ok", "dependencies": {}}

    # Check PostgreSQL
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        result["dependencies"]["postgres"] = "ok"
    except Exception as exc:
        logger.error("Health check — PostgreSQL unavailable: %s", exc)
        result["dependencies"]["postgres"] = "down"
        result["status"] = "degraded"

    # Check Redis
    try:
        await redis_client.ping()
        result["dependencies"]["redis"] = "ok"
    except Exception as exc:
        logger.error("Health check — Redis unavailable: %s", exc)
        result["dependencies"]["redis"] = "down"
        result["status"] = "degraded"

    # If both are down, mark as down
    if all(v == "down" for v in result["dependencies"].values()):
        result["status"] = "down"

    return result
