from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings
from app.services.p2p_source.interface import P2PDataSource

settings = get_settings()


class P2PArmyClient(P2PDataSource):
    """
    Client for p2p.army API (production).

    Requires API key in X-APIKEY header.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self._api_key = api_key or settings.P2P_ARMY_API_KEY
        self._base_url = base_url or settings.P2P_ARMY_BASE_URL
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={"X-APIKEY": self._api_key},
        )

    async def get_order_book(
        self,
        market: str,
        fiat: str,
        asset: str,
        side: str,
        payment_method: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Get order book from p2p.army."""
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
        """Get prices from p2p.army."""
        url = f"{self._base_url}/get_p2p_prices"

        payload = {
            "market": market,
            "fiat": fiat,
            "asset": asset,
        }
        if payment_method:
            payload["payment_method"] = payment_method

        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    async def get_payment_methods(self, fiat: str) -> dict[str, Any]:
        """Get payment methods from p2p.army."""
        url = f"{self._base_url}/get_popular_p2p_payment_methods"

        payload = {"fiat": fiat}
        response = await self._client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    async def get_assets(self) -> dict[str, Any]:
        """Get assets from p2p.army."""
        url = f"{self._base_url}/get_p2p_assets"

        response = await self._client.post(url)
        response.raise_for_status()
        return response.json()

    async def ping(self) -> bool:
        """Check if p2p.army is available."""
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
