from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


# =============================================================================
# Registration Tests
# =============================================================================


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, mock_redis_client: AsyncMock) -> None:
    """Test successful user registration."""
    # Get CSRF token first
    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123!"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "verification" in data["message"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_email(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test registration with duplicate email fails."""
    # Create existing user
    user_repo = UserRepository(test_db)
    await user_repo.create(
        email="existing@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    # Get CSRF token
    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    # Try to register with same email
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "existing@example.com", "password": "SecurePass123!"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient) -> None:
    """Test registration with invalid email fails."""
    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "SecurePass123!"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient) -> None:
    """Test registration with short password fails."""
    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "short"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 422  # Validation error


# =============================================================================
# Login Tests
# =============================================================================


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test successful login."""
    # Create verified user
    user_repo = UserRepository(test_db)
    await user_repo.create(
        email="login@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    # Mock session storage
    mock_redis_client.hset = AsyncMock(return_value=1)
    mock_redis_client.expire = AsyncMock(return_value=True)

    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "login@example.com"
    assert "session_token" in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test login with wrong password fails."""
    # Create verified user
    user_repo = UserRepository(test_db)
    await user_repo.create(
        email="wrongpass@example.com",
        hashed_password=get_password_hash("correctpassword"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_unverified_email(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test login with unverified email fails."""
    # Create unverified user
    user_repo = UserRepository(test_db)
    await user_repo.create(
        email="unverified@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER,
        is_verified=False,
    )
    await test_db.commit()

    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "unverified@example.com", "password": "password123"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient, mock_redis_client: AsyncMock) -> None:
    """Test login with non-existent user fails."""
    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "password123"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


# =============================================================================
# Email Verification Tests
# =============================================================================


@pytest.mark.asyncio
async def test_verify_email_success(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test successful email verification."""
    # Create unverified user
    user_repo = UserRepository(test_db)
    user = await user_repo.create(
        email="verify@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.USER,
        is_verified=False,
    )
    await test_db.commit()

    # Mock Redis to return user_id for verification token
    mock_redis_client.get = AsyncMock(return_value=user.id)

    response = await client.get("/api/v1/auth/verify-email/test-token-123")

    assert response.status_code == 200
    assert "verified successfully" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_verify_email_invalid_token(client: AsyncClient, mock_redis_client: AsyncMock) -> None:
    """Test verification with invalid token fails."""
    mock_redis_client.get = AsyncMock(return_value=None)

    response = await client.get("/api/v1/auth/verify-email/invalid-token")

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


# =============================================================================
# CSRF Tests
# =============================================================================


@pytest.mark.asyncio
async def test_csrf_protection(client: AsyncClient) -> None:
    """Test that mutating requests require CSRF token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123!"},
        # No CSRF header
    )

    assert response.status_code == 403
    assert "csrf" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_csrf_token_endpoint(client: AsyncClient) -> None:
    """Test CSRF token endpoint returns token."""
    response = await client.get("/api/v1/auth/csrf-token")

    assert response.status_code == 200
    assert "csrf_token" in response.json()


# =============================================================================
# Rate Limiting Tests
# =============================================================================


@pytest.mark.asyncio
async def test_login_rate_limit(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test login rate limiting after 5 attempts."""
    # Create verified user
    user_repo = UserRepository(test_db)
    await user_repo.create(
        email="ratelimit@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    # Mock rate limit exceeded
    mock_redis_client.zcard = AsyncMock(return_value=5)

    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ratelimit@example.com", "password": "password123"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 429
    assert "too many" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_rate_limit(client: AsyncClient, mock_redis_client: AsyncMock) -> None:
    """Test registration rate limiting after 3 attempts."""
    # Mock rate limit exceeded
    mock_redis_client.zcard = AsyncMock(return_value=3)

    csrf_response = await client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123!"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 429
    assert "too many" in response.json()["detail"].lower()


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
    """Test /me endpoint with valid session returns user."""
    # Create verified user
    user_repo = UserRepository(test_db)
    user = await user_repo.create(
        email="me@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    # Mock session data
    mock_redis_client.hgetall = AsyncMock(return_value={
        "user_id": user.id,
        "role": "USER",
        "email": user.email,
    })
    mock_redis_client.exists = AsyncMock(return_value=1)

    # Set session cookie
    client.cookies.set("session_token", "valid-session-token")

    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
