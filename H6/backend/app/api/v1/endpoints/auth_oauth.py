"""OAuth2 Google authentication endpoints."""

from __future__ import annotations

from typing import Annotated
from urllib.parse import urlencode

import structlog
from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.redis import get_redis
from app.services.oauth_google import GoogleOAuthService

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()


def _get_frontend_url() -> str:
    """Get frontend URL from CORS origins (first origin)."""
    origins = settings.BACKEND_CORS_ORIGINS.split(",")
    return origins[0].strip() if origins else "http://localhost:5173"


@router.get("/google")
async def google_login(
    redis: Annotated[Redis, Depends(get_redis)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RedirectResponse:
    """Initiate Google OAuth2 flow — redirect to Google consent screen."""
    service = GoogleOAuthService(db, redis)
    authorization_url, _state = await service.get_authorization_url()
    return RedirectResponse(url=authorization_url, status_code=302)


@router.get("/google/callback")
async def google_callback(
    code: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
    redis: Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """
    Handle Google OAuth2 callback.
    Verifies state, exchanges code, creates session, sets cookie,
    and redirects to frontend.
    """
    frontend_url = _get_frontend_url()

    # Handle user cancellation or Google error
    if error:
        logger.warning("oauth_callback_error", error=error)
        params = urlencode({"error": error})
        return RedirectResponse(url=f"{frontend_url}/auth/callback?{params}", status_code=302)

    # Validate required params
    if not code or not state:
        logger.warning("oauth_callback_missing_params", has_code=bool(code), has_state=bool(state))
        params = urlencode({"error": "missing_params"})
        return RedirectResponse(url=f"{frontend_url}/auth/callback?{params}", status_code=302)

    try:
        service = GoogleOAuthService(db, redis)
        _user, session_token = await service.handle_callback(code, state)

        # Redirect to frontend with success
        response = RedirectResponse(
            url=f"{frontend_url}/auth/callback?success=1",
            status_code=302,
        )

        # Set HttpOnly session cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
            max_age=24 * 60 * 60,  # 24 hours
        )

        return response

    except ValueError as e:
        logger.warning("oauth_callback_failed", error=str(e))
        params = urlencode({"error": "auth_failed"})
        return RedirectResponse(url=f"{frontend_url}/auth/callback?{params}", status_code=302)
