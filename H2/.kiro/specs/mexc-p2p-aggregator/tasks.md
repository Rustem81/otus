# Задачи реализации: MEXC P2P Агрегатор (MVP)

Задачи сформулированы по шаблонам из `prompt_templates.md` (RTCF-структура).

## Фаза 1: Инфраструктура и база

### Задача 1.1: Инициализация проекта и Docker
- [x] Создать структуру `backend/` (FastAPI) и `frontend/` (Quasar)
- [x] Настроить Docker Compose: backend, frontend, postgres, redis
- [x] Создать Dockerfile (multi-stage) для backend и frontend
- [x] Настроить .env.example со всеми переменными

**Промпт-шаблон:** #5 (Декомпозиция) + `#04-docker-rules`

```
Role: DevOps / Full-Stack Developer.
Task: Инициализировать проект с Docker Compose для dev-окружения.
Context: FastAPI backend, Quasar frontend, PostgreSQL 16, Redis 7.
         Steering: 04-docker-rules.md (manual).
Format: docker-compose.yml, Dockerfile для backend и frontend, .env.example.
```

### Задача 1.2: Схема БД и начальная миграция
- [x] Создать SQLAlchemy модели: User, TraderProfile, Merchant, Advertisement, PollingError, SavedFilters
- [x] Настроить Alembic (async env.py)
- [x] Создать начальную миграцию
- [x] Добавить индексы

**Промпт-шаблон:** #1 (Генерация) + `#fastapi-templates`

```
Role: Senior Backend Developer. Используй скилл #fastapi-templates.
Task: Создать SQLAlchemy 2 async модели для всех сущностей MVP.
Context: Модели из design.md (User, TraderProfile, Merchant, Advertisement,
         PollingError, SavedFilters). PostgreSQL 16, Alembic для миграций.
         Steering: 03-database-rules.md.
Format: Файлы в backend/app/models/, alembic/env.py (async), начальная миграция.
```

### Задача 1.3: Базовая конфигурация FastAPI
- [x] Создать main.py с lifespan (startup/shutdown)
- [x] Настроить pydantic-settings (config.py)
- [x] Настроить async DB engine + session
- [x] Настроить Redis client
- [x] Настроить CORS middleware
- [x] Добавить GET /health

**Промпт-шаблон:** #1 (Генерация) + `#fastapi-templates`

```
Role: Senior Backend Developer. Используй скилл #fastapi-templates.
Task: Создать базовую конфигурацию FastAPI приложения.
Context: Lifespan events для DB и Redis, pydantic-settings, CORS,
         health check endpoint. Паттерн из fastapi-templates skill.
Format: main.py, core/config.py, core/database.py, core/redis.py.
```

---

## Фаза 2: Аутентификация (Требования 1, 2, 22)

### Задача 2.1: Регистрация и вход
- [x] UserRepository (BaseRepository + get_by_email)
- [x] AuthService (register, login, verify_email, logout)
- [x] AuthRouter (POST /register, /login, /logout, GET /verify-email/{token})
- [x] JWT + серверная сессия в Redis
- [x] Хеширование паролей (bcrypt)

**Промпт-шаблон:** #1 (Генерация) + `#fastapi-templates` + `#gof-design-patterns`

```
Role: Senior Backend Developer. Используй скиллы #fastapi-templates, #gof-design-patterns.
Task: Реализовать модуль аутентификации: регистрация, вход, выход, подтверждение email.
Context: FastAPI + SQLAlchemy async + Redis. Repository → Service → Router.
         GoF: Repository (BaseRepository → UserRepository), Factory Method (Depends).
         Безопасность: bcrypt, JWT, сессии в Redis (TTL 24ч).
Format: repositories/user_repository.py, services/auth_service.py,
        api/v1/endpoints/auth.py, core/security.py.
```

### Задача 2.2: Rate limiting и CSRF
- [x] Rate limiting middleware (Redis sliding window)
- [x] CSRF double-submit cookie
- [x] Ролевая модель (USER/ADMIN dependency)

**Промпт-шаблон:** #1 (Генерация) + `#fastapi-templates`

```
Role: Senior Backend Developer, специалист по безопасности.
Task: Реализовать rate limiting (5 login/мин, 3 register/час на IP)
      и CSRF-защиту для мутирующих эндпоинтов.
Context: FastAPI middleware, Redis для счётчиков (sliding window).
         CSRF: double-submit cookie pattern.
Format: middleware/rate_limiter.py, middleware/csrf.py, api/dependencies.py (role check).
```

### Задача 2.3: Тесты аутентификации
- [x] Тесты регистрации (happy path, дубликат email, невалидные данные)
- [x] Тесты входа (успех, неверный пароль, неподтверждённый email)
- [x] Тесты rate limiting (превышение лимита)
- [x] Тесты ролевой модели (USER vs ADMIN)

**Промпт-шаблон:** #3 (Тесты)

```
Role: QA Engineer с опытом в pytest.
Task: Написать тесты для модуля аутентификации.
Context: pytest + pytest-asyncio + httpx AsyncClient. Моки: Redis (AsyncMock).
         Сценарии: register, login, rate limit, role check, CSRF.
Format: tests/test_auth.py, минимум 12 тестов, фикстуры в conftest.py.
```

---

## Фаза 3: Профиль трейдера (Требования 4, 5, 6, 7, 15)

### Задача 3.1: CRUD профиля
- [x] ProfileRepository
- [x] ProfileService (валидация, сохранение, получение)
- [x] ProfileRouter (GET/PUT /profile, GET /banks)
- [x] Сохранение/загрузка фильтров (GET/PUT /profile/filters)

**Промпт-шаблон:** #1 (Генерация) + `#fastapi-templates`

```
Role: Senior Backend Developer. Используй скилл #fastapi-templates.
Task: Реализовать CRUD профиля трейдера: банки, суммы, валютная пара,
      риск-профиль, комиссии, сохранённые фильтры.
Context: Repository → Service → Router. Pydantic v2 схемы.
         Один набор фильтров на пользователя (JSONB).
Format: repositories/profile_repository.py, services/profile_service.py,
        api/v1/endpoints/profile.py, schemas/profile.py.
```

---

## Фаза 4: Сбор P2P-данных (Требования 8, 9, 10, 11)

### Задача 4.0: Mock-сервис для разработки
- [x] Создать `mock-server/` — отдельный FastAPI-проект (порт 8001)
- [x] Реализовать генератор данных: пул 30-50 мерчантов, реалистичные цены (нормальное распределение), РФ-банки
- [x] Реализовать эндпоинты p2p.army: `/v1/api/ping`, `/v1/api/get_p2p_order_book`, `/v1/api/get_p2p_prices`, `/v1/api/get_popular_p2p_payment_methods`
- [x] Добавить mock-server в docker-compose.yml
- [x] Данные должны меняться при каждом запросе (имитация обновления)

**Промпт-шаблон:** #1 (Генерация) + `#fastapi-templates`

```
Role: Senior Backend Developer. Используй скилл #fastapi-templates.
Task: Создать mock-сервис, эмулирующий API p2p.army для локальной разработки.
Context: FastAPI на порту 8001. Формат ответов идентичен p2p.army API
         (get_p2p_order_book, ping, get_p2p_prices, get_popular_p2p_payment_methods).
         Генерация реалистичных данных: 30-50 мерчантов, цены RUB/USDT 88-96,
         банки: СБП, Сбер, Тинькофф, Альфа, Райффайзен. Не требует API-ключа.
Format: mock-server/app/main.py, generator.py, merchants.py, Dockerfile.
```

### Задача 4.1: P2P Data Source (Strategy pattern)
- [x] Интерфейс `P2PDataSource` (ABC) с методами: `get_order_book`, `get_prices`, `get_payment_methods`, `ping`
- [x] Реализация `P2PArmyClient` (httpx async, заголовок X-APIKEY)
- [x] Реализация `MockClient` (тот же интерфейс, обращается к mock-server)
- [x] Выбор реализации через конфиг `P2P_DATA_SOURCE` (p2p_army / mock)
- [x] Маппинг полей p2p.army → модели Advertisement + Merchant
- [x] Exponential backoff с jitter при 429/5xx

**Промпт-шаблон:** #1 (Генерация) + `#fastapi-templates` + `#gof-design-patterns`

```
Role: Senior Backend Developer. Используй скиллы #fastapi-templates, #gof-design-patterns.
Task: Реализовать P2P Data Source с паттерном Strategy — интерфейс P2PDataSource
      с реализациями P2PArmyClient и MockClient.
Context: p2p.army API: POST /v1/api/get_p2p_order_book с параметрами
         market, fiat, asset, side, payment_method, limit. Авторизация: X-APIKEY.
         Маппинг полей из design.md. Backoff при ошибках.
         GoF: Strategy (P2PDataSource ABC → P2PArmyClient, MockClient).
Format: services/p2p_source/interface.py, services/p2p_source/p2p_army.py,
        services/p2p_source/mock_client.py, schemas/p2p_raw.py.
```

### Задача 4.2: Polling task
- [x] Background task (asyncio) с интервалом из конфига
- [x] Distributed lock (Redis SETNX) против параллельных циклов
- [x] Обновление advertisements + merchants в БД
- [x] Пометка неактивных объявлений (TTL 15 сек)
- [x] Пересчёт Reference Price
- [x] Логирование ошибок (PollingError)

**Промпт-шаблон:** #5 (Декомпозиция) + #4 (Баги — race condition)

```
Role: Senior Backend Developer, специалист по async Python.
Task: Реализовать polling task для сбора P2P-данных.
Context: asyncio background task, Redis distributed lock, SQLAlchemy async.
         Интервал 10 сек, TTL неактивных 15 сек. Observer: уведомить scoring при обновлении.
         GoF: Observer (notify scoring + cache on data update).
Format: tasks/polling.py, services/reference_price.py, services/error_aggregator.py.
```

---

## Фаза 5: Скоринг и LLM (Требования 17, 18, 19)

### Задача 5.1: Rule-based скоринг
- [x] ScoringStrategy (ABC) + RuleBasedScoring
- [x] Нормализация метрик, перераспределение весов
- [x] Маппинг в категории (low/medium/high)

**Промпт-шаблон:** #1 (Генерация) + `#gof-design-patterns` + `#fastapi-templates`

```
Role: Senior Backend Developer. Используй скиллы #gof-design-patterns, #fastapi-templates.
Task: Реализовать rule-based скоринг с паттерном Strategy.
Context: Формула из design.md. Веса из pydantic-settings.
         При отсутствии closing_speed — перераспределение весов.
Format: services/scoring/strategy.py, services/scoring/schemas.py.
```

### Задача 5.2: LLM-объяснения + кэш
- [x] LLMExplainer (OpenAI async + Redis кэш TTL 10 мин)
- [x] Промпт для OpenAI (до 300 символов, на русском)
- [x] Fallback при недоступности LLM
- [x] ScoringFacade (объединяет scoring + LLM)

**Промпт-шаблон:** #1 (Генерация) + `#fastapi-templates`

```
Role: Senior Backend Developer, специалист по LLM-интеграции.
Task: Реализовать LLM-объяснения риск-скора с кэшированием.
Context: OpenAI API (GPT-4o-mini), Redis кэш (merchant_id, TTL 10 мин).
         Graceful degradation: при ошибке LLM — вернуть None.
         GoF: Facade (ScoringFacade = scoring + LLM + cache).
Format: services/scoring/llm_explainer.py, services/scoring/facade.py.
```

### Задача 5.3: Интегральный скор + API
- [x] IntegralScoreCalculator (в AdvertisementService)
- [x] ScoringRouter (GET /scoring/{merchant_id}/explain)

### Задача 5.4: Тесты скоринга
- [ ] Тесты RuleBasedScoring (нормальный, без speed, граничные)
- [ ] Тесты LLMExplainer (кэш-хит, кэш-мисс, LLM ошибка)
- [ ] Тесты эндпоинта (happy path, 404, LLM недоступен)

**Промпт-шаблон:** #3 (Тесты)

---

## Фаза 6: Доходность (Требование 20)

### Задача 6.1: Расчёт чистой доходности
- [x] ProfitabilityService (формула из design.md)
- [x] Интеграция в AdvertisementRouter (поле в ответе)
- [x] Обработка случая «комиссии не указаны»

---

## Фаза 7: Фронтенд (Требования 3, 12, 13, 14, 15, 16, 21)

### Задача 7.1: Инициализация Quasar + Orval
- [x] Создать Quasar-проект (TypeScript, Composition API)
- [x] Настроить orval.config.ts (vue-query, tags-split)
- [ ] Сгенерировать API-клиент из OpenAPI бэкенда
- [x] Настроить Pinia stores (auth, filters)

**Промпт-шаблон:** #6 (API-клиент) + `#orval`

### Задача 7.2: Аутентификация UI
- [x] LoginPage (вход + регистрация)
- [ ] Auth guard (router middleware)
- [x] MainLayout с ReadOnlyBadge

**Промпт-шаблон:** #7 (UI-компонент) + `#quasar-skilld`

### Задача 7.3: Основной экран — таблица объявлений
- [x] AdvertisementTable (QTable, сортировка, цветовой риск-скор)
- [x] FilterPanel (банки, рейтинг, сделки, сумма)
- [x] RiskScoreBadge + LLM-объяснение (QPopover)
- [x] ProfitabilityTooltip (QTooltip с детализацией)
- [ ] Состояния UI: loading, empty, error
- [x] Время последнего обновления

**Промпт-шаблон:** #7 (UI-компонент) + `#quasar-skilld`

### Задача 7.4: Карточка объявления
- [x] AdvertisementCard (QDialog модалка)
- [x] Кнопка «Открыть в MEXC» (target=_blank)
- [ ] Возврат фокуса при закрытии

### Задача 7.5: Профиль трейдера UI
- [x] ProfilePage + ProfileForm
- [x] BankSelector, RiskProfileSelector
- [x] Сохранение фильтров

### Задача 7.6: Админка UI
- [x] AdminPage (доступ только ADMIN)
- [x] SourceStatusPanel (OK/Degraded/Down)
- [x] ErrorStats (ошибки за 24ч)

---

## Фаза 8: Интеграция и финализация

### Задача 8.1: End-to-end проверка
- [ ] Полный flow: регистрация → профиль → таблица → карточка → MEXC
- [ ] Проверка фильтров и сортировки
- [ ] Проверка LLM fallback
- [ ] Проверка rate limiting

### Задача 8.2: Docker production
- [ ] docker-compose.prod.yml
- [ ] nginx reverse proxy
- [ ] Бэкап БД (pg_dump cron)
