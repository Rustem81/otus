from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.advertisement import Advertisement, Direction
from app.repositories.base_repository import BaseRepository


class AdvertisementRepository(BaseRepository[Advertisement]):
    """Repository for Advertisement entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Advertisement, session)

    async def get_by_id(self, entity_id: str) -> Advertisement | None:
        """Get advertisement by ID with merchant relation preloaded."""
        stmt = (
            select(Advertisement)
            .options(selectinload(Advertisement.merchant))
            .where(Advertisement.id == entity_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> Advertisement | None:
        """Get advertisement by external ID (from P2P source)."""
        stmt = (
            select(Advertisement)
            .options(selectinload(Advertisement.merchant))
            .where(Advertisement.external_id == external_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_pair(
        self,
        currency: str,
        direction: Direction,
        limit: int = 200,
    ) -> list[Advertisement]:
        """Get active advertisements by currency pair."""
        stmt = (
            select(Advertisement)
            .options(selectinload(Advertisement.merchant))
            .where(
                Advertisement.currency == currency,
                Advertisement.direction == direction,
                Advertisement.is_active == True,
            )
            .order_by(Advertisement.price)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_with_filters(
        self,
        currency: str,
        direction: Direction | None = None,
        payment_methods: list[str] | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        limit: int = 200,
    ) -> list[Advertisement]:
        """Get active advertisements with filters."""
        stmt = select(Advertisement).where(
            Advertisement.currency == currency,
            Advertisement.is_active == True,
        )
        stmt = stmt.options(selectinload(Advertisement.merchant))

        if direction:
            stmt = stmt.where(Advertisement.direction == direction)

        if payment_methods:
            # Check if any payment method overlaps
            stmt = stmt.where(
                Advertisement.payment_methods.overlap(payment_methods)
            )

        if min_amount is not None:
            stmt = stmt.where(Advertisement.max_limit >= min_amount)

        if max_amount is not None:
            stmt = stmt.where(Advertisement.min_limit <= max_amount)

        stmt = stmt.order_by(Advertisement.price).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def mark_inactive_by_ttl(self, ttl_seconds: int) -> int:
        """
        Mark advertisements as inactive if not updated within TTL.

        Returns number of marked advertisements.
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=ttl_seconds)

        stmt = (
            update(Advertisement)
            .where(
                Advertisement.is_active == True,
                Advertisement.fetched_at < cutoff_time,
            )
            .values(is_active=False)
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    async def upsert(
        self,
        external_id: str,
        merchant_id: str,
        price: float,
        volume: float,
        min_limit: float,
        max_limit: float,
        direction: Direction,
        currency: str,
        payment_methods: list[str],
        description: str | None = None,
    ) -> Advertisement:
        """
        Create or update advertisement.

        Returns existing advertisement if external_id found, otherwise creates new.
        """
        ad = await self.get_by_external_id(external_id)

        if ad:
            # Update existing
            return await self.update(
                ad,
                price=price,
                volume=volume,
                min_limit=min_limit,
                max_limit=max_limit,
                payment_methods=payment_methods,
                is_active=True,
                fetched_at=datetime.now(timezone.utc),
                description=description,
            )

        # Create new
        return await self.create(
            external_id=external_id,
            merchant_id=merchant_id,
            price=price,
            volume=volume,
            min_limit=min_limit,
            max_limit=max_limit,
            direction=direction,
            currency=currency,
            payment_methods=payment_methods,
            description=description,
            is_active=True,
        )

    async def get_top_by_price(
        self,
        currency: str,
        direction: Direction,
        limit: int = 10,
    ) -> list[Advertisement]:
        """Get top N advertisements by price for reference price calculation."""
        stmt = (
            select(Advertisement)
            .options(selectinload(Advertisement.merchant))
            .where(
                Advertisement.currency == currency,
                Advertisement.direction == direction,
                Advertisement.is_active == True,
            )
        )

        if direction == Direction.BUY:
            stmt = stmt.order_by(Advertisement.price.asc())
        else:
            stmt = stmt.order_by(Advertisement.price.desc())

        stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
