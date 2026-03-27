from __future__ import annotations


class AppException(Exception):
    """Base application exception with HTTP status code and error code."""

    def __init__(self, status_code: int, detail: str, error_code: str) -> None:
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)
