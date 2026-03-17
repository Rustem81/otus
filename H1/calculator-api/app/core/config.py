"""Application configuration module.

Loads settings from environment variables and .env file using pydantic-settings.
Follows the fastapi-templates skill pattern with lru_cache singleton.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """Return a singleton Settings instance (cached via lru_cache)."""
    return Settings()
