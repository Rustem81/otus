from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.redis import get_redis
from app.main import app
from app.models.base import Base

# Use SQLite with custom type handling for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def mock_redis() -> AsyncMock:
    """Create a mock Redis client for testing."""
    redis_mock = AsyncMock(spec=Redis)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.getdel = AsyncMock(return_value=None)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.hset = AsyncMock(return_value=1)
    redis_mock.hgetall = AsyncMock(return_value={})
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.exists = AsyncMock(return_value=0)
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.zremrangebyscore = AsyncMock(return_value=0)
    redis_mock.zcard = AsyncMock(return_value=0)
    redis_mock.zadd = AsyncMock(return_value=1)
    redis_mock.aclose = AsyncMock()
    return redis_mock


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine with SQLite (ARRAY columns stored as JSON text)."""
    from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
    from sqlalchemy.dialects.postgresql import ARRAY, JSONB
    from sqlalchemy import String, Text

    # Patch ARRAY and JSONB to work with SQLite
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        future=True,
    )

    # Replace PostgreSQL-specific types for SQLite
    from app.models import base as models_base
    import app.models.trader_profile
    import app.models.advertisement
    import app.models.saved_filters

    # Create tables, replacing ARRAY with String and JSONB with Text
    from sqlalchemy import MetaData, Table, Column, String as SAString, Text as SAText

    async with engine.begin() as conn:
        # Use render_as_batch for SQLite compatibility
        await conn.run_sync(_create_tables_sqlite_compat)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


def _create_tables_sqlite_compat(connection):
    """Create tables with SQLite-compatible types."""
    from sqlalchemy.dialects.postgresql import ARRAY, JSONB
    from sqlalchemy import String, Text

    # Monkey-patch ARRAY and JSONB compilation for SQLite
    from sqlalchemy.ext.compiler import compiles

    @compiles(ARRAY, "sqlite")
    def compile_array_sqlite(type_, compiler, **kw):
        return "TEXT"

    @compiles(JSONB, "sqlite")
    def compile_jsonb_sqlite(type_, compiler, **kw):
        return "TEXT"

    Base.metadata.create_all(connection)


@pytest_asyncio.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    session_factory = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def mock_redis_client() -> AsyncMock:
    """Provide a mock Redis client."""
    return mock_redis()


@pytest_asyncio.fixture
async def client(
    test_db: AsyncSession, mock_redis_client: AsyncMock
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with mocked dependencies."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    async def override_get_redis() -> AsyncGenerator[AsyncMock, None]:
        yield mock_redis_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    # Patch rate limiter's redis to use mock
    from app.middleware.rate_limiter import RateLimitMiddleware
    for middleware in app.user_middleware:
        if hasattr(middleware, 'cls') and middleware.cls == RateLimitMiddleware:
            break

    # Patch the module-level redis_client used by rate limiter
    import app.middleware.rate_limiter as rl_module
    original_redis = rl_module.redis_client
    rl_module.redis_client = mock_redis_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    rl_module.redis_client = original_redis
    app.dependency_overrides.clear()
