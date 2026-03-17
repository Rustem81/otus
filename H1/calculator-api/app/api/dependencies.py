"""Shared API dependencies.

Central place for dependency injection providers used across endpoints.
"""

from app.core.config import Settings, get_settings


def get_app_settings() -> Settings:
    """Dependency for injecting application settings."""
    return get_settings()
