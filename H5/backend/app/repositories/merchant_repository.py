from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant import Merchant
from app.repositories.base_repository import BaseRepository


class MerchantRepository(BaseRepository[Merchant]):
    """Repository for Merchant entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Merchant, session)

    async def get_by_external_id(self, external_id: str) -> Merchant | None:
        """Get merchant by external ID (from P2P source)."""
        stmt = select(Merchant).where(Merchant.external_id == external_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        external_id: str,
        name: str,
        trades_count: int,
        success_rate: float | None,
        is_verified: bool,
        rating: float | None = None,
        closing_speed: float | None = None,
    ) -> Merchant:
        """
        Create or update merchant.

        Returns existing merchant if external_id found, otherwise creates new.
        """
        merchant = await self.get_by_external_id(external_id)

        if merchant:
            # Update existing
            return await self.update(
                merchant,
                name=name,
                trades_count=trades_count,
                success_rate=success_rate,
                is_verified=is_verified,
                rating=rating,
                closing_speed=closing_speed,
            )

        # Create new
        return await self.create(
            external_id=external_id,
            name=name,
            trades_count=trades_count,
            success_rate=success_rate,
            is_verified=is_verified,
            rating=rating,
            closing_speed=closing_speed,
        )
