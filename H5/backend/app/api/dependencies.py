from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

# Bearer token authentication
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    bearer: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    redis: Annotated[Redis, Depends(get_redis)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Dependency to get current authenticated user from Bearer token.
    Extends session TTL on each request.
    """
    token = bearer.credentials if bearer else None

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    auth_service = AuthService(db, redis)

    user = await auth_service.get_user_by_session(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    # Extend session on activity
    await auth_service.extend_session(token)

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Dependency to ensure user is active (verified)."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    return current_user


class RoleChecker:
    """Dependency factory for role-based access control."""

    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if user_role_value(current_user.role) not in [r.value for r in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user


def user_role_value(role: UserRole | str) -> str:
    """Normalize role to string value."""
    return role.value if isinstance(role, UserRole) else role


# Predefined role checkers
require_user = Depends(RoleChecker([UserRole.USER, UserRole.ADMIN]))
require_admin = Depends(RoleChecker([UserRole.ADMIN]))


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> AsyncGenerator[AuthService, None]:
    """Factory dependency for AuthService."""
    yield AuthService(db, redis)
