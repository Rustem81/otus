"""Logging configuration for the Calculator API.

Configures structured logging with level from Settings.
"""

import logging

from app.core.config import get_settings

logger = logging.getLogger("calculator_api")


def configure_logging() -> None:
    """Configure the root logger level from application settings."""
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.setLevel(level)
