from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, require_user
from app.core.database import get_db
from app.core.redis import get_redis
from app.models.user import User
from app.schemas.scoring import RiskExplanationResponse
from app.services.scoring.facade import ScoringFacade

router = APIRouter()


async def get_scoring_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> ScoringFacade:
    """Factory dependency for ScoringFacade."""
    return ScoringFacade(db, redis)


@router.get(
    "/{merchant_id}/explain",
    response_model=RiskExplanationResponse,
    dependencies=[require_user],
)
async def get_risk_explanation(
    merchant_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    scoring_service: Annotated[ScoringFacade, Depends(get_scoring_service)] = None,
) -> RiskExplanationResponse:
    """
    Get risk score explanation for a merchant.

    Returns cached LLM explanation if available.
    """
    from app.repositories.merchant_repository import MerchantRepository

    merchant_repo = MerchantRepository(scoring_service._session)
    merchant = await merchant_repo.get_by_id(merchant_id)

    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # Calculate score
    score_result = await scoring_service.calculate_risk_score(merchant)

    # Get explanation (may be None for MVP)
    explanation = await scoring_service.get_explanation(merchant_id)

    return RiskExplanationResponse(
        merchant_id=merchant_id,
        merchant_name=merchant.name,
        risk_score=score_result.score,
        risk_category=score_result.category,
        explanation=explanation or "Текстовое объяснение временно недоступно",
    )
