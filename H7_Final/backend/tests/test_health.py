"""Unit tests for health check endpoints.

Tests:
- GET /health: all deps ok → status "ok"
- GET /health: one dep down → status "degraded"
- GET /health: all deps down → status "degraded" (not "down")
- GET /health/live: always returns 200 {"status": "ok"}
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Tests for GET /health."""

    async def test_all_deps_ok(self, client: AsyncClient, mock_redis_client: AsyncMock):
        """When all dependencies are healthy, status should be 'ok'."""
        # mock_redis_client.ping already returns True by default from conftest
        mock_response = httpx.Response(200, json={"status": 1, "message": "pong"})

        with patch("app.api.v1.endpoints.health.httpx.AsyncClient") as mock_httpx:
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.get = AsyncMock(return_value=mock_response)
            mock_httpx_instance.__aenter__ = AsyncMock(return_value=mock_httpx_instance)
            mock_httpx_instance.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.return_value = mock_httpx_instance

            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert data["version"] == "1.0.0"
        assert data["dependencies"]["postgres"] == "ok"
        assert data["dependencies"]["redis"] == "ok"
        assert data["dependencies"]["mock_server"] == "ok"

    async def test_redis_down_returns_degraded(self, client: AsyncClient, mock_redis_client: AsyncMock):
        """When Redis is down, status should be 'degraded'."""
        mock_redis_client.ping = AsyncMock(side_effect=ConnectionError("Redis unavailable"))
        mock_response = httpx.Response(200, json={"status": 1, "message": "pong"})

        with patch("app.api.v1.endpoints.health.httpx.AsyncClient") as mock_httpx:
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.get = AsyncMock(return_value=mock_response)
            mock_httpx_instance.__aenter__ = AsyncMock(return_value=mock_httpx_instance)
            mock_httpx_instance.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.return_value = mock_httpx_instance

            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["redis"] == "down"
        assert data["dependencies"]["postgres"] == "ok"
        assert data["dependencies"]["mock_server"] == "ok"

    async def test_mock_server_down_returns_degraded(self, client: AsyncClient, mock_redis_client: AsyncMock):
        """When mock server is unreachable, status should be 'degraded'."""
        with patch("app.api.v1.endpoints.health.httpx.AsyncClient") as mock_httpx:
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_httpx_instance.__aenter__ = AsyncMock(return_value=mock_httpx_instance)
            mock_httpx_instance.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.return_value = mock_httpx_instance

            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["mock_server"] == "down"
        assert data["dependencies"]["postgres"] == "ok"
        assert data["dependencies"]["redis"] == "ok"

    async def test_all_deps_down_returns_degraded_not_down(
        self, client: AsyncClient, mock_redis_client: AsyncMock, test_db
    ):
        """When ALL dependencies are down, status should still be 'degraded' (not 'down')."""
        # Make redis fail
        mock_redis_client.ping = AsyncMock(side_effect=ConnectionError("Redis unavailable"))

        # Make postgres fail by patching the db execute
        with patch("app.api.v1.endpoints.health._check_postgres", return_value="down"):
            with patch("app.api.v1.endpoints.health.httpx.AsyncClient") as mock_httpx:
                mock_httpx_instance = AsyncMock()
                mock_httpx_instance.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
                mock_httpx_instance.__aenter__ = AsyncMock(return_value=mock_httpx_instance)
                mock_httpx_instance.__aexit__ = AsyncMock(return_value=None)
                mock_httpx.return_value = mock_httpx_instance

                response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        # Per design: only "ok" or "degraded", never "down" at top level
        assert data["status"] == "degraded"
        assert data["dependencies"]["postgres"] == "down"
        assert data["dependencies"]["redis"] == "down"
        assert data["dependencies"]["mock_server"] == "down"

    async def test_response_contains_version(self, client: AsyncClient, mock_redis_client: AsyncMock):
        """Health response should include the APP_VERSION from settings."""
        mock_response = httpx.Response(200, json={"status": 1, "message": "pong"})

        with patch("app.api.v1.endpoints.health.httpx.AsyncClient") as mock_httpx:
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.get = AsyncMock(return_value=mock_response)
            mock_httpx_instance.__aenter__ = AsyncMock(return_value=mock_httpx_instance)
            mock_httpx_instance.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.return_value = mock_httpx_instance

            response = await client.get("/health")

        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0


@pytest.mark.asyncio
class TestHealthLiveEndpoint:
    """Tests for GET /health/live."""

    async def test_liveness_always_200(self, client: AsyncClient):
        """Liveness probe should always return 200 with status ok."""
        response = await client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}

    async def test_liveness_no_dependency_checks(self, client: AsyncClient, mock_redis_client: AsyncMock):
        """Liveness probe should succeed even if dependencies are down."""
        # Make redis fail
        mock_redis_client.ping = AsyncMock(side_effect=ConnectionError("Redis unavailable"))

        response = await client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}
