"""Pytest fixtures for Calculator API tests.

Follows the fastapi-templates skill testing pattern with dependency overrides.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    """Return a TestClient wrapping the FastAPI application."""
    return TestClient(app)
