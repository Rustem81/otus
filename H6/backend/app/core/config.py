from __future__ import annotations

from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_file=".env")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://mexc:mexc_secret@localhost:5432/mexc_p2p"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Google OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:9000,http://127.0.0.1:9000"

    # P2P data source
    P2P_DATA_SOURCE: str = "mock"  # "p2p_army" | "mock"
    P2P_ARMY_API_KEY: str = ""
    P2P_ARMY_BASE_URL: str = "https://p2p.army/v1/api"
    P2P_MOCK_BASE_URL: str = "http://mock-server:8001/v1/api"

    # Sentry
    SENTRY_DSN_BACKEND: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0

    # Metrics
    METRICS_ENABLED: bool = True

    # Application version (informational, returned in /health)
    APP_VERSION: str = "1.0.0"

    # Polling
    POLLING_INTERVAL_SEC: int = 10
    INACTIVE_TTL_SEC: int = 15

    # LLM
    OPENAI_API_KEY: str = ""
    LLM_CACHE_TTL_SEC: int = 600
    LLM_MAX_CHARS: int = 300

    # Scoring weights
    SCORING_WEIGHT_RATING: float = 0.3
    SCORING_WEIGHT_TRADES: float = 0.25
    SCORING_WEIGHT_SUCCESS_RATE: float = 0.3
    SCORING_WEIGHT_SPEED: float = 0.15

    # Integral score weights
    INTEGRAL_WEIGHT_PRICE: float = 0.4
    INTEGRAL_WEIGHT_RISK: float = 0.35
    INTEGRAL_WEIGHT_PROFILE: float = 0.25

    def validate_secret_key(self) -> None:
        """Warn if SECRET_KEY is using the default insecure value."""
        import logging
        import os

        if self.SECRET_KEY == "change-me-in-production":
            if os.getenv("RAILWAY_ENVIRONMENT"):
                raise ValueError(
                    "SECRET_KEY must be set to a secure value in production. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            logging.getLogger(__name__).warning(
                "SECRET_KEY is using the default insecure value. "
                "Set a secure SECRET_KEY environment variable for production."
            )


@lru_cache
def get_settings() -> Settings:
    """Cached singleton for application settings."""
    settings = Settings()
    settings.validate_secret_key()
    return settings
