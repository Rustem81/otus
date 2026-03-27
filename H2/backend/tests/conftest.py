from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import get_db
from app.core.redis import get_redis
from app.main import app
from app.models.base import Base

# Test database URL (use in-memory SQLite for tests)
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
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        # Rollback after test
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
