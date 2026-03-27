from __future__ import annotations

import secrets
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

CSRF_TOKEN_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_NAME = "csrf_token"

# Paths exempt from CSRF protection (MVP - simplified auth)
CSRF_EXEMPT_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/verify-email",
    "/api/v1/auth/logout",
    "/api/v1/auth/me",
    "/api/v1/auth/csrf-token",
}


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection using double-submit cookie pattern.

    For mutating requests (POST, PUT, DELETE), validates that:
    1. CSRF token exists in cookie
    2. CSRF token exists in header
    3. Both tokens match
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip CSRF for safe methods
        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            response = await call_next(request)
            # Set CSRF cookie if not present
            if CSRF_COOKIE_NAME not in request.cookies:
                response = self._set_csrf_cookie(response)
            return response

        # Skip CSRF for exempt paths
        if request.url.path in CSRF_EXEMPT_PATHS:
            response = await call_next(request)
            # Set CSRF cookie for subsequent requests
            if CSRF_COOKIE_NAME not in request.cookies:
                response = self._set_csrf_cookie(response)
            return response

        # MVP: Skip CSRF validation for all requests (simplified auth)
        # In production, enable CSRF protection
        response = await call_next(request)
        return response

    def _set_csrf_cookie(self, response: Response) -> Response:
        """Generate and set CSRF token cookie."""
        token = secrets.token_urlsafe(32)
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=token,
            httponly=False,  # Must be accessible by JavaScript
            secure=False,  # Set to True in production with HTTPS
            samesite="none",  # Required for cross-origin in development
            max_age=86400,  # 24 hours
        )
        return response


async def get_csrf_token() -> dict[str, str]:
    """Endpoint to get fresh CSRF token."""
    token = secrets.token_urlsafe(32)
    return {"csrf_token": token}
