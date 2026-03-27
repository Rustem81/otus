from __future__ import annotations

import logging
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.advertisement import Direction
from app.repositories.advertisement_repository import AdvertisementRepository

logger = logging.getLogger(__name__)


class ReferencePriceCalculator:
    """
    Calculate reference price (средневзвешенная цена по топ-10).

    Used as baseline for spread calculations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._ad_repo = AdvertisementRepository(session)

    async def calculate_reference_price(
        self,
        currency: str,
        direction: Direction,
        top_n: int = 10,
    ) -> Decimal | None:
        """
        Calculate volume-weighted average price of top N advertisements.

        Args:
            currency: Currency pair (e.g., RUB)
            direction: BUY or SELL
            top_n: Number of top ads to include

        Returns:
            Reference price or None if no ads available
        """
        ads = await self._ad_repo.get_top_by_price(currency, direction, top_n)

        if not ads:
            logger.warning(f"No ads found for {currency} {direction.value}")
            return None

        # Calculate volume-weighted average price
        total_volume = Decimal(0)
        weighted_sum = Decimal(0)

        for ad in ads:
            volume = Decimal(str(ad.volume))
            price = Decimal(str(ad.price))
            total_volume += volume
            weighted_sum += volume * price

        if total_volume == 0:
            return None

        reference_price = weighted_sum / total_volume
        logger.debug(f"Reference price for {currency} {direction.value}: {reference_price}")

        return reference_price.quantize(Decimal("0.01"))

    async def calculate_spread(
        self,
        ad_price: Decimal,
        currency: str,
        direction: Direction,
    ) -> Decimal | None:
        """
        Calculate spread between ad price and reference price.

        Returns:
            Spread in percentage points (e.g., 0.5 for 0.5%)
        """
        ref_price = await self.calculate_reference_price(currency, direction)
        if not ref_price or ref_price == 0:
            return None

        spread = ((ad_price - ref_price) / ref_price) * 100
        return spread.quantize(Decimal("0.01"))
