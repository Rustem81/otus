"""LLM-based risk explanation service with caching."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from openai import AsyncOpenAI
from redis.asyncio import Redis

from app.core.config import get_settings
from app.services.scoring.strategy import ScoringResult

if TYPE_CHECKING:
    from app.models.merchant import Merchant

settings = get_settings()

# Cache TTL in seconds (10 minutes)
CACHE_TTL = 600

# Prompt template for risk explanation
RISK_EXPLANATION_PROMPT = """Ты — аналитик P2P-трейдинга. Объясни риск-скор мерчанта кратко (до 300 символов).

Данные мерчанта:
- Рейтинг: {rating}/5
- Сделок: {trades_count}
- Успешных: {success_rate:.1%}
- Скорость: {speed}
- Риск-скор: {risk_score}/10 ({risk_category})

Объясни почему такой риск."""


class LLMExplainer:
    """Service for generating LLM-based risk explanations with caching."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis
        self._client: AsyncOpenAI | None = None
        if settings.OPENAI_API_KEY:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _get_cache_key(self, merchant_id: str, risk_score: int) -> str:
        """Generate cache key for merchant explanation."""
        return f"llm:explain:{merchant_id}:{risk_score}"

    async def _get_cached(self, cache_key: str) -> str | None:
        """Get cached explanation from Redis."""
        cached = await self._redis.get(cache_key)
        if cached:
            return cached.decode("utf-8")
        return None

    async def _set_cached(self, cache_key: str, explanation: str) -> None:
        """Cache explanation in Redis with TTL."""
        await self._redis.setex(cache_key, CACHE_TTL, explanation)

    def _build_prompt(self, merchant: "Merchant", scoring_result: ScoringResult) -> str:
        """Build prompt for OpenAI."""
        speed_text = merchant.avg_payment_time or "неизвестна"
        if isinstance(speed_text, (int, float)):
            speed_text = f"{speed_text:.1f} мин"

        return RISK_EXPLANATION_PROMPT.format(
            rating=merchant.rating or 0,
            trades_count=merchant.trades_count or 0,
            success_rate=merchant.success_rate or 0,
            speed=speed_text,
            risk_score=scoring_result.risk_score,
            risk_category=scoring_result.risk_category,
        )

    async def explain(
        self,
        merchant: "Merchant",
        scoring_result: ScoringResult,
    ) -> str | None:
        """
        Generate LLM explanation for merchant risk score.

        Returns cached result if available. Falls back to None on LLM errors.
        """
        # Check if LLM is configured
        if not self._client:
            return None

        cache_key = self._get_cache_key(str(merchant.id), scoring_result.risk_score)

        # Try cache first
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        try:
            prompt = self._build_prompt(merchant, scoring_result)

            response = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты — аналитик P2P-трейдинга. Отвечай кратко, по существу.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            explanation = response.choices[0].message.content
            if explanation:
                # Clean up and truncate
                explanation = explanation.strip()
                if len(explanation) > 300:
                    explanation = explanation[:297] + "..."

                # Cache the result
                await self._set_cached(cache_key, explanation)
                return explanation

        except Exception:
            # Graceful degradation: return None on any LLM error
            pass

        return None
