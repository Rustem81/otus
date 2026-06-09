from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository

# =============================================================================
# Registration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, mock_redis_client: AsyncMock) -> None:
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123!"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test registration with duplicate email fails."""
    user_repo = UserRepository(test_db)
    await user_repo.create(
        email="existing@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "existing@example.com", "password": "SecurePass123!"},
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient) -> None:
    """Test registration with invalid email fails."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "SecurePass123!"},
    )

    assert response.status_code in (422, 400)  # Validation error


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient) -> None:
    """Test registration with short password fails."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test2@example.com", "password": "short"},
    )

    assert response.status_code in (422, 400)  # Validation error


# =============================================================================
# Login Tests
# =============================================================================


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test successful login returns access_token."""
    user_repo = UserRepository(test_db)
    await user_repo.create(
        email="login@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    mock_redis_client.hset = AsyncMock(return_value=1)
    mock_redis_client.expire = AsyncMock(return_value=True)

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "login@example.com"
    assert "access_token" in data
    assert data["access_token"] is not None


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test login with wrong password fails."""
    user_repo = UserRepository(test_db)
    await user_repo.create(
        email="wrongpass@example.com",
        hashed_password=get_password_hash("correctpassword"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient, mock_redis_client: AsyncMock) -> None:
    """Test login with non-existent user fails."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "password123"},
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


# =============================================================================
# Logout Tests
# =============================================================================


@pytest.mark.asyncio
async def test_logout_invalidates_session(
    client: AsyncClient, mock_redis_client: AsyncMock
) -> None:
    """Test logout deletes session from Redis."""
    mock_redis_client.delete = AsyncMock(return_value=1)

    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": "Bearer valid-session-token"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"
    mock_redis_client.delete.assert_called_once_with("session:valid-session-token")


@pytest.mark.asyncio
async def test_logout_without_token(client: AsyncClient) -> None:
    """Test logout without token returns 401."""
    response = await client.post("/api/v1/auth/logout")

    assert response.status_code in (401, 403)


# =============================================================================
# Protected Endpoint Tests
# =============================================================================


@pytest.mark.asyncio
async def test_me_endpoint_unauthorized(client: AsyncClient) -> None:
    """Test /me endpoint without authentication fails."""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint_authorized(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test /me endpoint with valid Bearer token returns user."""
    user_repo = UserRepository(test_db)
    user = await user_repo.create(
        email="me@example.com",
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

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer valid-session-token"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


# =============================================================================
# Admin Role Tests
# =============================================================================


@pytest.mark.asyncio
async def test_admin_endpoint_forbidden_for_user(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test that regular USER cannot access admin endpoints."""
    user_repo = UserRepository(test_db)
    user = await user_repo.create(
        email="regular@example.com",
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

    response = await client.get(
        "/api/v1/admin/errors",
        headers={"Authorization": "Bearer user-session-token"},
    )

    assert response.status_code == 403
    assert "insufficient" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_endpoint_allowed_for_admin(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test that ADMIN can access admin endpoints."""
    user_repo = UserRepository(test_db)
    user = await user_repo.create(
        email="admin@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.ADMIN,
        is_verified=True,
    )
    await test_db.commit()

    mock_redis_client.hgetall = AsyncMock(return_value={
        "user_id": user.id,
        "role": "ADMIN",
        "email": user.email,
    })
    mock_redis_client.exists = AsyncMock(return_value=1)

    response = await client.get(
        "/api/v1/admin/errors",
        headers={"Authorization": "Bearer admin-session-token"},
    )

    assert response.status_code == 200


# =============================================================================
# CSRF Tests
# =============================================================================


@pytest.mark.asyncio
async def test_csrf_required_for_mutating_requests(client: AsyncClient) -> None:
    """Test that POST requests without CSRF token are rejected (except exempt paths)."""
    # /api/v1/blacklist is NOT exempt — should require CSRF
    response = await client.post(
        "/api/v1/blacklist",
        json={"merchant_id": "test"},
        headers={"Authorization": "Bearer some-token"},
    )

    assert response.status_code == 403
    assert "csrf" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_csrf_exempt_for_login(client: AsyncClient, mock_redis_client: AsyncMock) -> None:
    """Test that login endpoint is exempt from CSRF."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@test.com", "password": "wrong"},
    )

    # Should get 400 (invalid credentials), NOT 403 (CSRF)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_csrf_valid_token_passes(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test that matching CSRF cookie + header passes validation."""
    csrf_token = "test-csrf-token-123"

    mock_redis_client.hgetall = AsyncMock(return_value={
        "user_id": "test-user",
        "role": "USER",
        "email": "test@test.com",
    })
    mock_redis_client.exists = AsyncMock(return_value=1)

    # Set CSRF cookie and matching header
    client.cookies.set("csrf_token", csrf_token)
    response = await client.post(
        "/api/v1/blacklist",
        json={"merchant_id": "merchant-1"},
        headers={
            "Authorization": "Bearer valid-token",
            "X-CSRF-Token": csrf_token,
        },
    )

    # Should NOT be 403 (CSRF passed) — may be 404/500 depending on DB state, but not CSRF error
    assert response.status_code != 403
