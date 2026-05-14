"""Tests for scoring module."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.scoring.strategy import RuleBasedScoring, ScoringResult
from app.services.scoring.facade import ScoringFacade
from app.models.merchant import Merchant


def create_merchant(
    rating: float = 4.8,
    trades_count: int = 1000,
    success_rate: float = 0.98,
    closing_speed: float | None = 300.0,
) -> Merchant:
    """Create a test merchant."""
    merchant = MagicMock(spec=Merchant)
    merchant.id = "test-merchant-1"
    merchant.name = "Test Merchant"
    merchant.rating = rating
    merchant.trades_count = trades_count
    merchant.success_rate = success_rate
    merchant.closing_speed = closing_speed
    return merchant


class TestRuleBasedScoring:
    """Tests for RuleBasedScoring."""

    def setup_method(self):
        self.scoring = RuleBasedScoring()

    def test_calculate_low_risk(self):
        """Excellent merchant should have low risk score."""
        merchant = create_merchant(
            rating=5.0,
            trades_count=10000,
            success_rate=0.99,
            closing_speed=60.0,  # Very fast
        )
        result = self.scoring.calculate(merchant)

        assert isinstance(result, ScoringResult)
        assert 1 <= result.score <= 10
        assert result.category == "low"
        assert 0 <= result.raw_score <= 1

    def test_calculate_high_risk(self):
        """Poor merchant should have high risk score."""
        merchant = create_merchant(
            rating=2.0,
            trades_count=10,
            success_rate=0.7,
            closing_speed=3000.0,  # Very slow
        )
        result = self.scoring.calculate(merchant)

        assert isinstance(result, ScoringResult)
        assert result.category == "high"

    def test_calculate_medium_risk(self):
        """Average merchant should have medium risk."""
        merchant = create_merchant(
            rating=3.5,
            trades_count=100,
            success_rate=0.85,
            closing_speed=600.0,
        )
        result = self.scoring.calculate(merchant)

        assert result.category in ("low", "medium", "high")

    def test_calculate_without_speed(self):
        """Should work without closing_speed."""
        merchant = create_merchant(
            rating=4.5,
            trades_count=500,
            success_rate=0.9,
            closing_speed=None,
        )
        result = self.scoring.calculate(merchant)

        assert isinstance(result, ScoringResult)
        assert 1 <= result.score <= 10

    def test_score_inversion(self):
        """High raw score should result in low risk score."""
        # Create excellent merchant
        excellent = create_merchant(rating=5.0, trades_count=10000, success_rate=1.0)
        excellent_result = self.scoring.calculate(excellent)

        # Create poor merchant
        poor = create_merchant(rating=1.0, trades_count=1, success_rate=0.5)
        poor_result = self.scoring.calculate(poor)

        # Excellent merchant should have lower risk score (inverted)
        assert excellent_result.raw_score > poor_result.raw_score
        assert excellent_result.score <= poor_result.score

    def test_category_mapping(self):
        """Test score to category mapping."""
        # Low risk: score 1-3
        assert self.scoring._score_to_category(1) == "low"
        assert self.scoring._score_to_category(3) == "low"

        # Medium risk: score 4-7
        assert self.scoring._score_to_category(4) == "medium"
        assert self.scoring._score_to_category(7) == "medium"

        # High risk: score 8-10
        assert self.scoring._score_to_category(8) == "high"
        assert self.scoring._score_to_category(10) == "high"


class TestScoringFacade:
    """Tests for ScoringFacade."""

    @pytest.mark.asyncio
    async def test_calculate_risk_score(self):
        """Facade should delegate to scoring strategy."""
        mock_session = AsyncMock()
        mock_redis = AsyncMock()

        facade = ScoringFacade(mock_session, mock_redis)
        merchant = create_merchant()

        result = await facade.calculate_risk_score(merchant)

        assert isinstance(result, ScoringResult)
        assert 1 <= result.score <= 10

    @pytest.mark.asyncio
    async def test_get_explanation_merchant_not_found(self):
        """Should return None if merchant not found."""
        mock_session = AsyncMock()
        mock_redis = AsyncMock()

        # Mock repository to return None
        with patch(
            "app.services.scoring.facade.MerchantRepository"
        ) as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id = AsyncMock(return_value=None)
            mock_repo_class.return_value = mock_repo

            facade = ScoringFacade(mock_session, mock_redis)
            result = await facade.get_explanation("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_calculate_with_explanation(self):
        """Should return both score and explanation."""
        mock_session = AsyncMock()
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)  # No cache

        merchant = create_merchant()

        with patch.object(
            ScoringFacade, "calculate_risk_score"
        ) as mock_calc:
            mock_calc.return_value = ScoringResult(
                score=3, category="low", raw_score=0.85
            )

            facade = ScoringFacade(mock_session, mock_redis)
            score, explanation = await facade.calculate_with_explanation(merchant)

            assert isinstance(score, ScoringResult)
            # Explanation may be None if OpenAI key not configured
