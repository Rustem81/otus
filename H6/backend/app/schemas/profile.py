from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.models.trader_profile import RiskProfile


# =============================================================================
# Bank / Payment Method Schemas
# =============================================================================


class BankInfo(BaseModel):
    """Information about a payment method / bank."""

    id: str
    name: str
    category: str  # e.g., "bank", "sbp", "wallet"


class BanksListResponse(BaseModel):
    """Response with list of available banks."""

    banks: list[BankInfo]


# =============================================================================
# Trader Profile Schemas
# =============================================================================


class TraderProfileBase(BaseModel):
    """Base schema for trader profile."""

    payment_methods: list[str] = Field(default_factory=list)
    min_amount: float | None = None
    max_amount: float | None = None
    currency_pair: str = "RUB_USDT"
    risk_profile: RiskProfile = RiskProfile.MEDIUM
    commission_percent: float | None = None
    commission_fixed: float | None = None
    kyc_level: str | None = None
    country: str | None = "RU"
    kyc_limit_warning: float | None = None

    @field_validator("max_amount")
    @classmethod
    def validate_amount_range(cls, max_amount: float | None, info) -> float | None:
        """Ensure max_amount >= min_amount if both are set."""
        if max_amount is not None:
            min_amount = info.data.get("min_amount")
            if min_amount is not None and max_amount < min_amount:
                raise ValueError("max_amount must be greater than or equal to min_amount")
        return max_amount


class TraderProfileCreate(TraderProfileBase):
    """Schema for creating trader profile."""

    pass


class TraderProfileUpdate(BaseModel):
    """Schema for updating trader profile (all fields optional)."""

    payment_methods: list[str] | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    currency_pair: str | None = None
    risk_profile: RiskProfile | None = None
    commission_percent: float | None = None
    commission_fixed: float | None = None
    kyc_level: str | None = None
    country: str | None = None
    kyc_limit_warning: float | None = None

    @field_validator("max_amount")
    @classmethod
    def validate_amount_range(cls, max_amount: float | None, info) -> float | None:
        """Ensure max_amount >= min_amount if both are set."""
        if max_amount is not None:
            min_amount = info.data.get("min_amount")
            if min_amount is not None and max_amount < min_amount:
                raise ValueError("max_amount must be greater than or equal to min_amount")
        return max_amount


class TraderProfileResponse(TraderProfileBase):
    """Response schema for trader profile."""

    id: int
    user_id: str

    model_config = {"from_attributes": True}


# =============================================================================
# Saved Filters Schemas
# =============================================================================


class AdvertisementFilters(BaseModel):
    """Filter criteria for advertisements."""

    payment_methods: list[str] | None = None
    min_rating: float | None = Field(None, ge=0, le=5)
    min_trades: int | None = Field(None, ge=0)
    min_amount: float | None = None
    max_amount: float | None = None


class SavedFiltersResponse(BaseModel):
    """Response schema for saved filters."""

    filters: AdvertisementFilters

    model_config = {"from_attributes": True}


class SavedFiltersUpdate(BaseModel):
    """Schema for updating saved filters."""

    filters: AdvertisementFilters


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str


# =============================================================================
# Onboarding Schemas
# =============================================================================


class OnboardingRequest(BaseModel):
    """Request schema for completing onboarding."""

    payment_methods: list[str] = Field(default_factory=list)
    min_amount: float | None = None
    max_amount: float | None = None
    risk_profile: RiskProfile = RiskProfile.MEDIUM
    commission_percent: float | None = None
    commission_fixed: float | None = None
