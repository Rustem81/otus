"""Calculator API application entry point.

Follows the fastapi-templates skill pattern:
- Lifespan context manager for startup/shutdown
- Versioned API router (api/v1)
- Dependency injection
- Centralized configuration via core/config
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware import LoggingMiddleware
from app.api.v1.router import api_router

logger = logging.getLogger("calculator_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    configure_logging()
    logger.info("Calculator API starting up")
    yield
    logger.info("Calculator API shutting down")


def create_app() -> FastAPI:
    """Application factory that creates and configures a FastAPI instance."""
    settings = get_settings()

    application = FastAPI(
        title="Calculator API",
        description="REST API для выполнения арифметических операций",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.add_middleware(LoggingMiddleware)

    # Versioned API routes
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled error: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return application


app = create_app()
