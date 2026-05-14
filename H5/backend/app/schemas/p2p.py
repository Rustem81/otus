from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# =============================================================================
# Raw P2P Data Schemas (from p2p.army API)
# =============================================================================


class P2PAdvertisementRaw(BaseModel):
    """Raw advertisement data from P2P source."""

    pos: int
    updated_at: int
    market: str
    asset: str
    fiat: str
    side: str  # BUY or SELL
    payment_methods: list[str]
    price: str
    surplus_amount: str
    surplus_fiat: float
    min_fiat: str
    max_fiat: str
    text: str
    user_name: str
    user_id: str
    adv_id: str
    user_orders: int
    user_rate: int
    is_merchant: int


class P2POrderBookResponse(BaseModel):
    """Response from get_p2p_order_book endpoint."""

    status: int
    ads: list[P2PAdvertisementRaw]


# =============================================================================
# Internal Advertisement Schemas
# =============================================================================


class MerchantResponse(BaseModel):
    """Merchant information in advertisement."""

    id: str
    external_id: str
    name: str
    rating: float | None = None
    trades_count: int
    success_rate: float
    is_verified: bool

    model_config = {"from_attributes": True}


class AdvertisementResponse(BaseModel):
    """Advertisement response schema."""

    id: str
    external_id: str
    price: float
    volume: float
    min_limit: float
    max_limit: float
    direction: str  # BUY or SELL
    currency: str
    payment_methods: list[str]
    is_active: bool
    fetched_at: datetime
    risk_score: int | None = None
    risk_category: str | None = None
    net_yield: float | None = None
    spread: float | None = None
    merchant: MerchantResponse

    model_config = {"from_attributes": True}


class AdvertisementListResponse(BaseModel):
    """List of advertisements with metadata."""

    items: list[AdvertisementResponse]
    total: int
    reference_price: float | None = None
    last_updated: datetime | None = None


# =============================================================================
# Filter Schemas
# =============================================================================


class AdvertisementFilters(BaseModel):
    """Filters for advertisement query."""

    payment_methods: list[str] | None = None
    min_rating: float | None = Field(None, ge=0, le=5)
    min_trades: int | None = Field(None, ge=0)
    min_amount: float | None = None
    max_amount: float | None = None
    direction: str | None = None  # BUY or SELL


# =============================================================================
# Sorting Schemas
# =============================================================================


class AdvertisementSort(BaseModel):
    """Sorting parameters for advertisements."""

    field: str = "integral_score"  # price, rating, volume, risk_score, net_yield, integral_score
    order: str = "desc"  # asc or desc
