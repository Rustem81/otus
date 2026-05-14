"""Repository for merchant blacklist operations."""
from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant_blacklist import MerchantBlacklist


class BlacklistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_blacklisted_merchant_ids(self, user_id: str) -> list[str]:
        """Get list of merchant IDs blacklisted by user."""
        stmt = select(MerchantBlacklist.merchant_id).where(
            MerchantBlacklist.user_id == user_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, user_id: str, merchant_id: str) -> MerchantBlacklist:
        """Add merchant to blacklist."""
        entry = MerchantBlacklist(user_id=user_id, merchant_id=merchant_id)
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def remove(self, user_id: str, merchant_id: str) -> bool:
        """Remove merchant from blacklist. Returns True if deleted."""
        stmt = delete(MerchantBlacklist).where(
            MerchantBlacklist.user_id == user_id,
            MerchantBlacklist.merchant_id == merchant_id,
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def get_all(self, user_id: str) -> list[MerchantBlacklist]:
        """Get all blacklist entries for user."""
        stmt = (
            select(MerchantBlacklist)
            .where(MerchantBlacklist.user_id == user_id)
            .order_by(MerchantBlacklist.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
