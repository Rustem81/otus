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

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:9000,http://127.0.0.1:9000"

    # P2P data source
    P2P_DATA_SOURCE: str = "mock"  # "p2p_army" | "mock"
    P2P_ARMY_API_KEY: str = ""
    P2P_ARMY_BASE_URL: str = "https://p2p.army/v1/api"
    P2P_MOCK_BASE_URL: str = "http://mock-server:8001/v1/api"

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


@lru_cache
def get_settings() -> Settings:
    """Cached singleton for application settings."""
    return Settings()
