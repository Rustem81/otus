from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.services.p2p_source.interface import P2PDataSource

settings = get_settings()


class MockP2PClient(P2PDataSource):
    """
    Client for mock P2P server (local development).

    Connects to mock-server running on port 8001.
    """

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url or settings.P2P_MOCK_BASE_URL
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_order_book(
        self,
        market: str,
        fiat: str,
        asset: str,
        side: str,
        payment_method: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Get order book from mock server."""
        url = f"{self._base_url}/get_p2p_order_book"

        payload = {
            "market": market,
            "fiat": fiat,
            "asset": asset,
            "side": side,
            "limit": limit,
        }
        if payment_method:
            payload["payment_method"] = payment_method

        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    async def get_prices(
        self,
        market: str,
        fiat: str,
        asset: str,
        payment_method: str | None = None,
    ) -> dict[str, Any]:
        """Get prices from mock server."""
        url = f"{self._base_url}/get_p2p_prices"

        params = {
            "market": market,
            "fiat": fiat,
            "asset": asset,
        }
        if payment_method:
            params["payment_method"] = payment_method

        response = await self._client.post(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_payment_methods(self, fiat: str) -> dict[str, Any]:
        """Get payment methods from mock server."""
        url = f"{self._base_url}/get_popular_p2p_payment_methods"

        response = await self._client.post(url, params={"fiat": fiat})
        response.raise_for_status()
        return response.json()

    async def get_assets(self) -> dict[str, Any]:
        """Get assets from mock server."""
        url = f"{self._base_url}/get_p2p_assets"

        response = await self._client.post(url)
        response.raise_for_status()
        return response.json()

    async def ping(self) -> bool:
        """Check if mock server is available."""
        try:
            url = f"{self._base_url}/ping"
            response = await self._client.get(url, timeout=5.0)
            data = response.json()
            return data.get("status") == 1
        except Exception:
            return False

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()
