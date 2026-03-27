from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class P2PDataSource(ABC):
    """
    Abstract interface for P2P data sources.

    Implementations: P2PArmyClient, MockP2PClient
    """

    @abstractmethod
    async def get_order_book(
        self,
        market: str,
        fiat: str,
        asset: str,
        side: str,
        payment_method: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Get P2P order book (advertisements).

        Args:
            market: Exchange name (mexc, binance, etc.)
            fiat: Fiat currency (RUB, USD, etc.)
            asset: Crypto asset (USDT, BTC, etc.)
            side: BUY or SELL
            payment_method: Filter by payment method
            limit: Max number of ads to return

        Returns:
            Raw API response dict
        """
        pass

    @abstractmethod
    async def get_prices(
        self,
        market: str,
        fiat: str,
        asset: str,
        payment_method: str | None = None,
    ) -> dict[str, Any]:
        """Get current P2P prices and spreads."""
        pass

    @abstractmethod
    async def get_payment_methods(self, fiat: str) -> dict[str, Any]:
        """Get list of popular payment methods."""
        pass

    @abstractmethod
    async def get_assets(self) -> dict[str, Any]:
        """Get list of available crypto assets."""
        pass

    @abstractmethod
    async def ping(self) -> bool:
        """Check if data source is available."""
        pass
