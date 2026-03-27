from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_filters import SavedFilters
from app.models.trader_profile import RiskProfile, TraderProfile
from app.repositories.base_repository import BaseRepository


class TraderProfileRepository(BaseRepository[TraderProfile]):
    """Repository for TraderProfile entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TraderProfile, session)

    async def get_by_user_id(self, user_id: str) -> TraderProfile | None:
        """Get trader profile by user ID."""
        stmt = select(TraderProfile).where(TraderProfile.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: str) -> TraderProfile:
        """Get existing profile or create default one."""
        profile = await self.get_by_user_id(user_id)
        if profile:
            return profile

        # Create default profile
        return await self.create(
            user_id=user_id,
            payment_methods=[],
            min_amount=None,
            max_amount=None,
            currency_pair="RUB_USDT",
            risk_profile=RiskProfile.MEDIUM,
            commission_percent=None,
            commission_fixed=None,
        )

    async def update_by_user_id(
        self, user_id: str, **kwargs
    ) -> TraderProfile | None:
        """Update profile by user ID."""
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return None

        return await self.update(profile, **kwargs)


class SavedFiltersRepository(BaseRepository[SavedFilters]):
    """Repository for SavedFilters entity."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SavedFilters, session)

    async def get_by_user_id(self, user_id: str) -> SavedFilters | None:
        """Get saved filters by user ID."""
        stmt = select(SavedFilters).where(SavedFilters.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: str) -> SavedFilters:
        """Get existing filters or create empty ones."""
        filters = await self.get_by_user_id(user_id)
        if filters:
            return filters

        return await self.create(user_id=user_id, filters_json={})

    async def update_by_user_id(
        self, user_id: str, filters_json: dict
    ) -> SavedFilters | None:
        """Update filters by user ID."""
        filters = await self.get_by_user_id(user_id)
        if not filters:
            return None

        return await self.update(filters, filters_json=filters_json)
