from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.redis import redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis sliding window.

    Limits:
    - Login: 5 attempts per minute per IP
    - Register: 3 attempts per hour per IP
    """

    def __init__(self, app) -> None:
        super().__init__(app)
        self._redis = redis_client

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path
        method = request.method

        # Only check POST requests to auth endpoints
        if method != "POST":
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        if path.endswith("/login"):
            if not await self._check_limit(
                f"ratelimit:login:{client_ip}", limit=5, window=60
            ):
                return Response(
                    content='{"detail": "Too many login attempts. Try again later."}',
                    status_code=429,
                    media_type="application/json",
                )

        elif path.endswith("/register"):
            if not await self._check_limit(
                f"ratelimit:register:{client_ip}", limit=3, window=3600
            ):
                return Response(
                    content='{"detail": "Too many registration attempts. Try again later."}',
                    status_code=429,
                    media_type="application/json",
                )

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def _check_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Check if request is within rate limit using sliding window.

        Args:
            key: Redis key for this limit
            limit: Maximum number of requests
            window: Time window in seconds

        Returns:
            True if allowed, False if limit exceeded
        """
        now = int(time.time())
        window_start = now - window

        # Remove old entries outside window
        await self._redis.zremrangebyscore(key, 0, window_start)

        # Count current requests in window
        current = await self._redis.zcard(key)

        if current >= limit:
            return False

        # Add current request
        await self._redis.zadd(key, {str(now): now})
        await self._redis.expire(key, window)

        return True
