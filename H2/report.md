# Домашнее задание: Создание системы правил и промпт-шаблонов

Проект: **MEXC P2P Агрегатор** — веб-приложение для мониторинга и анализа P2P-объявлений криптобиржи MEXC (режим read-only).

Инструмент: **Kiro** (вместо Cursor). Аналог `.cursorrules` в Kiro — steering-файлы `.kiro/steering/*.md`.

---

## Шаг 1. Анализ требований к проекту

### Проект

MEXC P2P Агрегатор — учебный проект, представляющий собой веб-приложение для мониторинга и анализа P2P-объявлений криптобиржи MEXC. Приложение работает в режиме «только чтение» (read-only): не совершает торговых операций от имени пользователя и не требует API-ключей MEXC.

### Технологический стек

| Слой | Технология |
|------|-----------|
| Фронтенд | Vue.js 3 (Composition API) + Quasar Framework 2 + TypeScript 5 |
| API-клиент фронтенда | Orval (генерация из OpenAPI-спецификации бэкенда) |
| Бэкенд | Python 3.12 + FastAPI 0.115+ + Pydantic v2 |
| БД | PostgreSQL 16 + SQLAlchemy 2 (async) |
| Миграции БД | Alembic |
| Кэш / Сессии | Redis 7 |
| LLM | OpenAI API (GPT-4o-mini) |
| Тесты фронтенд | Vitest + Vue Test Utils |
| Тесты бэкенд | pytest + pytest-asyncio + httpx |
| Линтинг | ESLint + Prettier (фронт), Ruff (бэк) |
| Контейнеризация | Docker + Docker Compose |

### Ключевые требования к стилю кода, архитектуре, стандартам

**Архитектура:**
- Два отдельных проекта: `frontend/` и `backend/`, связанных через REST API
- Бэкенд: трёхслойная архитектура Repository → Service → Router (FastAPI)
- Фронтенд общается с бэкендом через сгенерированный Orval-клиент (из OpenAPI-схемы FastAPI)
- Server-side polling P2P-данных (asyncio tasks), не на клиенте
- Graceful degradation при недоступности LLM или источника данных
- Configuration over code: веса скоринга, интервалы, TTL — в переменных окружения

**Стиль кода — бэкенд (Python):**
- Типизация везде, Pydantic v2 для схем, async everywhere
- Именование: `snake_case` (переменные, функции), `PascalCase` (классы), `UPPER_SNAKE_CASE` (константы)
- Линтинг: Ruff

**Стиль кода — фронтенд (TypeScript/Vue):**
- TypeScript strict mode, запрет `any`
- Только Composition API + `<script setup lang="ts">`
- Только Quasar UI-компоненты, API-клиент через Orval
- Форматирование: Prettier (100 символов, 2 пробела, одинарные кавычки)

**Стандарты разработки:**
- GoF-паттерны где уместно: Repository, Strategy, Facade, Observer, Template Method
- Миграции БД только через Alembic
- Безопасность: bcrypt, JWT, rate limiting, CORS, валидация Pydantic/Zod
- Docker + Docker Compose для разработки и деплоя

---

## Шаг 2. Создание системы правил (steering-файлы Kiro)

В Kiro аналогом `.cursorrules` являются steering-файлы в `.kiro/steering/*.md`. В отличие от единого файла Cursor, правила разделены по доменам с разными режимами подключения:

- **always** — подключается к каждому запросу (аналог `.cursorrules`)
- **fileMatch** — подключается автоматически когда в контексте файл по паттерну
- **manual** — подключается вручную через `#имя-файла` в чате

### Созданные файлы правил

| Файл | Режим | Назначение |
|------|-------|-----------|
| `00-project-core.md` | always | Роль AI-агента, стек технологий, архитектурные принципы, скиллы Kiro, общие ограничения |
| `01-backend-rules.md` | fileMatch: `backend/**` | Структура FastAPI-проекта, стиль Python, GoF на бэкенде, безопасность, обработка ошибок, тесты |
| `02-frontend-rules.md` | fileMatch: `frontend/**` | Структура Vue/Quasar-проекта, стиль TypeScript, Orval-интеграция, Quasar-правила, тесты |
| `03-database-rules.md` | fileMatch: `**/models/**,**/alembic/**` | SQLAlchemy 2 модели, async-сессии, индексы, Alembic миграции |
| `04-docker-rules.md` | manual | Docker, Docker Compose (dev/prod), Dockerfile multi-stage, .env |
| `05-gof-patterns.md` | fileMatch: `**/services/**,**/repositories/**` | Карта GoF-паттернов проекта с примерами (Strategy, Repository, Facade и др.) |

### Структура правил (по разделам из ДЗ)

**Роль:** Senior Full-Stack Developer, специализирующийся на Vue.js + Quasar (фронтенд) и Python + FastAPI (бэкенд). Следует принципам KISS, YAGNI, DRY. Применяет GoF-паттерны осознанно. Учитывает контекст MVP.

**Контекст проекта:** Полный стек технологий, архитектурные принципы (трёхслойная архитектура, server-side polling, graceful degradation), ссылки на установленные скиллы Kiro (gof-design-patterns, fastapi-templates, orval, quasar-skilld).

**Стиль кода:** Раздельные правила для Python (типизация, Pydantic v2, async, snake_case, Ruff) и TypeScript/Vue (strict mode, Composition API, PascalCase компоненты, Prettier).

**Ограничения:** Запрещённые библиотеки (Vuetify, axios, moment.js), запрещённые паттерны (Options API, `var`, `any`, прямые SQL), запрет функций из v1.1+, требования безопасности (bcrypt, CSRF, rate limiting, валидация).

**Формат вывода:** Структура проекта (frontend/ + backend/), паттерны API-эндпоинтов, модели SQLAlchemy, Alembic-миграции, тесты, Docker-конфигурация.

### Количество правил

Суммарно в steering-файлах зафиксировано **25+ конкретных правил** с примерами кода и паттернами (B1–B5 бэкенд, F1–F7 фронтенд, D1–D7 база данных, GoF-карта из 8 паттернов, Docker-правила).

---

## Шаг 3. Разработка промпт-шаблонов

Создана библиотека из 7 промпт-шаблонов в формате RTCF, привязанных к скиллам Kiro и стеку проекта. Каждый шаблон содержит универсальную заготовку и конкретный пример использования на задачах MEXC P2P Агрегатора.

| # | Сценарий | Скилл Kiro | Пример из проекта |
|---|----------|-----------|-------------------|
| 1 | Генерация компонента/функции | #fastapi-templates | Эндпоинт GET /api/v1/advertisements с фильтрацией |
| 2 | Рефакторинг кода | #gof-design-patterns | Рефакторинг calculate_risk_score → паттерн Strategy |
| 3 | Написание тестов | — | Unit-тесты для AdvertisementRepository (pytest) |
| 4 | Исправление багов | — | Race condition в polling-сервисе (distributed lock) |
| 5 | Декомпозиция задачи | #gof-design-patterns | Модуль риск-скоринга с LLM на подзадачи спринта |
| 6 | Генерация API-клиента | #orval | Настройка Orval для vue-query хуков из OpenAPI |
| 7 | Создание UI-компонента | #quasar-skilld | AdvertisementTable с QTable, риск-скор, tooltip |

Полная библиотека шаблонов: **[prompt_templates.md](prompt_templates.md)**

---

## Шаг 4. Применение Chain-of-Thought техники

### Выбранная задача

**«Спроектировать и реализовать модуль риск-скоринга с LLM-объяснениями»** — одна из самых сложных задач MVP, затрагивающая бэкенд (FastAPI + SQLAlchemy), интеграцию с внешним API (OpenAI), кэширование (Redis), GoF-паттерны (Strategy, Decorator) и API-дизайн.

### Разбиение на логические шаги

```
Шаг 1: Архитектура модуля → Шаг 2: Модели данных → Шаг 3: Сервис скоринга →
→ Шаг 4: LLM-объяснения + кэш → Шаг 5: API-эндпоинт → Шаг 6: Тесты
```

Каждый шаг использует результат предыдущего как контекст.

---

### Шаг 1. Проектирование архитектуры модуля

**Промпт:**

```
Role: Архитектор бэкенда. Используй скилл #gof-design-patterns.

Task: Спроектировать архитектуру модуля риск-скоринга для P2P-объявлений.
Модуль должен: рассчитывать числовой скор 1-10 по метрикам мерчанта,
маппировать в категории (низкий/средний/высокий), поддерживать LLM-объяснения
с fallback, кэшировать объяснения в Redis.

Context:
- Стек: FastAPI + SQLAlchemy 2 async + Redis + OpenAI API
- Метрики мерчанта: rating, trades_count, success_rate, closing_speed (опционально)
- Веса факторов из конфига (pydantic-settings), не из UI
- В будущем (v1.1) возможен LLM-enhanced скоринг — архитектура должна это допускать

Format: Диаграмма классов (текстом), выбор GoF-паттернов с обоснованием,
описание взаимодействия компонентов.
```

**Результат:**

Выбраны паттерны:
- **Strategy** — интерфейс `ScoringStrategy` с реализациями `RuleBasedScoring` (MVP) и будущей `LLMEnhancedScoring` (v1.1)
- **Facade** — `ScoringFacade` объединяет скоринг + LLM-объяснения + кэш в единый интерфейс для API-слоя
- **Decorator** (концептуально) — LLM-объяснение «оборачивает» базовый скор, добавляя текстовое поле

Структура файлов:
```
backend/app/services/scoring/
├── strategy.py          # ScoringStrategy (ABC), RuleBasedScoring
├── llm_explainer.py     # LLMExplainer (обращение к OpenAI + кэш Redis)
├── facade.py            # ScoringFacade (единый интерфейс)
└── schemas.py           # ScoringResult, ScoringWeights
```

---

### Шаг 2. Модели данных и миграция

**Промпт:**

```
Role: Backend Developer. Используй скилл #fastapi-templates.

Task: Создать SQLAlchemy-модели и Pydantic-схемы для модуля скоринга.
Добавить поле risk_score в модель Advertisement.

Context:
- Результат Шага 1: архитектура с Strategy + Facade
- Модель Advertisement уже существует (id, price, volume, direction, currency,
  payment_methods, is_active, merchant_id)
- Модель Merchant уже существует (id, name, rating, trades_count, success_rate,
  closing_speed)
- Нужно: добавить risk_score (int 1-10) и risk_category (enum) в Advertisement
- Миграция через Alembic

Format: SQLAlchemy модели (дополнения), Pydantic-схемы ScoringResult и
MerchantMetrics, Alembic миграция.
```

**Результат:**

Дополнение модели Advertisement:
```python
class RiskCategory(str, enum.Enum):
    LOW = "low"        # 1-3
    MEDIUM = "medium"  # 4-7
    HIGH = "high"      # 8-10

class Advertisement(Base):
    # ... существующие поля ...
    risk_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    risk_category: Mapped[RiskCategory | None] = mapped_column(String(10), nullable=True)
```

Pydantic-схемы:
```python
class MerchantMetrics(BaseModel):
    rating: float = Field(ge=0, le=5)
    trades_count: int = Field(ge=0)
    success_rate: float = Field(ge=0, le=1)
    closing_speed: float | None = None  # секунды, может отсутствовать

class ScoringResult(BaseModel):
    score: int = Field(ge=1, le=10)
    category: RiskCategory
    explanation: str | None = None  # до 300 символов, от LLM
```

Миграция: `alembic revision --autogenerate -m "add_risk_score_to_advertisements"`

---

### Шаг 3. Сервис скоринга (Strategy)

**Промпт:**

```
Role: Senior Backend Developer. Используй скиллы #fastapi-templates и #gof-design-patterns.

Task: Реализовать сервис скоринга с паттерном Strategy.

Context:
- Результат Шага 1: интерфейс ScoringStrategy, реализация RuleBasedScoring
- Результат Шага 2: MerchantMetrics, ScoringResult, ScoringWeights
- Формула: score = rating * w1 + trades_normalized * w2 + success_rate * w3 + speed_normalized * w4
- При отсутствии closing_speed — перераспределить вес w4 пропорционально между w1, w2, w3
- Нормализация: trades_count → 0-1 (логарифмическая шкала, max=10000),
  closing_speed → 0-1 (инверсия, быстрее = лучше, max=3600 сек)
- Маппинг: 1-3 = low, 4-7 = medium, 8-10 = high
- Веса из pydantic-settings

Format: Полная реализация strategy.py с типизацией, docstrings, обработкой edge cases.
```

**Результат:**

```python
class ScoringStrategy(ABC):
    @abstractmethod
    async def calculate(self, metrics: MerchantMetrics) -> ScoringResult: ...

class RuleBasedScoring(ScoringStrategy):
    def __init__(self, weights: ScoringWeights):
        self._weights = weights

    async def calculate(self, metrics: MerchantMetrics) -> ScoringResult:
        factors = {
            "rating": metrics.rating / 5.0,
            "trades": min(math.log1p(metrics.trades_count) / math.log1p(10000), 1.0),
            "success_rate": metrics.success_rate,
        }
        active_weights = {"rating": self._weights.rating, ...}

        if metrics.closing_speed is not None:
            factors["speed"] = 1.0 - min(metrics.closing_speed / 3600, 1.0)
            active_weights["speed"] = self._weights.speed
        else:
            # Перераспределение веса speed пропорционально
            total = sum(v for k, v in active_weights.items())
            active_weights = {k: v / total for k, v in active_weights.items()}

        raw = sum(factors[k] * active_weights[k] for k in factors)
        score = max(1, min(10, round(raw * 10)))
        # Инверсия: высокий raw = надёжный мерчант = НИЗКИЙ риск
        risk_score = 11 - score
        return ScoringResult(score=risk_score, category=self._categorize(risk_score))
```

**Что потребовало корректировки:** Инверсия скора — высокие метрики мерчанта означают НИЗКИЙ риск, а не высокий. AI первоначально перепутал направление шкалы.

---

### Шаг 4. LLM-объяснения с кэшированием

**Промпт:**

```
Role: Senior Backend Developer, специалист по интеграции с LLM.

Task: Реализовать LLMExplainer — сервис для генерации текстовых объяснений
риск-скора с кэшированием в Redis.

Context:
- Результат Шага 3: RuleBasedScoring возвращает ScoringResult (score, category)
- OpenAI API: GPT-4o-mini, ответ до 300 символов
- Кэш: Redis, ключ = merchant_id, TTL = 10 минут
- Fallback: при ошибке OpenAI — вернуть ScoringResult без explanation (= None)
- Не блокировать основной flow при недоступности LLM

Format: Полная реализация llm_explainer.py, промпт для OpenAI, обработка ошибок,
кэширование.
```

**Результат:**

```python
class LLMExplainer:
    def __init__(self, openai_client: AsyncOpenAI, redis: Redis, ttl: int = 600):
        self._client = openai_client
        self._redis = redis
        self._ttl = ttl

    async def explain(self, merchant_id: str, metrics: MerchantMetrics,
                      score: int, category: RiskCategory) -> str | None:
        # 1. Проверить кэш
        cached = await self._redis.get(f"llm:score:{merchant_id}")
        if cached:
            return cached.decode()

        # 2. Запросить LLM
        try:
            response = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "system",
                    "content": "Ты аналитик P2P-рисков. Объясни риск-скор кратко, до 300 символов, на русском."
                }, {
                    "role": "user",
                    "content": f"Мерчант: рейтинг {metrics.rating}/5, "
                               f"{metrics.trades_count} сделок, "
                               f"{metrics.success_rate*100:.0f}% успешных. "
                               f"Риск-скор: {score}/10 ({category.value})."
                }],
                max_tokens=150,
            )
            explanation = response.choices[0].message.content[:300]

            # 3. Сохранить в кэш
            await self._redis.setex(f"llm:score:{merchant_id}", self._ttl, explanation)
            return explanation

        except Exception as e:
            logger.warning("LLM unavailable: %s", e)
            return None  # Graceful degradation
```

---

### Шаг 5. API-эндпоинт

**Промпт:**

```
Role: Backend Developer. Используй скилл #fastapi-templates.

Task: Создать эндпоинт GET /api/v1/scoring/{advertisement_id}/explain
для получения LLM-объяснения риск-скора.

Context:
- Результат Шагов 3-4: ScoringFacade объединяет RuleBasedScoring + LLMExplainer
- Вход: advertisement_id (path param)
- Выход: ScoringResult (score, category, explanation)
- Если LLM недоступен — explanation = null, добавить поле llm_available = false
- Авторизация: требуется (Depends(get_current_user))

Format: Эндпоинт с Pydantic response model, обработка 404, dependency injection.
```

**Результат:**

```python
@router.get("/{advertisement_id}/explain", response_model=ScoringExplainResponse)
async def get_scoring_explanation(
    advertisement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    scoring: ScoringFacade = Depends(get_scoring_facade),
):
    ad = await advertisement_repo.get_by_id(db, advertisement_id)
    if not ad:
        raise AppException(404, "Объявление не найдено", "AD_NOT_FOUND")

    result = await scoring.score_and_explain(ad.merchant)
    return ScoringExplainResponse(
        score=result.score,
        category=result.category,
        explanation=result.explanation,
        llm_available=result.explanation is not None,
    )
```

---

### Шаг 6. Тесты

**Промпт:**

```
Role: QA Engineer с опытом в pytest.

Task: Написать тесты для модуля скоринга: RuleBasedScoring, LLMExplainer, эндпоинт.

Context:
- Результаты Шагов 3-5: полная реализация модуля
- Стек: pytest + pytest-asyncio + httpx
- Моки: AsyncMock для OpenAI client и Redis
- Критические сценарии: отсутствие closing_speed, LLM недоступен,
  кэш-хит, кэш-мисс, невалидные метрики

Format: Три test-файла, минимум 3 теста на компонент, фикстуры для переиспользования.
```

**Результат:** 12 тестов в трёх файлах:
- `test_scoring_strategy.py` — 5 тестов (нормальный расчёт, без closing_speed, граничные значения, нулевые метрики, максимальные метрики)
- `test_llm_explainer.py` — 4 теста (кэш-хит, кэш-мисс + LLM ответ, LLM ошибка → None, превышение 300 символов)
- `test_scoring_endpoint.py` — 3 теста (happy path, 404, LLM недоступен → llm_available=false)

---

### Итоги Chain-of-Thought

| Шаг | Вход | Выход | Что дал CoT |
|-----|------|-------|-------------|
| 1. Архитектура | Требования из ТЗ | Диаграмма классов, выбор паттернов | Определил структуру до написания кода |
| 2. Модели | Архитектура (Шаг 1) | SQLAlchemy + Pydantic + миграция | Типы данных согласованы с архитектурой |
| 3. Скоринг | Модели (Шаг 2) | RuleBasedScoring с формулой | Использовал типы из Шага 2 |
| 4. LLM | Скоринг (Шаг 3) | LLMExplainer + кэш | Знал формат ScoringResult из Шага 3 |
| 5. API | Всё выше | Эндпоинт с DI | Собрал все компоненты через Facade |
| 6. Тесты | Всё выше | 12 тестов | Знал все edge cases из предыдущих шагов |

**Ключевой вывод:** Без CoT пришлось бы описывать всю задачу в одном промпте — AI потерял бы контекст и выдал бы поверхностное решение. Пошаговый подход позволил на каждом шаге получить глубокую проработку, а результат предыдущего шага автоматически становился контекстом для следующего.

---

## Шаг 5. Тестирование системы правил

Для оценки эффективности steering-правил сгенерирован один и тот же модуль (сервис скоринга) двумя способами: минимальным промптом без правил и с активными steering-файлами + скиллами Kiro.

### Промпт без правил

> «Напиши сервис расчёта риск-скора для P2P-объявлений»

Результат: `samples/without_rules/scoring.py`

### Промпт с правилами

> Тот же запрос, но с активными steering-файлами (`00-project-core`, `01-backend-rules`, `05-gof-patterns`) и скиллами `#fastapi-templates`, `#gof-design-patterns`

Результат: `samples/with_rules/scoring_strategy.py`

### Сравнение результатов

| Критерий | Без правил | С правилами |
|----------|-----------|-------------|
| Типизация | `dict` на входе/выходе, нет аннотаций | Pydantic v2 модели, полные аннотации типов |
| Архитектура | Одна функция, всё в куче | GoF Strategy: ABC-интерфейс + реализация, разделение ответственности |
| Обработка отсутствующих данных | Не обрабатывает `closing_speed` | Перераспределение весов пропорционально |
| Конфигурация весов | Захардкожены в теле функции | Вынесены в `ScoringWeights` (из pydantic-settings) |
| Нормализация | Примитивная (`trades / 1000`) | Логарифмическая шкала, инверсия скорости |
| Логирование | Нет | `logger.debug` с промежуточными результатами |
| Async | Синхронный код | Async-совместимый (async def) |
| OpenAI API | Устаревший `ChatCompletion.create` | Вынесен в отдельный `LLMExplainer` (Шаг 4 CoT) |
| Redis | Глобальный `redis.Redis()` | Инъекция через конструктор (DI) |
| Обработка ошибок | Голый `except:` | Типизированные исключения, graceful degradation |
| Расширяемость | Нужно переписывать функцию | Новая стратегия = новый класс |
| Документация | Минимальные docstrings | JSDoc-стиль docstrings, комментарии к сложной логике |

### Выводы по тестированию

1. **Без правил** AI выдаёт «рабочий» код, но с устаревшим API, без типизации, без архитектуры — пригоден только как прототип на выброс.
2. **С правилами** код сразу соответствует стеку проекта (async, Pydantic v2, Strategy), готов к интеграции без переписывания.
3. Количество итераций до рабочего кода: ~3–4 без правил vs 1–2 с правилами.
4. Steering-правила особенно эффективны для: выбора правильных библиотек/API, соблюдения архитектурных паттернов, единообразия стиля кода.

---

## Шаг 6. Оформление результатов

### Артефакты

| Артефакт | Файл | Описание |
|----------|------|----------|
| Система правил (аналог .cursorrules) | `.kiro/steering/00-project-core.md` | Роль, стек, архитектура, скиллы, ограничения |
| | `.kiro/steering/01-backend-rules.md` | Правила бэкенда: FastAPI, Python, безопасность |
| | `.kiro/steering/02-frontend-rules.md` | Правила фронтенда: Vue, Quasar, Orval, TypeScript |
| | `.kiro/steering/03-database-rules.md` | SQLAlchemy модели, Alembic миграции |
| | `.kiro/steering/04-docker-rules.md` | Docker, Docker Compose, инфраструктура |
| | `.kiro/steering/05-gof-patterns.md` | Карта GoF-паттернов проекта |
| Библиотека промпт-шаблонов | `prompt_templates.md` | 7 шаблонов RTCF с примерами |
| Отчёт о применении | `report_my.md` | Этот файл |
| Примеры кода (без правил) | `samples/without_rules/scoring.py` | Генерация без steering-правил |
| Примеры кода (с правилами) | `samples/with_rules/scoring_strategy.py` | Генерация с steering-правилами |
| Требования проекта | `.kiro/specs/mexc-p2p-aggregator/requirements.md` | 27 требований с критериями приёмки |
| Аудит ТЗ | `solution/tz_audit.md` | Противоречия, пропуски, рекомендации |

### Особенности реализации в Kiro (vs Cursor)

В ДЗ предполагается использование Cursor и файла `.cursorrules`. Работа выполнена в Kiro, где аналогичная функциональность реализована через steering-файлы. Ключевые отличия:

| Аспект | Cursor (.cursorrules) | Kiro (steering) |
|--------|----------------------|-----------------|
| Формат | Один файл в корне проекта | Несколько .md файлов в `.kiro/steering/` |
| Подключение | Всегда активен | always / fileMatch / manual — гибкое управление |
| Контекстность | Все правила всегда в контексте | Правила бэкенда подключаются только при работе с `backend/**` |
| Скиллы | Нет аналога | Подключаемые пакеты знаний (GoF, FastAPI, Orval, Quasar) |
| Спецификации | Нет аналога | `.kiro/specs/` — формальные требования с критериями приёмки |

### Итоговые выводы

1. **Steering-правила работают.** Сравнение генерации с правилами и без показало кратное улучшение качества: правильный стек, типизация, архитектурные паттерны, обработка ошибок — всё с первой итерации.

2. **Разделение правил по доменам** (fileMatch) эффективнее единого файла — AI получает только релевантный контекст, не перегружается.

3. **Скиллы Kiro** (fastapi-templates, gof-design-patterns, orval, quasar-skilld) дают AI глубокие знания о конкретных технологиях, которых нет в базовой модели.

4. **RTCF-структура промптов** — необходимый минимум. Без чёткого Role/Task/Context/Format результат непредсказуем.

5. **Chain-of-Thought** критически важен для сложных задач. Декомпозиция на 6 шагов (архитектура → модели → сервис → LLM → API → тесты) дала качественно лучший результат, чем попытка решить всё одним промптом.

6. **Контекст решает.** Чем точнее описаны стек, версии, формулы и ограничения — тем меньше итераций и ручных правок.
