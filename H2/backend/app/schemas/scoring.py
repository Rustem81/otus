from __future__ import annotations

from pydantic import BaseModel


class RiskExplanationResponse(BaseModel):
    """Response schema for risk score explanation."""

    merchant_id: str
    merchant_name: str
    risk_score: int
    risk_category: str
    explanation: str


class IntegralScoreRequest(BaseModel):
    """Request for integral score calculation."""

    price_weight: float = 0.4
    risk_weight: float = 0.3
    profile_weight: float = 0.3
