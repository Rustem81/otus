from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from app.core.config import get_settings
from app.models.merchant import Merchant

settings = get_settings()


@dataclass
class ScoringResult:
    """Result of risk scoring calculation."""

    score: int  # 1-10
    category: str  # low, medium, high
    raw_score: float  # Before inversion


class ScoringStrategy(Protocol):
    """Protocol for scoring strategies."""

    def calculate(self, merchant: Merchant) -> ScoringResult:
        """Calculate risk score for merchant."""
        ...


class RuleBasedScoring:
    """
    Rule-based risk scoring implementation.

    Formula:
    raw = rating_norm * w1 + trades_norm * w2 + success_rate * w3 [+ speed_norm * w4]
    risk_score = 11 - round(raw * 10)  # inversion: good = low risk
    """

    def __init__(self) -> None:
        self._weights = {
            "rating": settings.SCORING_WEIGHT_RATING,
            "trades": settings.SCORING_WEIGHT_TRADES,
            "success_rate": settings.SCORING_WEIGHT_SUCCESS_RATE,
            "speed": settings.SCORING_WEIGHT_SPEED,
        }

    def calculate(self, merchant: Merchant) -> ScoringResult:
        """Calculate risk score based on merchant metrics."""
        # Normalize metrics
        rating_norm = self._normalize_rating(merchant.rating)
        trades_norm = self._normalize_trades(merchant.trades_count)
        success_norm = merchant.success_rate or 0.5  # Default to neutral if missing
        speed_norm = self._normalize_speed(merchant.closing_speed)

        # Check if speed is available
        has_speed = merchant.closing_speed is not None

        if has_speed:
            # Use all weights
            raw = (
                rating_norm * self._weights["rating"]
                + trades_norm * self._weights["trades"]
                + success_norm * self._weights["success_rate"]
                + speed_norm * self._weights["speed"]
            )
        else:
            # Redistribute speed weight proportionally
            total_other = (
                self._weights["rating"]
                + self._weights["trades"]
                + self._weights["success_rate"]
            )
            scale = 1.0 / total_other

            raw = (
                rating_norm * self._weights["rating"] * scale
                + trades_norm * self._weights["trades"] * scale
                + success_norm * self._weights["success_rate"] * scale
            )

        # Invert: high raw = good merchant = low risk
        risk_score = max(1, min(10, 11 - round(raw * 10)))

        # Map to category
        category = self._score_to_category(risk_score)

        return ScoringResult(
            score=risk_score,
            category=category,
            raw_score=raw,
        )

    def _normalize_rating(self, rating: float | None) -> float:
        """Normalize rating (typically 0-5) to 0-1."""
        if rating is None:
            return 0.5  # Neutral default
        return min(max(rating / 5.0, 0.0), 1.0)

    def _normalize_trades(self, trades: int) -> float:
        """Normalize trade count using log scale."""
        # Normalize: log1p(trades) / log1p(10000)
        return min(math.log1p(trades) / math.log1p(10000), 1.0)

    def _normalize_speed(self, speed: float | None) -> float:
        """Normalize closing speed (lower is better)."""
        if speed is None:
            return 0.5
        # Invert: faster (lower seconds) = higher score
        # Cap at 1 hour (3600 seconds)
        return max(0.0, 1.0 - min(speed / 3600.0, 1.0))

    def _score_to_category(self, score: int) -> str:
        """Map score to risk category."""
        if score <= 3:
            return "low"
        elif score <= 7:
            return "medium"
        else:
            return "high"
