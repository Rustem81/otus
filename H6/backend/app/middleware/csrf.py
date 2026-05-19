"""CSRF protection middleware using double-submit cookie pattern.

For SPA with Bearer token auth, CSRF is not strictly required (tokens are not
sent automatically like cookies). However, this middleware adds defense-in-depth
for any cookie-based flows and demonstrates the pattern.

How it works:
1. On any response, a CSRF cookie is set (readable by JavaScript).
2. For mutating requests (POST, PUT, DELETE), the middleware checks that
   the X-CSRF-Token header matches the csrf_token cookie value.
3. Safe methods (GET, HEAD, OPTIONS) and exempt paths skip validation.
"""

from __future__ import annotations

import os
import secrets
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"

# Paths exempt from CSRF (public endpoints that don't need protection)
CSRF_EXEMPT_PATHS = frozenset({
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
})

# Prefixes exempt from CSRF (Bearer-only auth endpoints)
CSRF_EXEMPT_PREFIXES = (
    "/api/v1/auth/",
)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Double-submit cookie CSRF protection.

    - Sets csrf_token cookie on every response (httponly=False so JS can read it).
    - Validates X-CSRF-Token header matches cookie on POST/PUT/DELETE.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Safe methods — no CSRF check needed
        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            response = await call_next(request)
            self._ensure_csrf_cookie(request, response)
            return response

        # Exempt paths
        path = request.url.path
        if path in CSRF_EXEMPT_PATHS or path.startswith(CSRF_EXEMPT_PREFIXES):
            response = await call_next(request)
            self._ensure_csrf_cookie(request, response)
            return response

        # Validate CSRF for mutating requests
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)

        if not cookie_token or not header_token:
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token missing"},
            )

        if not secrets.compare_digest(cookie_token, header_token):
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token mismatch"},
            )

        # Valid — proceed
        response = await call_next(request)
        return response

    def _ensure_csrf_cookie(self, request: Request, response: Response) -> None:
        """Set CSRF cookie if not already present."""
        if CSRF_COOKIE_NAME not in request.cookies:
            token = secrets.token_urlsafe(32)
            # Use Secure flag in production (HTTPS environments)
            is_production = bool(os.getenv("RAILWAY_ENVIRONMENT"))
            response.set_cookie(
                key=CSRF_COOKIE_NAME,
                value=token,
                httponly=False,  # JS must read this
                secure=is_production,
                samesite="lax",
                max_age=86400,
            )
