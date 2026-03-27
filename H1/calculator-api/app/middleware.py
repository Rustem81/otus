"""Logging middleware for the Calculator API.

Logs HTTP method, path, and processing time for every incoming request.
Errors are logged at ERROR level. Log level is configurable via Settings.
"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("calculator_api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that logs method, path, status code, and duration for each request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "%s %s - error after %.2fms: %s",
                request.method,
                request.url.path,
                duration_ms,
                exc,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000

        if response.status_code >= 500:
            logger.error(
                "%s %s %d %.2fms",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
        elif response.status_code >= 400:
            logger.warning(
                "%s %s %d %.2fms",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
        else:
            logger.info(
                "%s %s %d %.2fms",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )

        return response
