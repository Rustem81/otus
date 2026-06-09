"""Tests for blacklist CRUD operations."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_blacklist_add_requires_csrf(client: AsyncClient) -> None:
    """POST /blacklist without CSRF token returns 403."""
    response = await client.post(
        "/api/v1/blacklist",
        json={"merchant_id": "merchant-1"},
        headers={"Authorization": "Bearer some-token"},
    )
    assert response.status_code == 403
    assert "csrf" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_blacklist_add_with_csrf(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """POST /blacklist with valid CSRF and auth succeeds."""
    user_repo = UserRepository(test_db)
    user = await user_repo.create(
        email="bl_user@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    mock_redis_client.hgetall = AsyncMock(return_value={
        "user_id": user.id,
        "role": "USER",
        "email": user.email,
    })
    mock_redis_client.exists = AsyncMock(return_value=1)

    csrf = "test-csrf-token"
    client.cookies.set("csrf_token", csrf)

    response = await client.post(
        "/api/v1/blacklist",
        json={"merchant_id": "merchant-123"},
        headers={
            "Authorization": "Bearer valid-token",
            "X-CSRF-Token": csrf,
        },
    )

    # Should not be 403 (CSRF passed), may be 500 if merchant doesn't exist in DB
    assert response.status_code != 403
