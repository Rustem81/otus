"""Google OAuth2 service for authentication via Google accounts."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

import httpx
import structlog
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.metrics import auth_logins_total
from app.core.security import generate_session_token
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

logger = structlog.get_logger()
settings = get_settings()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

OAUTH_STATE_TTL = 600  # 10 minutes


class GoogleOAuthService:
    """Service handling Google OAuth2 flow."""

    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self._session = session
        self._redis = redis
        self._user_repo = UserRepository(session)

    async def get_authorization_url(self) -> tuple[str, str]:
        """
        Generate OAuth state, store in Redis with TTL 10min,
        and return the Google authorization URL.

        Returns:
            Tuple of (authorization_url, state)
        """
        state = secrets.token_hex(32)

        # Store state in Redis with TTL
        await self._redis.setex(
            f"oauth_state:{state}",
            OAUTH_STATE_TTL,
            "1",
        )

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        authorization_url = f"{GOOGLE_AUTH_URL}?{query_string}"

        logger.info("oauth_authorization_url_generated", state=state[:8] + "...")
        return authorization_url, state

    async def handle_callback(self, code: str, state: str) -> tuple[User, str]:
        """
        Handle OAuth callback: verify state, exchange code, get userinfo,
        find/create user, create session.

        Returns:
            Tuple of (user, session_token)

        Raises:
            ValueError: If state is invalid or Google API fails
        """
        # Verify and consume state (one-time use via GET+DELETE)
        state_key = f"oauth_state:{state}"
        state_value = await self._redis.get(state_key)
        if not state_value:
            logger.warning("oauth_invalid_state", state=state[:8] + "...")
            raise ValueError("Invalid or expired OAuth state")

        # Delete state immediately (one-time use)
        await self._redis.delete(state_key)

        # Exchange code for tokens
        token_data = await self._exchange_code(code)
        access_token = token_data.get("access_token")
        if not access_token:
            logger.error("oauth_no_access_token", response_keys=list(token_data.keys()))
            raise ValueError("Failed to obtain access token from Google")

        # Get user info from Google
        userinfo = await self._get_userinfo(access_token)
        email = userinfo.get("email")
        if not email:
            logger.error("oauth_no_email_in_userinfo")
            raise ValueError("Google did not provide email address")

        google_sub = userinfo.get("id", "")

        # Find or create user
        user = await self._user_repo.get_by_email(email)
        if user:
            # Link OAuth data to existing user
            if not user.oauth_provider:
                await self._user_repo.update(
                    user,
                    oauth_provider="google",
                    oauth_subject=google_sub,
                )
                logger.info("oauth_linked_existing_user", user_id=user.id, email=email)
        else:
            # Create new user with OAuth data
            user = await self._user_repo.create(
                email=email,
                hashed_password="",  # OAuth users don't have a password
                role=UserRole.USER,
                is_verified=True,  # Google guarantees email verification
                oauth_provider="google",
                oauth_subject=google_sub,
            )
            logger.info("oauth_created_new_user", user_id=user.id, email=email)

        # Create session in Redis
        session_token = generate_session_token()
        session_key = f"session:{session_token}"
        await self._redis.hset(
            session_key,
            mapping={
                "user_id": user.id,
                "role": user.role if isinstance(user.role, str) else user.role.value,
                "email": user.email,
                "created_at": datetime.now(UTC).isoformat(),
            },
        )
        await self._redis.expire(session_key, 24 * 60 * 60)  # 24 hours

        logger.info("oauth_login_success", user_id=user.id, email=email)
        auth_logins_total.labels(method="google").inc()
        return user, session_token

    async def _exchange_code(self, code: str) -> dict:
        """Exchange authorization code for access token via Google token endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code != 200:
            logger.error(
                "oauth_token_exchange_failed",
                status_code=response.status_code,
            )
            raise ValueError("Failed to exchange authorization code")

        return response.json()

    async def _get_userinfo(self, access_token: str) -> dict:
        """Get user information from Google userinfo endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if response.status_code != 200:
            logger.error(
                "oauth_userinfo_failed",
                status_code=response.status_code,
            )
            raise ValueError("Failed to get user info from Google")

        return response.json()
