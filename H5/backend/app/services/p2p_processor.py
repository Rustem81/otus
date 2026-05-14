from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.advertisement import Advertisement, Direction
from app.models.merchant import Merchant
from app.repositories.advertisement_repository import AdvertisementRepository
from app.repositories.merchant_repository import MerchantRepository
from app.schemas.p2p import P2PAdvertisementRaw

logger = logging.getLogger(__name__)


class P2PDataProcessor:
    """
    Process raw P2P data and persist to database.

    Handles:
    - Merchant upsert (create or update)
    - Advertisement upsert (create or update)
    - Field mapping from raw API to internal models
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._merchant_repo = MerchantRepository(session)
        self._ad_repo = AdvertisementRepository(session)

    async def process_advertisements(
        self,
        raw_ads: list[dict[str, Any]],
        currency: str,
        direction: Direction,
    ) -> tuple[int, int]:
        """
        Process list of raw advertisements.

        Args:
            raw_ads: List of raw ad data from P2P source
            currency: Currency pair (e.g., RUB)
            direction: BUY or SELL

        Returns:
            Tuple of (processed_count, error_count)
        """
        processed = 0
        errors = 0

        for raw_ad in raw_ads:
            try:
                await self._process_single_ad(raw_ad, currency, direction)
                processed += 1
            except Exception as e:
                logger.error(f"Error processing ad {raw_ad.get('adv_id')}: {e}")
                errors += 1

        return processed, errors

    async def _process_single_ad(
        self,
        raw_ad: dict[str, Any],
        currency: str,
        direction: Direction,
    ) -> Advertisement:
        """Process single advertisement."""
        # Parse raw data
        ad_data = P2PAdvertisementRaw.model_validate(raw_ad)

        # Upsert merchant first
        merchant = await self._upsert_merchant(ad_data)

        # Upsert advertisement
        advertisement = await self._upsert_advertisement(
            ad_data, merchant.id, currency, direction
        )

        return advertisement

    async def _upsert_merchant(self, ad_data: P2PAdvertisementRaw) -> Merchant:
        """Create or update merchant from ad data."""
        # Map success rate from percentage (0-100) to decimal (0-1)
        success_rate = ad_data.user_rate / 100.0 if ad_data.user_rate else None

        return await self._merchant_repo.upsert(
            external_id=ad_data.user_id,
            name=ad_data.user_name,
            trades_count=ad_data.user_orders,
            success_rate=success_rate,
            is_verified=bool(ad_data.is_merchant),
            rating=None,  # Not provided by p2p.army
            closing_speed=None,  # Not provided by p2p.army
        )

    async def _upsert_advertisement(
        self,
        ad_data: P2PAdvertisementRaw,
        merchant_id: str,
        currency: str,
        direction: Direction,
    ) -> Advertisement:
        """Create or update advertisement."""
        return await self._ad_repo.upsert(
            external_id=ad_data.adv_id,
            merchant_id=merchant_id,
            price=float(ad_data.price),
            volume=float(ad_data.surplus_amount),
            min_limit=float(ad_data.min_fiat),
            max_limit=float(ad_data.max_fiat),
            direction=direction,
            currency=currency,
            payment_methods=ad_data.payment_methods,
            description=ad_data.text,
        )

    async def mark_stale_ads(self, ttl_seconds: int) -> int:
        """Mark advertisements as inactive if not updated within TTL."""
        return await self._ad_repo.mark_inactive_by_ttl(ttl_seconds)
