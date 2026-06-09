"""X-Request-ID middleware for request tracing.

Generates or propagates a unique request ID for each HTTP request,
binds it to structlog contextvars so all logs within the request
include the request_id field, and sets the X-Request-ID response header.
"""

from __future__ import annotations

from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that manages X-Request-ID header and structlog context."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Use incoming X-Request-ID if present, otherwise generate a new one
        request_id = request.headers.get("X-Request-ID") or str(uuid4())

        # Bind request_id to structlog contextvars for all logs in this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        try:
            response = await call_next(request)
        finally:
            # Unbind after response to avoid leaking context between requests
            structlog.contextvars.unbind_contextvars("request_id")

        # Set X-Request-ID on the response header
        response.headers["X-Request-ID"] = request_id
        return response
