from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

# Cookie-based session authentication (fallback)
session_cookie = APIKeyCookie(name="session_token", auto_error=False)

# Bearer token authentication (MVP)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    session_token: Annotated[str | None, Depends(session_cookie)],
    bearer: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    redis: Annotated[Redis, Depends(get_redis)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Dependency to get current authenticated user from session.
    Supports both cookie and Bearer token (MVP).
    Extends session TTL on each request.
    """
    # Try Bearer token first (MVP)
    token = bearer.credentials if bearer else None
    
    # Fallback to cookie
    if not token:
        token = session_token
    
    if not token:
        # Try to get from query param for WebSocket support
        token = request.query_params.get("session_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    auth_service = AuthService(db, redis)

    # Get user and extend session
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

    def __call__(
        self, user: Annotated["User", Depends(get_current_active_user)]
    ) -> "User":
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user


# Predefined role dependencies - use functions to defer evaluation
def require_user_dependency() -> "User":
    return RoleChecker([UserRole.USER, UserRole.ADMIN])


def require_admin_dependency() -> "User":
    return RoleChecker([UserRole.ADMIN])


require_user = Depends(require_user_dependency)
require_admin = Depends(require_admin_dependency)


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> AsyncGenerator[AuthService, None]:
    """Factory dependency for AuthService."""
    yield AuthService(db, redis)
