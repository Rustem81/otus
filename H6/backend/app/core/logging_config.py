"""Structured logging configuration using structlog.

Auto-detects format:
- JSON (machine-parseable) when RAILWAY_ENVIRONMENT is set or LOG_FORMAT=json
- Console (pretty, colored) for local development (default when no RAILWAY_ENVIRONMENT)
"""

from __future__ import annotations

import logging
import os

import structlog


def configure_logging() -> None:
    """Configure structlog with JSON (prod) or console (dev) renderer.

    Detection logic:
    1. If LOG_FORMAT env var is explicitly set → use that value
    2. If RAILWAY_ENVIRONMENT env var exists → json
    3. Otherwise → console
    """
    log_format = os.getenv(
        "LOG_FORMAT",
        "json" if os.getenv("RAILWAY_ENVIRONMENT") else "console",
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "console":
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
