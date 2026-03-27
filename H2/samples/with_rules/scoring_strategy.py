"""Scoring service - generated WITH project steering rules and skills."""

# Промпт: тот же + активны steering-файлы + скиллы #fastapi-templates, #gof-design-patterns

from __future__ import annotations

import math
import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


# --- Schemas (Pydantic v2) ---

class RiskCategory(str, Enum):
    LOW = "low"        # 1-3
    MEDIUM = "medium"  # 4-7
    HIGH = "high"      # 8-10


class ScoringWeights(BaseModel):
    """Weights for risk score factors, loaded from config."""
    model_config = ConfigDict(frozen=True)

    rating: float = 0.3
    trades: float = 0.25
    success_rate: float = 0.3
    speed: float = 0.15


class MerchantMetrics(BaseModel):
    """Normalized merchant metrics from P2P source."""
    rating: float = Field(ge=0, le=5)
    trades_count: int = Field(ge=0)
    success_rate: float = Field(ge=0, le=1)
    closing_speed: float | None = None  # seconds, may be absent


class ScoringResult(BaseModel):
    """Result of risk scoring calculation."""
    score: int = Field(ge=1, le=10)
    category: RiskCategory
    explanation: str | None = None  # up to 300 chars, from LLM


# --- Strategy pattern (GoF) ---

class ScoringStrategy(ABC):
    """Interface for scoring algorithms (GoF: Strategy)."""

    @abstractmethod
    async def calculate(self, metrics: MerchantMetrics) -> ScoringResult:
        """Calculate risk score from merchant metrics."""
        ...


class RuleBasedScoring(ScoringStrategy):
    """Rule-based scoring using weighted factors from config.

    Higher merchant metrics → lower risk score (1 = safest, 10 = riskiest).
    When closing_speed is unavailable, its weight is redistributed proportionally.
    """

    MAX_TRADES_FOR_NORM = 10_000
    MAX_SPEED_FOR_NORM = 3_600  # 1 hour in seconds

    def __init__(self, weights: ScoringWeights) -> None:
        self._weights = weights

    async def calculate(self, metrics: MerchantMetrics) -> ScoringResult:
        factors = self._normalize_factors(metrics)
        active_weights = self._resolve_weights(metrics)

        raw_score = sum(factors[k] * active_weights[k] for k in factors)
        # Invert: high raw = reliable merchant = LOW risk
        risk_score = max(1, min(10, 11 - round(raw_score * 10)))
        category = self._categorize(risk_score)

        logger.debug(
            "Scoring merchant: factors=%s, weights=%s, raw=%.3f, risk=%d (%s)",
            factors, active_weights, raw_score, risk_score, category.value,
        )

        return ScoringResult(score=risk_score, category=category)

    def _normalize_factors(self, metrics: MerchantMetrics) -> dict[str, float]:
        """Normalize all factors to 0-1 range."""
        factors: dict[str, float] = {
            "rating": metrics.rating / 5.0,
            "trades": min(
                math.log1p(metrics.trades_count) / math.log1p(self.MAX_TRADES_FOR_NORM),
                1.0,
            ),
            "success_rate": metrics.success_rate,
        }
        if metrics.closing_speed is not None:
            factors["speed"] = 1.0 - min(
                metrics.closing_speed / self.MAX_SPEED_FOR_NORM, 1.0
            )
        return factors

    def _resolve_weights(self, metrics: MerchantMetrics) -> dict[str, float]:
        """Get active weights; redistribute speed weight if speed is absent."""
        weights: dict[str, float] = {
            "rating": self._weights.rating,
            "trades": self._weights.trades,
            "success_rate": self._weights.success_rate,
        }
        if metrics.closing_speed is not None:
            weights["speed"] = self._weights.speed
        else:
            # Redistribute speed weight proportionally
            total = sum(weights.values())
            if total > 0:
                weights = {k: v / total for k, v in weights.items()}

        return weights

    @staticmethod
    def _categorize(score: int) -> RiskCategory:
        if score <= 3:
            return RiskCategory.LOW
        if score <= 7:
            return RiskCategory.MEDIUM
        return RiskCategory.HIGH
