---
inclusion: fileMatch
fileMatchPattern: "backend/**"
---

# Правила бэкенда (Python + FastAPI)

## Структура проекта

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── profile.py
│   │   │   │   ├── advertisements.py
│   │   │   │   ├── scoring.py
│   │   │   │   └── admin.py
│   │   │   └── router.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py          # pydantic-settings
│   │   ├── security.py        # JWT, bcrypt
│   │   ├── database.py        # async SQLAlchemy engine + session
│   │   └── redis.py           # aioredis client
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic v2 schemas (request/response)
│   ├── services/              # Бизнес-логика
│   ├── repositories/          # Data access layer (SQLAlchemy queries)
│   ├── tasks/                 # Background tasks (polling, cleanup)
│   └── main.py                # FastAPI app + lifespan
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_advertisements.py
│   └── test_scoring.py
├── pyproject.toml
├── Dockerfile
└── .env.example
```

## Стиль кода Python

### Правило B1: Типизация везде

Все функции, методы и параметры должны иметь аннотации типов. Используй `from __future__ import annotations` в каждом файле.

```python
# Плохо
def get_user(db, user_id):
    ...

# Хорошо
from __future__ import annotations
async def get_user(db: AsyncSession, user_id: int) -> User | None:
    ...
```

### Правило B2: Pydantic v2 для схем

Все request/response модели — через Pydantic v2 с `model_config = ConfigDict(...)`. Не используй Pydantic v1 синтаксис (`class Config`).

```python
from pydantic import BaseModel, ConfigDict, Field

class AdvertisementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    price: Decimal
    volume: Decimal
    risk_score: int = Field(ge=1, le=10)
    direction: Direction
```

### Правило B3: Async everywhere

Все эндпоинты, сервисы и репозитории — async. Не используй синхронные вызовы к БД или Redis.

```python
# Плохо
@router.get("/ads")
def get_ads(db: Session = Depends(get_db)):
    ...

# Хорошо
@router.get("/ads")
async def get_ads(db: AsyncSession = Depends(get_db)):
    ...
```

### Правило B4: Именование Python

- Файлы, переменные, функции: `snake_case`
- Классы: `PascalCase`
- Константы: `UPPER_SNAKE_CASE`
- Приватные методы: `_leading_underscore`

### Правило B5: Конфигурация через pydantic-settings

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str
    POLLING_INTERVAL_SEC: int = 10
    LLM_CACHE_TTL_SEC: int = 600
    SCORING_WEIGHTS: dict = {"rating": 0.3, "trades": 0.25, "success_rate": 0.3, "speed": 0.15}

    model_config = ConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## GoF-паттерны на бэкенде

Используй паттерны осознанно, не ради паттернов:

- **Repository** — для всех операций с БД. Базовый `BaseRepository[ModelType]` с CRUD, конкретные репозитории наследуют и добавляют специфичные запросы
- **Strategy** — для скоринга: разные стратегии расчёта риск-скора (rule-based, LLM-enhanced). Интерфейс `ScoringStrategy`, реализации `RuleBasedScoring`, `LLMEnhancedScoring`
- **Factory Method** — для создания сервисов с зависимостями через FastAPI `Depends()`
- **Observer** — для уведомления подсистем об обновлении P2P-данных (scoring пересчёт, кэш инвалидация)
- **Template Method** — для базового flow обработки API-запросов (валидация → бизнес-логика → ответ)
- **Facade** — `AdvertisementFacade` объединяет polling service, scoring service и profitability service в единый интерфейс для API-слоя

## Безопасность бэкенда

- Пароли: bcrypt через `passlib[bcrypt]`
- JWT-токены: `python-jose[cryptography]`
- Rate limiting: `slowapi` или кастомный middleware с Redis
- Валидация: Pydantic v2 на каждом эндпоинте (автоматически через FastAPI)
- CORS: настроить `CORSMiddleware` с явным списком origins
- Не возвращай stack trace клиенту — кастомный exception handler

## Обработка ошибок

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "detail": exc.detail},
    )
```

## Тесты бэкенда

- Фреймворк: pytest + pytest-asyncio
- HTTP-клиент для тестов: httpx `AsyncClient`
- Фикстуры: `conftest.py` с тестовой БД (SQLite async или testcontainers-postgres)
- Структура: `tests/` зеркалит `app/`, один test-файл на модуль
- Моки внешних сервисов (MEXC API, OpenAI) через `unittest.mock.AsyncMock`
