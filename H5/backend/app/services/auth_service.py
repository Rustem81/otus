from __future__ import annotations

from datetime import datetime, timezone

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    generate_session_token,
    generate_verification_token,
    get_password_hash,
    get_session_expiry,
    get_verification_expiry,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication business logic."""

    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self._session = session
        self._redis = redis
        self._user_repo = UserRepository(session)

    async def register(self, email: str, password: str) -> tuple[User, str]:
        """
        Register a new user.

        Returns:
            Tuple of (created_user, verification_token)
        """
        # Check if user already exists
        if await self._user_repo.exists_by_email(email):
            raise ValueError("User with this email already exists")

        # Create user
        hashed_password = get_password_hash(password)
        user = await self._user_repo.create(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.USER,
            is_verified=False,
        )

        # Generate verification token
        verification_token = generate_verification_token()
        expiry = get_verification_expiry()

        # Store in Redis (TTL 24 hours)
        await self._redis.setex(
            f"verify:{verification_token}",
            int((expiry - datetime.now(timezone.utc)).total_seconds()),
            user.id,
        )

        return user, verification_token

    async def verify_email(self, token: str) -> User:
        """Verify user email with token."""
        user_id = await self._redis.get(f"verify:{token}")
        if not user_id:
            raise ValueError("Invalid or expired verification token")

        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if user.is_verified:
            raise ValueError("Email already verified")

        # Update user
        await self._user_repo.update(user, is_verified=True)

        # Delete token
        await self._redis.delete(f"verify:{token}")

        return user

    async def login(self, email: str, password: str) -> tuple[User, str]:
        """
        Authenticate user and create session.

        Returns:
            Tuple of (user, session_token)
        """
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        if not user.is_verified:
            raise ValueError("Email not verified")

        # Create session
        session_token = generate_session_token()
        expiry = get_session_expiry()
        ttl_seconds = int((expiry - datetime.now(timezone.utc)).total_seconds())

        # Store session in Redis
        await self._redis.hset(
            f"session:{session_token}",
            mapping={
                "user_id": user.id,
                "role": user.role if isinstance(user.role, str) else user.role.value,
                "email": user.email,
            },
        )
        await self._redis.expire(f"session:{session_token}", ttl_seconds)

        return user, session_token

    async def logout(self, session_token: str) -> None:
        """Logout user by deleting session."""
        await self._redis.delete(f"session:{session_token}")

    async def logout_all_sessions(self, user_id: str) -> None:
        """Logout user from all sessions (not implemented for MVP)."""
        # For MVP, we only track single session per token
        # In production, would scan for all user sessions
        pass

    async def get_user_by_session(self, session_token: str) -> User | None:
        """Get user by session token."""
        session_data = await self._redis.hgetall(f"session:{session_token}")
        if not session_data:
            return None

        user_id = session_data.get("user_id")
        if not user_id:
            return None

        return await self._user_repo.get_by_id(user_id)

    async def extend_session(self, session_token: str) -> bool:
        """Extend session TTL on activity."""
        session_key = f"session:{session_token}"
        exists = await self._redis.exists(session_key)
        if not exists:
            return False

        # Extend TTL to 24 hours
        await self._redis.expire(session_key, 24 * 60 * 60)
        return True
