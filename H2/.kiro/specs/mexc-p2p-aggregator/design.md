# Документ дизайна: MEXC P2P Агрегатор (MVP)

## Обзор архитектуры

Система состоит из двух отдельных приложений, связанных через REST API:

```
┌─────────────────────┐         ┌─────────────────────────────────────┐
│     Frontend        │  HTTP   │            Backend                  │
│  Vue.js + Quasar    │◄───────►│         FastAPI                     │
│  (SPA, port 9000)   │  JSON   │       (API, port 8000)              │
└─────────────────────┘         └──────┬──────────┬──────────┬────────┘
                                       │          │          │
                                  ┌────▼───┐ ┌───▼────┐ ┌───▼──────┐
                                  │PostgreSQL│ │ Redis  │ │ OpenAI   │
                                  │  (БД)   │ │(кэш)  │ │ (LLM)    │
                                  └────────┘ └────────┘ └──────────┘
                                       ▲
                                       │ polling (10 сек)
                              ┌────────┴─────────┐
                              │  P2P Data Source  │
                              │  (Strategy)       │
                              └──┬───────────┬────┘
                                 │           │
                          ┌──────▼──┐  ┌─────▼──────┐
                          │p2p.army │  │ Mock Server │
                          │  (prod) │  │   (dev)     │
                          └─────────┘  └────────────┘
```

## Источник P2P-данных: p2p.army API

Основной источник данных — сторонний сервис [p2p.army](https://p2p.army/en/api_docs), предоставляющий унифицированный REST API для P2P-объявлений с 8 бирж, включая MEXC.

### Используемые эндпоинты p2p.army

| Эндпоинт | Метод | Назначение |
|----------|-------|-----------|
| `/v1/api/get_p2p_order_book` | POST | Получение объявлений (основной) |
| `/v1/api/get_p2p_prices` | POST | Цены и спреды по payment methods |
| `/v1/api/get_popular_p2p_payment_methods` | POST | Список способов оплаты |
| `/v1/api/get_p2p_assets` | POST | Доступные криптоактивы |
| `/v1/api/get_p2p_fiats` | GET | Список фиатных валют |
| `/v1/api/ping` | GET | Проверка доступности |

### Формат ответа get_p2p_order_book (ключевой)

```json
{
  "status": 1,
  "ads": [
    {
      "pos": 1,
      "updated_at": 1712722398,
      "market": "mexc",
      "asset": "USDT",
      "fiat": "RUB",
      "side": "BUY",
      "payment_methods": ["SBP", "Sberbank"],
      "price": "92.50",
      "surplus_amount": "1500.00",
      "surplus_fiat": 138750.0,
      "min_fiat": "10000",
      "max_fiat": "100000",
      "text": "Быстрая оплата, онлайн 24/7",
      "user_name": "trader123",
      "user_id": "98765",
      "adv_id": "1777899381177700352",
      "user_orders": 1250,
      "user_rate": 98,
      "is_merchant": 1
    }
  ]
}
```

### Маппинг полей p2p.army → наши модели

| p2p.army | Наша модель | Поле |
|----------|-------------|------|
| `adv_id` | Advertisement | `external_id` |
| `price` | Advertisement | `price` |
| `surplus_amount` | Advertisement | `volume` |
| `min_fiat` | Advertisement | `min_limit` |
| `max_fiat` | Advertisement | `max_limit` |
| `side` | Advertisement | `direction` |
| `fiat` | Advertisement | `currency` |
| `payment_methods` | Advertisement | `payment_methods` |
| `user_name` | Merchant | `name` |
| `user_id` | Merchant | `external_id` |
| `user_rate` | Merchant | `success_rate` (÷100) |
| `user_orders` | Merchant | `trades_count` |
| `is_merchant` | Merchant | `is_verified` |
| `text` | Advertisement | `description` |

### Авторизация

- Заголовок: `X-APIKEY: {key}`
- Ключ хранится в `.env` как `P2P_ARMY_API_KEY`

### Rate limits

- Зависят от тарифа (Lite: 200K/мес, Pro: 500K/мес)
- Для MVP с поллингом раз в 10 сек по одной паре (BUY + SELL): ~520K запросов/мес → тариф Pro

## Mock-сервис для разработки

Для локальной разработки без API-ключа p2p.army используется mock-сервис, эмулирующий формат ответов p2p.army.

### Архитектура mock-сервиса

```
mock-server/
├── app/
│   ├── main.py              # FastAPI app (порт 8001)
│   ├── generator.py         # Генератор реалистичных P2P-данных
│   ├── merchants.py         # Пул мерчантов с метриками
│   └── config.py            # Настройки генерации
├── Dockerfile
└── pyproject.toml
```

### Функции mock-сервиса

- Реализует те же эндпоинты что и p2p.army (`/v1/api/get_p2p_order_book`, `/v1/api/ping` и т.д.)
- Генерирует реалистичные данные: пул из 30-50 мерчантов с разными рейтингами, цены с нормальным распределением вокруг базовой цены, случайные payment methods из реального списка РФ-банков
- Данные меняются при каждом запросе (имитация обновления объявлений)
- Поддерживает параметры `market`, `fiat`, `asset`, `side`, `payment_method`, `limit`
- Не требует API-ключа (или принимает любой)

### Переключение между prod и mock

Через переменную окружения:

```env
# Production (p2p.army)
P2P_DATA_SOURCE=p2p_army
P2P_ARMY_API_KEY=your-key-here
P2P_ARMY_BASE_URL=https://p2p.army/v1/api

# Development (mock)
P2P_DATA_SOURCE=mock
P2P_MOCK_BASE_URL=http://mock-server:8001/v1/api
```

GoF-паттерн **Strategy** — интерфейс `P2PDataSource` с реализациями `P2PArmyClient` и `MockClient`. Выбор через конфиг.

## Компоненты бэкенда

### Слои архитектуры (Repository → Service → Router)

```
Router (FastAPI endpoints)
  │ Pydantic schemas (request/response validation)
  ▼
Service (бизнес-логика)
  │ GoF: Strategy, Facade, Observer
  ▼
Repository (доступ к данным)
  │ GoF: Template Method (BaseRepository)
  ▼
SQLAlchemy models → PostgreSQL
```

### Модуль аутентификации (Требования 1, 2, 22)

**Компоненты:**
- `AuthRouter` — эндпоинты: POST /register, POST /login, POST /logout, GET /verify-email
- `AuthService` — бизнес-логика регистрации, входа, управления сессиями
- `UserRepository` — CRUD для пользователей (наследует BaseRepository)
- `RateLimiter` — middleware на Redis (sliding window): 5 login/мин, 3 register/час на IP
- `SessionManager` — создание/продление/удаление сессий в Redis (TTL 24ч)

**Модели:**
- `User` — id, email, hashed_password, role (USER/ADMIN), is_verified, created_at
- `Session` — хранится в Redis: `session:{token}` → `{user_id, role, created_at}`

**Безопасность:**
- Пароли: bcrypt через passlib
- Токены: JWT (access) + серверная сессия в Redis
- CSRF: double-submit cookie pattern
- Email verification: токен с TTL 24ч в Redis

### Модуль профиля трейдера (Требования 4, 5, 6, 7)

**Компоненты:**
- `ProfileRouter` — GET/PUT /profile, GET /profile/banks
- `ProfileService` — валидация и сохранение настроек
- `ProfileRepository` — CRUD для профилей

**Модели:**
- `TraderProfile` — user_id (FK), payment_methods (ARRAY), min_amount, max_amount, currency_pair, risk_profile (enum: low/medium/high), commission_percent, commission_fixed
- `SavedFilters` — user_id (FK), filters_json (JSONB) — один набор на пользователя

### Модуль сбора P2P-данных (Требования 8, 9, 10, 11)

**Компоненты:**
- `PollingTask` — asyncio background task, интервал из конфига (10 сек)
- `MexcP2PClient` — HTTP-клиент к MEXC P2P endpoint (httpx async)
- `AdvertisementRepository` — CRUD + mark_inactive, get_active_by_pair
- `MerchantRepository` — upsert метрик мерчантов
- `ReferencePriceCalculator` — средневзвешенная по топ-10 BUY/SELL
- `ErrorAggregator` — подсчёт ошибок по часам для админки

**GoF-паттерны:**
- **Observer** — при обновлении данных уведомляет ScoringService (пересчёт скоров) и CacheInvalidator
- **Template Method** — BaseRepository.create/update/delete, AdvertisementRepository добавляет mark_inactive

**Устойчивость:**
- Exponential backoff с jitter при 429/5xx от MEXC
- Distributed lock через Redis SETNX (предотвращение параллельных циклов поллинга)
- При недоступности источника — отдаём последние данные + timestamp последнего обновления

**Модели:**
- `Advertisement` — id, external_id (unique), price, volume, min_limit, max_limit, direction (BUY/SELL), currency, payment_methods (ARRAY), is_active, fetched_at, risk_score, risk_category, merchant_id (FK)
- `Merchant` — id, external_id, name, rating, trades_count, success_rate, closing_speed (nullable)
- `PollingError` — id, source, error_type, message, hour_bucket, created_at

**Индексы:**
- `(currency, direction, is_active)` — основной фильтр
- `(fetched_at)` — для TTL-очистки
- `(merchant_id)` — для JOIN с мерчантами

### Модуль скоринга (Требования 17, 18, 19)

**Компоненты:**
- `ScoringRouter` — GET /scoring/{ad_id}/explain
- `ScoringFacade` — единый интерфейс: score + explain (GoF: Facade)
- `ScoringStrategy` (ABC) → `RuleBasedScoring` — расчёт скора 1-10 (GoF: Strategy)
- `LLMExplainer` — генерация объяснений через OpenAI + кэш Redis (TTL 10 мин)
- `IntegralScoreCalculator` — комбинированный скор для дефолтной сортировки

**Формула риск-скора:**
```
raw = rating_norm * w1 + trades_norm * w2 + success_rate * w3 [+ speed_norm * w4]
risk_score = 11 - round(raw * 10)  # инверсия: хороший мерчант = низкий риск
```
- Нормализация trades: `min(log1p(trades) / log1p(10000), 1.0)`
- Нормализация speed: `1.0 - min(speed / 3600, 1.0)`
- При отсутствии speed: перераспределение w4 пропорционально

**Формула интегрального скора:**
```
integral = price_norm * w1 + (1 - risk_score/10) * w2 + profile_match * w3
```

### Модуль доходности (Требование 20)

**Компоненты:**
- `ProfitabilityService` — расчёт чистой доходности
- Встроен в AdvertisementRouter (не отдельный эндпоинт)

**Формула:**
```
net_yield = ((ref_price - ad_price) / ad_price - commission_pct) * 100
            - commission_fix / deal_amount * 100
```

### Модуль админки (Требования 23, 24)

**Компоненты:**
- `AdminRouter` — GET/PUT /admin/sources, GET /admin/monitoring
- `SourceManager` — включение/выключение валютных пар и источников
- `MonitoringService` — агрегация статусов (OK/Degraded/Down) и ошибок за 24ч

**Доступ:** только роль ADMIN (проверка через Depends)

### Health check (Требование 25)

- `GET /health` — проверка PostgreSQL, Redis, последний успешный поллинг MEXC
- Формат: `{"status": "ok|degraded|down", "dependencies": {...}}`

## Компоненты фронтенда

### Страницы

| Страница | Роут | Доступ | Описание |
|----------|------|--------|----------|
| LoginPage | /login | public | Вход и регистрация |
| DashboardPage | / | USER, ADMIN | Таблица объявлений + фильтры |
| ProfilePage | /profile | USER, ADMIN | Настройки профиля трейдера |
| AdminPage | /admin | ADMIN | Управление источниками + мониторинг |

### Ключевые компоненты

- `MainLayout` — шапка с ReadOnlyBadge, навигация, router-view
- `AdvertisementTable` — QTable с сортировкой, цветовой индикацией риск-скора
- `AdvertisementCard` — QDialog модалка с полными данными + кнопка «Открыть в MEXC»
- `FilterPanel` — фильтры по банкам, рейтингу, сделкам, сумме + кнопка «Сохранить»
- `RiskScoreBadge` — QBadge с цветом (positive/warning/negative) + иконка для LLM-объяснения
- `ProfitabilityTooltip` — QTooltip с детализацией расчёта доходности
- `ProfileForm` — форма профиля: банки, суммы, пара, риск-профиль, комиссии
- `SourceStatusPanel` — статусы источников для админки (OK/Degraded/Down)

### Интеграция с бэкендом (Orval)

Фронтенд НЕ пишет HTTP-запросы вручную. Orval генерирует из OpenAPI-схемы FastAPI:
- TypeScript-типы для всех request/response моделей
- vue-query хуки: `useGetAdvertisements`, `useGetProfile`, `usePostLogin` и т.д.
- Режим: `tags-split` (файлы по тегам OpenAPI)

### Состояния UI (Требование 16)

Каждый компонент с данными обрабатывает 4 состояния:
1. **Loading** — QSpinner или skeleton
2. **Data** — основной контент
3. **Empty** — «Нет объявлений, соответствующих фильтрам»
4. **Error** — сообщение + кнопка «Повторить»

## Схема базы данных

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│    users     │     │ trader_profiles  │     │  saved_filters  │
├──────────────┤     ├──────────────────┤     ├─────────────────┤
│ id (PK)      │◄───┤ user_id (FK)     │     │ user_id (FK)    │
│ email        │     │ payment_methods  │     │ filters_json    │
│ hashed_pass  │     │ min_amount       │     └─────────────────┘
│ role         │     │ max_amount       │
│ is_verified  │     │ currency_pair    │
│ created_at   │     │ risk_profile     │
└──────────────┘     │ commission_pct   │
                     │ commission_fix   │
                     └──────────────────┘

┌──────────────┐     ┌──────────────────┐
│  merchants   │     │ advertisements   │
├──────────────┤     ├──────────────────┤
│ id (PK)      │◄───┤ merchant_id (FK) │
│ external_id  │     │ id (PK)          │
│ name         │     │ external_id      │
│ rating       │     │ price            │
│ trades_count │     │ volume           │
│ success_rate │     │ min_limit        │
│ closing_speed│     │ max_limit        │
└──────────────┘     │ direction        │
                     │ currency         │
                     │ payment_methods  │
                     │ is_active        │
                     │ risk_score       │
                     │ risk_category    │
                     │ fetched_at       │
                     └──────────────────┘

┌──────────────────┐
│ polling_errors   │
├──────────────────┤
│ id (PK)          │
│ source           │
│ error_type       │
│ message          │
│ hour_bucket      │
│ created_at       │
└──────────────────┘
```

## API-эндпоинты

### Auth (`/api/v1/auth`)
| Метод | Путь | Описание |
|-------|------|----------|
| POST | /register | Регистрация |
| POST | /login | Вход |
| POST | /logout | Выход (все сессии) |
| GET | /verify-email/{token} | Подтверждение email |

### Profile (`/api/v1/profile`)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | / | Получить профиль |
| PUT | / | Обновить профиль |
| GET | /banks | Список доступных банков |
| GET | /filters | Получить сохранённые фильтры |
| PUT | /filters | Сохранить фильтры |

### Advertisements (`/api/v1/advertisements`)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | / | Список с фильтрами и сортировкой |
| GET | /{id} | Детали объявления (для карточки) |

### Scoring (`/api/v1/scoring`)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /{ad_id}/explain | LLM-объяснение риск-скора |

### Admin (`/api/v1/admin`)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /sources | Список источников и пар |
| PUT | /sources/{id} | Вкл/выкл источник или пару |
| GET | /monitoring | Статусы + ошибки за 24ч |

### System
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /health | Health check |
