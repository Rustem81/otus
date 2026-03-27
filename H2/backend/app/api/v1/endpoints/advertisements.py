from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, require_user
from app.core.database import get_db
from app.core.redis import get_redis
from redis.asyncio import Redis
from app.models.advertisement import Direction
from app.models.user import User
from app.schemas.p2p import (
    AdvertisementFilters,
    AdvertisementListResponse,
    AdvertisementResponse,
)
from app.services.profitability import ProfitabilityService
from app.services.reference_price import ReferencePriceCalculator
from app.services.scoring.facade import ScoringFacade

router = APIRouter()


def _direction_to_str(value: Direction | str) -> str:
    """Normalize direction to string for API response."""
    return value.value if isinstance(value, Direction) else value


async def get_advertisement_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> "AdvertisementService":
    """Factory dependency for AdvertisementService."""
    from app.repositories.advertisement_repository import AdvertisementRepository

    class AdvertisementService:
        def __init__(self, session: AsyncSession) -> None:
            self._repo = AdvertisementRepository(session)
            self._ref_calc = ReferencePriceCalculator(session)
            self._scoring = ScoringFacade(session)
            self._profit = ProfitabilityService()

    return AdvertisementService(db)


@router.get(
    "",
    response_model=AdvertisementListResponse,
    dependencies=[require_user],
)
async def list_advertisements(
    currency: str = Query(default="RUB", description="Currency pair"),
    direction: Direction | None = Query(default=None, description="BUY or SELL"),
    payment_methods: list[str] | None = Query(default=None, description="Filter by payment methods"),
    min_amount: float | None = Query(default=None, description="Minimum amount"),
    max_amount: float | None = Query(default=None, description="Maximum amount"),
    sort_by: str = Query(default="integral_score", description="Sort field"),
    sort_order: str = Query(default="desc", description="asc or desc"),
    limit: int = Query(default=200, le=500, description="Max results"),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    redis: Annotated[Redis, Depends(get_redis)] = None,
) -> AdvertisementListResponse:
    """
    List advertisements with filtering and sorting.
    """
    from app.repositories.advertisement_repository import AdvertisementRepository
    from app.services.reference_price import ReferencePriceCalculator
    from app.services.scoring.facade import ScoringFacade
    from app.services.profitability import ProfitabilityService

    ad_repo = AdvertisementRepository(db)
    ref_calc = ReferencePriceCalculator(db)
    scoring = ScoringFacade(db, redis)
    profit_calc = ProfitabilityService()

    # Get user's profile for commission calculation
    from app.repositories.profile_repository import TraderProfileRepository
    profile_repo = TraderProfileRepository(db)
    profile = await profile_repo.get_by_user_id(current_user.id)

    # Get advertisements
    ads = await ad_repo.get_active_with_filters(
        currency=currency,
        direction=direction,
        payment_methods=payment_methods,
        min_amount=min_amount,
        max_amount=max_amount,
        limit=limit,
    )

    # Get reference price
    ref_price = None
    if direction:
        ref_price = await ref_calc.calculate_reference_price(currency, direction)

    # Build response items
    items = []
    for ad in ads:
        # Calculate risk score if not set
        if ad.risk_score is None and ad.merchant:
            risk_result = await scoring.calculate_risk_score(ad.merchant)
            ad.risk_score = risk_result.score
            ad.risk_category = risk_result.category

        # Calculate spread
        spread = None
        if ref_price:
            from decimal import Decimal
            spread = float((Decimal(str(ad.price)) - ref_price) / ref_price * 100)

        # Calculate net yield
        commission_pct = profile.commission_percent if profile else None
        commission_fixed = profile.commission_fixed if profile else None
        net_yield = profit_calc.calculate_net_yield(
            ad_price=float(ad.price),
            ref_price=float(ref_price) if ref_price else None,
            commission_pct=commission_pct,
            commission_fixed=commission_fixed,
        )

        items.append(AdvertisementResponse(
            id=ad.id,
            external_id=ad.external_id,
            price=float(ad.price),
            volume=float(ad.volume),
            min_limit=float(ad.min_limit),
            max_limit=float(ad.max_limit),
            direction=_direction_to_str(ad.direction),
            currency=ad.currency,
            payment_methods=ad.payment_methods,
            is_active=ad.is_active,
            fetched_at=ad.fetched_at,
            risk_score=ad.risk_score,
            risk_category=ad.risk_category,
            net_yield=net_yield,
            spread=spread,
            merchant={
                "id": ad.merchant.id,
                "external_id": ad.merchant.external_id,
                "name": ad.merchant.name,
                "rating": ad.merchant.rating,
                "trades_count": ad.merchant.trades_count,
                "success_rate": ad.merchant.success_rate,
                "is_verified": ad.merchant.is_verified,
            } if ad.merchant else None,
        ))

    # Sort items
    reverse = sort_order.lower() == "desc"
    if sort_by == "price":
        items.sort(key=lambda x: x.price, reverse=reverse)
    elif sort_by == "risk_score":
        items.sort(key=lambda x: (x.risk_score or 999), reverse=reverse)
    elif sort_by == "net_yield":
        items.sort(key=lambda x: (x.net_yield or 0), reverse=reverse)
    # Default: integral_score (would need more complex calculation)

    return AdvertisementListResponse(
        items=items,
        total=len(items),
        reference_price=float(ref_price) if ref_price else None,
        last_updated=ads[0].fetched_at if ads else None,
    )


@router.get(
    "/{ad_id}",
    response_model=AdvertisementResponse,
    dependencies=[require_user],
)
async def get_advertisement(
    ad_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> AdvertisementResponse:
    """
    Get single advertisement details.
    """
    from app.repositories.advertisement_repository import AdvertisementRepository
    from fastapi import HTTPException

    ad_repo = AdvertisementRepository(db)
    ad = await ad_repo.get_by_id(ad_id)

    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    return AdvertisementResponse(
        id=ad.id,
        external_id=ad.external_id,
        price=float(ad.price),
        volume=float(ad.volume),
        min_limit=float(ad.min_limit),
        max_limit=float(ad.max_limit),
        direction=_direction_to_str(ad.direction),
        currency=ad.currency,
        payment_methods=ad.payment_methods,
        is_active=ad.is_active,
        fetched_at=ad.fetched_at,
        risk_score=ad.risk_score,
        risk_category=ad.risk_category,
        merchant={
            "id": ad.merchant.id,
            "external_id": ad.merchant.external_id,
            "name": ad.merchant.name,
            "rating": ad.merchant.rating,
            "trades_count": ad.merchant.trades_count,
            "success_rate": ad.merchant.success_rate,
            "is_verified": ad.merchant.is_verified,
        } if ad.merchant else None,
    )
