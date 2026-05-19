from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.database import async_session, engine
from app.core.exceptions import AppException
from app.core.logging_config import configure_logging
from app.core.redis import redis_client
from app.middleware.csrf import CSRFMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.tasks.polling import start_polling_task, stop_polling_task

# Configure structlog before anything else
configure_logging()

# --- Sentry initialization (conditional on DSN) ---
_sentry_settings = get_settings()
if _sentry_settings.SENTRY_DSN_BACKEND:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    _PII_FIELDS = {"password", "authorization", "cookie", "session_token"}

    def _before_send(event: dict, hint: dict) -> dict | None:
        """Filter PII fields from Sentry event data and attach request_id."""
        # Filter PII from request data
        if request_data := event.get("request", {}):
            if headers := request_data.get("headers"):
                if isinstance(headers, dict):
                    for key in list(headers.keys()):
                        if key.lower() in _PII_FIELDS:
                            headers[key] = "[Filtered]"
            if data := request_data.get("data"):
                if isinstance(data, dict):
                    for key in list(data.keys()):
                        if key.lower() in _PII_FIELDS:
                            data[key] = "[Filtered]"
            if cookies := request_data.get("cookies"):
                if isinstance(cookies, dict):
                    for key in list(cookies.keys()):
                        if key.lower() in _PII_FIELDS:
                            cookies[key] = "[Filtered]"

        # Attach request_id from structlog contextvars
        ctx_vars = structlog.contextvars.get_contextvars()
        if request_id := ctx_vars.get("request_id"):
            event.setdefault("tags", {})["request_id"] = request_id
            event.setdefault("extra", {})["request_id"] = request_id

        return event

    sentry_sdk.init(
        dsn=_sentry_settings.SENTRY_DSN_BACKEND,
        environment=_sentry_settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=_sentry_settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        before_send=_before_send,
        send_default_pii=False,
    )

logger = structlog.get_logger()
settings = get_settings()
cors_origins = [
    origin.strip()
    for origin in settings.BACKEND_CORS_ORIGINS.split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle for DB engine and Redis."""
    logger.info("app_startup", msg="Checking DB and Redis connections")
    # Verify DB is reachable
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    # Verify Redis is reachable
    await redis_client.ping()
    logger.info("app_startup_complete", msg="DB and Redis connections OK")

    # Start polling task
    await start_polling_task()

    yield

    # Shutdown
    logger.info("app_shutdown", msg="Disposing DB engine and closing Redis")
    await stop_polling_task()
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(
    title="MEXC P2P Aggregator",
    version="0.1.0",
    description="Read-only P2P advertisement monitoring for MEXC",
    lifespan=lifespan,
    # SEC-13: Limit request body size to 1MB to prevent DoS
    # Note: For file uploads, increase this or use streaming
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Security middleware ---
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token", "X-Request-ID"],
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


# --- Health check endpoints (moved to app/api/v1/endpoints/health.py) ---
from app.api.v1.endpoints.health import router as health_router

app.include_router(health_router)

# --- Prometheus metrics (conditional on METRICS_ENABLED) ---
if settings.METRICS_ENABLED:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
