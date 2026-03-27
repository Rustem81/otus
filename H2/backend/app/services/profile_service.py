from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_filters import SavedFilters
from app.models.trader_profile import TraderProfile
from app.repositories.profile_repository import (
    SavedFiltersRepository,
    TraderProfileRepository,
)
from app.schemas.profile import (
    AdvertisementFilters,
    SavedFiltersResponse,
    SavedFiltersUpdate,
    TraderProfileResponse,
    TraderProfileUpdate,
)


# Predefined list of Russian banks and payment methods
AVAILABLE_BANKS = [
    {"id": "sbp", "name": "СБП (Система быстрых платежей)", "category": "sbp"},
    {"id": "sberbank", "name": "Сбербанк", "category": "bank"},
    {"id": "tinkoff", "name": "Тинькофф", "category": "bank"},
    {"id": "alfa", "name": "Альфа-Банк", "category": "bank"},
    {"id": "raiffeisen", "name": "Райффайзен", "category": "bank"},
    {"id": "vtb", "name": "ВТБ", "category": "bank"},
    {"id": "gazprombank", "name": "Газпромбанк", "category": "bank"},
    {"id": "otkritie", "name": "Открытие", "category": "bank"},
    {"id": "rosbank", "name": "Росбанк", "category": "bank"},
    {"id": "sovcombank", "name": "Совкомбанк", "category": "bank"},
    {"id": "psb", "name": "Промсвязьбанк", "category": "bank"},
    {"id": "mts_bank", "name": "МТС Банк", "category": "bank"},
    {"id": "home_credit", "name": "Хоум Кредит", "category": "bank"},
    {"id": "cash", "name": "Наличные", "category": "cash"},
]


class ProfileService:
    """Service for trader profile business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._profile_repo = TraderProfileRepository(session)
        self._filters_repo = SavedFiltersRepository(session)

    async def get_profile(self, user_id: str) -> TraderProfile:
        """Get or create trader profile for user."""
        return await self._profile_repo.get_or_create(user_id)

    async def update_profile(
        self, user_id: str, update_data: TraderProfileUpdate
    ) -> TraderProfile:
        """Update trader profile."""
        # Ensure profile exists
        profile = await self._profile_repo.get_or_create(user_id)

        # Filter out None values
        update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)

        if update_dict:
            profile = await self._profile_repo.update(profile, **update_dict)

        return profile

    async def get_available_banks(self) -> list[dict]:
        """Get list of available banks and payment methods."""
        return AVAILABLE_BANKS

    async def get_saved_filters(self, user_id: str) -> SavedFilters:
        """Get or create saved filters for user."""
        return await self._filters_repo.get_or_create(user_id)

    async def update_saved_filters(
        self, user_id: str, filters_data: SavedFiltersUpdate
    ) -> SavedFilters:
        """Update saved filters for user."""
        # Ensure filters exist
        filters = await self._filters_repo.get_or_create(user_id)

        # Convert to dict for JSONB storage
        filters_json = filters_data.filters.model_dump(exclude_none=True)

        return await self._filters_repo.update(filters, filters_json=filters_json)

    @staticmethod
    def profile_to_response(profile: TraderProfile) -> TraderProfileResponse:
        """Convert profile model to response schema."""
        return TraderProfileResponse.model_validate(profile)

    @staticmethod
    def filters_to_response(filters: SavedFilters) -> SavedFiltersResponse:
        """Convert filters model to response schema."""
        # Convert JSONB to AdvertisementFilters
        filters_data = filters.filters_json or {}
        return SavedFiltersResponse(
            filters=AdvertisementFilters.model_validate(filters_data)
        )
