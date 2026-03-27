---
inclusion: fileMatch
fileMatchPattern: "backend/app/services/**,backend/app/repositories/**,frontend/src/composables/**"
---

# Применение GoF-паттернов в проекте

При работе с сервисами, репозиториями и composables используй скилл `#gof-design-patterns` для выбора оптимального паттерна.

## Карта паттернов проекта

| Паттерн | Где применяется | Зачем |
|---------|----------------|-------|
| **Repository** | `backend/app/repositories/` | Абстракция доступа к данным. `BaseRepository` → `AdvertisementRepository`, `MerchantRepository`, `UserRepository` |
| **Strategy** | `backend/app/services/scoring/` | Разные стратегии скоринга: `RuleBasedStrategy`, `LLMEnhancedStrategy`. Выбор через конфиг |
| **Factory Method** | `backend/app/services/` | Создание сервисов с зависимостями через FastAPI `Depends()` |
| **Observer** | `backend/app/tasks/` | При обновлении P2P-данных — уведомление scoring и cache сервисов |
| **Facade** | `backend/app/services/advertisement_facade.py` | Единый интерфейс для API: объединяет polling, scoring, profitability |
| **Template Method** | `backend/app/repositories/base.py` | Базовый CRUD flow в `BaseRepository`, конкретные репозитории переопределяют шаги |
| **Decorator** | `backend/app/api/dependencies.py` | Декораторы для auth, rate limiting, logging |
| **Singleton** | `backend/app/core/` | Конфигурация (`@lru_cache`), Redis-клиент, DB engine |

## Пример: Strategy для скоринга

```python
# backend/app/services/scoring/strategy.py
from abc import ABC, abstractmethod

class ScoringStrategy(ABC):
    """Интерфейс стратегии скоринга (GoF: Strategy)."""

    @abstractmethod
    async def calculate(self, metrics: MerchantMetrics) -> ScoringResult:
        ...

class RuleBasedScoring(ScoringStrategy):
    """Скоринг на основе правил и весов из конфига."""

    def __init__(self, weights: ScoringWeights):
        self._weights = weights

    async def calculate(self, metrics: MerchantMetrics) -> ScoringResult:
        score = (
            metrics.rating * self._weights.rating
            + metrics.trades_normalized * self._weights.trades
            + metrics.success_rate * self._weights.success_rate
        )
        if metrics.closing_speed is not None:
            score += metrics.closing_speed_normalized * self._weights.speed
        else:
            # Перераспределение весов пропорционально
            ...
        return ScoringResult(score=round(score), category=self._categorize(score))

class LLMEnhancedScoring(ScoringStrategy):
    """Скоринг с LLM-объяснением (декорирует rule-based)."""

    def __init__(self, base: RuleBasedScoring, llm_service: LLMService):
        self._base = base
        self._llm = llm_service

    async def calculate(self, metrics: MerchantMetrics) -> ScoringResult:
        result = await self._base.calculate(metrics)
        try:
            result.explanation = await self._llm.explain(metrics, result.score)
        except LLMUnavailableError:
            result.explanation = None  # Graceful degradation
        return result
```

## Пример: Repository (Template Method)

```python
# backend/app/repositories/base.py
from typing import Generic, TypeVar, Type, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с CRUD (GoF: Template Method)."""

    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get_by_id(self, db: AsyncSession, id: str) -> ModelType | None:
        result = await db.execute(select(self._model).where(self._model.id == id))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        result = await db.execute(select(self._model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        db_obj = self._model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj
```

## Когда НЕ применять паттерны

- Не создавай абстракции ради абстракций — если класс имеет одну реализацию и не планируется расширение, не нужен интерфейс
- Не используй Singleton через метаклассы — в FastAPI достаточно `@lru_cache` и `Depends()`
- Не используй Abstract Factory если нет семейств связанных объектов
- MVP — простота важнее расширяемости. Паттерн оправдан только если он решает конкретную проблему прямо сейчас
