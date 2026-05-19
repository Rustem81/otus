"""Unit tests for Google OAuth2 integration."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services.oauth_google import GoogleOAuthService, OAUTH_STATE_TTL


# =============================================================================
# 16.1 get_authorization_url generates state and stores in Redis
# =============================================================================


@pytest.mark.asyncio
async def test_get_authorization_url_generates_state_and_stores_in_redis(
    test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test that get_authorization_url generates a state token and stores it in Redis with TTL."""
    service = GoogleOAuthService(test_db, mock_redis_client)

    authorization_url, state = await service.get_authorization_url()

    # State should be a 64-char hex string (32 bytes)
    assert len(state) == 64
    assert all(c in "0123456789abcdef" for c in state)

    # Should store state in Redis with TTL
    mock_redis_client.setex.assert_called_once_with(
        f"oauth_state:{state}",
        OAUTH_STATE_TTL,
        "1",
    )

    # Authorization URL should contain required params
    assert "accounts.google.com" in authorization_url
    assert "client_id=" in authorization_url
    assert "redirect_uri=" in authorization_url
    assert "response_type=code" in authorization_url
    assert "scope=openid" in authorization_url
    assert f"state={state}" in authorization_url


# =============================================================================
# 16.2 callback with invalid state → 400
# =============================================================================


@pytest.mark.asyncio
async def test_callback_invalid_state_returns_error(
    client: AsyncClient, mock_redis_client: AsyncMock
) -> None:
    """Test that OAuth callback with invalid state redirects with error."""
    # Redis returns None for the state (not found / expired)
    mock_redis_client.get = AsyncMock(return_value=None)

    response = await client.get(
        "/api/v1/auth/google/callback",
        params={"code": "fake-code", "state": "invalid-state"},
        follow_redirects=False,
    )

    # Should redirect to frontend with error
    assert response.status_code == 302
    assert "error=auth_failed" in response.headers["location"]


@pytest.mark.asyncio
async def test_callback_missing_params_returns_error(
    client: AsyncClient, mock_redis_client: AsyncMock
) -> None:
    """Test that OAuth callback without code/state redirects with error."""
    response = await client.get(
        "/api/v1/auth/google/callback",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "error=missing_params" in response.headers["location"]


# =============================================================================
# 16.3 callback with valid state → creates user, returns session cookie
# =============================================================================


@pytest.mark.asyncio
async def test_callback_valid_state_creates_user_and_sets_cookie(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test that valid OAuth callback creates a new user and sets session cookie."""
    # Mock Redis: state exists
    mock_redis_client.get = AsyncMock(return_value="1")
    mock_redis_client.delete = AsyncMock(return_value=1)
    mock_redis_client.hset = AsyncMock(return_value=1)
    mock_redis_client.expire = AsyncMock(return_value=True)

    # Mock Google token exchange and userinfo
    mock_token_response = AsyncMock()
    mock_token_response.status_code = 200
    mock_token_response.json = lambda: {"access_token": "google-access-token"}

    mock_userinfo_response = AsyncMock()
    mock_userinfo_response.status_code = 200
    mock_userinfo_response.json = lambda: {
        "id": "google-sub-123",
        "email": "newuser@gmail.com",
        "name": "New User",
    }

    with patch("app.services.oauth_google.httpx.AsyncClient") as mock_httpx:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_token_response)
        mock_client_instance.get = AsyncMock(return_value=mock_userinfo_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_httpx.return_value = mock_client_instance

        response = await client.get(
            "/api/v1/auth/google/callback",
            params={"code": "valid-auth-code", "state": "valid-state-token"},
            follow_redirects=False,
        )

    # Should redirect to frontend with success
    assert response.status_code == 302
    assert "success=1" in response.headers["location"]

    # Should set session cookie
    set_cookie = response.headers.get("set-cookie", "")
    assert "session_token=" in set_cookie
    assert "httponly" in set_cookie.lower()

    # Verify user was created in DB
    user_repo = UserRepository(test_db)
    user = await user_repo.get_by_email("newuser@gmail.com")
    assert user is not None
    assert user.oauth_provider == "google"
    assert user.oauth_subject == "google-sub-123"
    assert user.is_verified is True

    # Verify state was consumed (deleted from Redis)
    mock_redis_client.delete.assert_any_call("oauth_state:valid-state-token")


# =============================================================================
# 16.4 existing user by email → links oauth_provider/oauth_subject
# =============================================================================


@pytest.mark.asyncio
async def test_callback_existing_user_links_oauth_data(
    client: AsyncClient, test_db: AsyncSession, mock_redis_client: AsyncMock
) -> None:
    """Test that OAuth callback with existing user links OAuth provider data."""
    # Create existing user (registered via password)
    user_repo = UserRepository(test_db)
    existing_user = await user_repo.create(
        email="existing@gmail.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER,
        is_verified=True,
    )
    await test_db.commit()

    # Mock Redis: state exists
    mock_redis_client.get = AsyncMock(return_value="1")
    mock_redis_client.delete = AsyncMock(return_value=1)
    mock_redis_client.hset = AsyncMock(return_value=1)
    mock_redis_client.expire = AsyncMock(return_value=True)

    # Mock Google responses
    mock_token_response = AsyncMock()
    mock_token_response.status_code = 200
    mock_token_response.json = lambda: {"access_token": "google-access-token"}

    mock_userinfo_response = AsyncMock()
    mock_userinfo_response.status_code = 200
    mock_userinfo_response.json = lambda: {
        "id": "google-sub-456",
        "email": "existing@gmail.com",
        "name": "Existing User",
    }

    with patch("app.services.oauth_google.httpx.AsyncClient") as mock_httpx:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_token_response)
        mock_client_instance.get = AsyncMock(return_value=mock_userinfo_response)
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_httpx.return_value = mock_client_instance

        response = await client.get(
            "/api/v1/auth/google/callback",
            params={"code": "valid-auth-code", "state": "valid-state-token"},
            follow_redirects=False,
        )

    # Should redirect with success
    assert response.status_code == 302
    assert "success=1" in response.headers["location"]

    # Verify OAuth data was linked to existing user
    await test_db.refresh(existing_user)
    assert existing_user.oauth_provider == "google"
    assert existing_user.oauth_subject == "google-sub-456"

    # Session cookie should be set
    set_cookie = response.headers.get("set-cookie", "")
    assert "session_token=" in set_cookie
