from __future__ import annotations

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant import Merchant
from app.repositories.merchant_repository import MerchantRepository
from app.services.scoring.llm_explainer import LLMExplainer
from app.services.scoring.strategy import RuleBasedScoring, ScoringResult


class ScoringFacade:
    """
    Facade for risk scoring operations.

    Combines:
    - Rule-based scoring calculation
    - LLM explanations (cached)
    """

    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self._session = session
        self._redis = redis
        self._scoring = RuleBasedScoring()
        self._explainer = LLMExplainer(redis)

    async def calculate_risk_score(self, merchant: Merchant) -> ScoringResult:
        """Calculate risk score for merchant."""
        return self._scoring.calculate(merchant)

    async def get_explanation(self, merchant_id: str) -> str | None:
        """
        Get LLM explanation for merchant.

        Returns cached explanation or generates new one.
        """
        # Get merchant from DB
        repo = MerchantRepository(self._session)
        merchant = await repo.get_by_id(merchant_id)
        if not merchant:
            return None

        # Calculate score first
        scoring_result = self._scoring.calculate(merchant)

        # Get explanation from LLM
        return await self._explainer.explain(merchant, scoring_result)

    async def calculate_with_explanation(
        self, merchant: Merchant
    ) -> tuple[ScoringResult, str | None]:
        """Calculate score and get explanation."""
        score = await self.calculate_risk_score(merchant)
        explanation = await self._explainer.explain(merchant, score)
        return score, explanation
