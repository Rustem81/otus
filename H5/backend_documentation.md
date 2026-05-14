# Документация Backend: MEXC P2P Агрегатор

**Курс:** OTUS — AI для разработчиков
**Задание:** H5 — Развертывание Backend и интеграция с Frontend
**Проект:** MEXC P2P Агрегатор (продолжение H2–H4)
**Дата:** Май 2026

---

## 1. Архитектура решения

### 1.1. Общая схема

```mermaid
graph LR
    subgraph Docker Compose
        Frontend["Frontend<br/>(React :3000)"]
        Backend["Backend<br/>(FastAPI :8000)"]
        Postgres["PostgreSQL 16<br/>(:5432)"]
        Redis["Redis 7<br/>(:6379)"]
        Mock["Mock Server<br/>(P2P data :8001)"]
    end

    Frontend -->|"/api/* proxy"| Backend
    Backend -->|"SQLAlchemy async"| Postgres
    Backend -->|"Сессии, кэш LLM"| Redis
    Backend -->|"Polling каждые 10s"| Mock
```

### 1.2. Выбор инфраструктурного решения: Self-hosted vs Supabase

| Критерий | Supabase (BaaS) | Self-hosted (Docker) |
|----------|----------------|---------------------|
| Server-side polling (asyncio tasks) | ❌ Невозможно | ✅ Полный контроль |
| Кастомная бизнес-логика (scoring, profitability) | ❌ Только Edge Functions | ✅ Любая логика |
| LLM-интеграция (OpenAI) | ⚠️ Через Edge Functions | ✅ Нативно в сервисах |
| Redis-кэширование | ❌ Нет встроенного | ✅ Redis 7 |
| Rate limiting на уровне API | ❌ Ограниченно | ✅ Кастомный middleware |
| Стоимость при масштабировании | 💰 Растёт с объёмом | 💰 Фиксированная VPS |
| Скорость старта (MVP) | ✅ Быстрее | ⚠️ Требует настройки |
| Row Level Security | ✅ Встроенный | ⚠️ Реализуется middleware |

**Выбор: Self-hosted (PostgreSQL + Redis в Docker)**

**Обоснование:** Проект MEXC P2P Агрегатор требует:
1. **Server-side polling** — фоновые asyncio-задачи опрашивают источник P2P-данных каждые 10 секунд. Supabase не поддерживает long-running background tasks.
2. **Вычислительная логика** — risk-scoring с формулой нормализации, расчёт чистой доходности, интегральный скор. Это не простой CRUD.
3. **LLM-интеграция** — кэширование объяснений в Redis с TTL, graceful degradation при недоступности OpenAI.
4. **Rate limiting** — централизованный контроль запросов к внешнему API на уровне бэкенда.

Supabase подходит для CRUD-приложений с простой авторизацией. Для проекта с серверной логикой, фоновыми задачами и внешними интеграциями — self-hosted решение оптимально.

### 1.3. Технологический стек

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Backend API | FastAPI | 0.115+ |
| ORM | SQLAlchemy 2 (async) | 2.0+ |
| Миграции | Alembic | 1.13+ |
| БД | PostgreSQL | 16 |
| Кэш / Сессии | Redis | 7 |
| Контейнеризация | Docker + Docker Compose | 24+ |
| Python | CPython | 3.12 |
| Аутентификация | bcrypt + JWT-сессии в Redis | — |
| LLM | OpenAI API (GPT-4o-mini) | — |
| Frontend | React 19 + TypeScript + Tailwind CSS 4 | — |

### 1.4. Архитектура бэкенда (трёхслойная)

```mermaid
graph TD
    A["API Layer<br/>(FastAPI Routers)"] -->|"Depends()"| B["Service Layer<br/>(бизнес-логика)"]
    B --> C["Repository Layer<br/>(SQLAlchemy queries)"]
    C --> D[("PostgreSQL")]

    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#9C27B0,color:#fff
```

- **API Layer** — валидация входных данных (Pydantic), маршрутизация, HTTP-ответы
- **Service Layer** — бизнес-логика: scoring, profitability, auth, polling
- **Repository Layer** — SQL-запросы через SQLAlchemy async

---

## 2. Проектирование базы данных

### 2.1. ER-диаграмма

```mermaid
erDiagram
    users ||--o| trader_profiles : "has"
    users ||--o| saved_filters : "has"
    users ||--o{ merchant_blacklist : "blocks"
    users ||--o{ view_history : "views"
    merchants ||--o{ advertisements : "publishes"
    merchants ||--o{ merchant_blacklist : "blocked_by"
    advertisements ||--o{ view_history : "viewed_in"

    users {
        string id PK
        string email UK
        string hashed_password
        string role "USER | ADMIN"
        boolean is_verified
        boolean onboarding_completed
        datetime created_at
    }

    merchants {
        string id PK
        string external_id UK
        string name
        float rating "0-5"
        int trades_count
        float success_rate "0-1"
        float closing_speed "seconds"
        boolean is_verified
        datetime updated_at
    }

    advertisements {
        string id PK
        string external_id UK
        decimal price
        decimal volume
        decimal min_limit
        decimal max_limit
        string direction "BUY | SELL"
        string currency
        array payment_methods
        boolean is_active
        int risk_score "1-10"
        string risk_category "low|medium|high"
        string merchant_id FK
        datetime fetched_at
    }

    trader_profiles {
        int id PK
        string user_id FK
        array payment_methods
        decimal min_amount
        decimal max_amount
        string currency_pair
        string risk_profile "low|medium|high"
        decimal commission_percent
        decimal commission_fixed
        string kyc_level
        string country
    }

    saved_filters {
        int id PK
        string user_id FK
        jsonb filters_json
    }

    merchant_blacklist {
        int id PK
        string user_id FK
        string merchant_id FK
        datetime created_at
    }

    view_history {
        int id PK
        string user_id FK
        string advertisement_id FK
        datetime viewed_at
    }

    polling_errors {
        int id PK
        string source
        string error_type
        text message
        datetime hour_bucket
        datetime created_at
    }
```

### 2.2. Таблицы и связи

| Таблица | Назначение | Связи |
|---------|-----------|-------|
| `users` | Пользователи системы | 1:1 → trader_profiles, 1:1 → saved_filters |
| `merchants` | Мерчанты P2P-биржи | 1:N → advertisements |
| `advertisements` | P2P-объявления | N:1 → merchants |
| `trader_profiles` | Настройки трейдера | N:1 → users |
| `saved_filters` | Сохранённые фильтры (JSONB) | N:1 → users |
| `merchant_blacklist` | Чёрный список мерчантов | N:1 → users, N:1 → merchants |
| `view_history` | История просмотров | N:1 → users, N:1 → advertisements |
| `polling_errors` | Логи ошибок интеграции | — |

### 2.3. Индексы

```sql
-- Быстрый поиск активных объявлений по валюте и направлению
CREATE INDEX ix_ads_currency_direction_active ON advertisements(currency, direction, is_active);

-- Сортировка по времени получения
CREATE INDEX ix_ads_fetched_at ON advertisements(fetched_at);

-- Поиск объявлений мерчанта
CREATE INDEX ix_ads_merchant_id ON advertisements(merchant_id);

-- История просмотров пользователя
CREATE INDEX ix_view_history_user_id ON view_history(user_id);
```

### 2.4. Использование AI для проектирования БД

**Промпт для генерации схемы:**
```
Role: Database Architect, специалист по PostgreSQL.

Task: Спроектировать схему БД для P2P-агрегатора. Сущности:
- Пользователи (email auth, роли USER/ADMIN)
- Мерчанты (рейтинг, число сделок, скорость)
- Объявления (цена, лимиты, направление BUY/SELL, способы оплаты)
- Профиль трейдера (банки, суммы, риск-профиль, комиссии)
- Чёрный список мерчантов
- История просмотров

Context:
- PostgreSQL 16, SQLAlchemy 2 async
- Объявления обновляются каждые 10 сек (server-side polling)
- Нужны индексы для фильтрации по currency+direction+is_active
- payment_methods — массив строк (ARRAY)
- Сохранённые фильтры — произвольный JSON (JSONB)

Format: SQLAlchemy модели с типизацией Mapped[], индексы, комментарии.
```

AI сгенерировал базовую схему, которая была скорректирована:
- Добавлен `external_id` для дедупликации объявлений при polling
- Добавлен `hour_bucket` в polling_errors для агрегации по часам
- Изменён тип `payment_methods` с JSON на `ARRAY(String)` для эффективного поиска
- Добавлен составной индекс `ix_ads_currency_direction_active`

---

## 3. Развертывание

### 3.1. Предварительные требования

- Docker 24+ и Docker Compose v2
- 2 GB RAM минимум
- Порты: 3000 (frontend), 8000 (backend), 5432 (postgres), 6379 (redis), 8001 (mock-server)

### 3.2. Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd H5

# 2. Создать .env из примера
cp .env.example .env

# 3. Запустить весь стек
docker compose up -d

# 4. Проверить статус
docker compose ps

# 5. Открыть приложение
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

### 3.3. Что происходит при запуске

```mermaid
graph TD
    A[docker compose up] --> B[PostgreSQL starts]
    A --> C[Redis starts]
    A --> D[Mock-server starts]
    B -->|healthcheck OK| E[Migrations: alembic upgrade head]
    C -->|healthcheck OK| F[Backend waits...]
    D -->|healthcheck OK| F
    E -->|completed| F
    F --> G[Backend starts + polling task]
    G -->|healthcheck OK| H[Frontend starts nginx]

    style A fill:#333,color:#fff
    style G fill:#4CAF50,color:#fff
    style H fill:#2196F3,color:#fff
```

### 3.4. Тестовые учётные записи

| Email | Пароль | Роль |
|-------|--------|------|
| test@test.com | test123456 | USER |
| admin@test.com | admin1234 | ADMIN |

### 3.5. Переменные окружения (.env)

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `DATABASE_URL` | Строка подключения PostgreSQL | `postgresql+asyncpg://mexc:mexc_secret@postgres:5432/mexc_p2p` |
| `REDIS_URL` | Строка подключения Redis | `redis://redis:6379` |
| `SECRET_KEY` | Секрет для JWT-сессий | `change-me-in-production` |
| `BACKEND_CORS_ORIGINS` | Разрешённые origins для CORS | `http://localhost:3000` |
| `P2P_DATA_SOURCE` | Источник данных (mock/p2p_army) | `mock` |
| `POLLING_INTERVAL_SEC` | Интервал polling (секунды) | `10` |
| `OPENAI_API_KEY` | Ключ OpenAI для LLM-объяснений | — |
| `SCORING_WEIGHT_*` | Веса факторов скоринга | 0.3/0.25/0.3/0.15 |

---

## 4. API Endpoints

### 4.1. Аутентификация (`/api/v1/auth`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| POST | `/api/v1/auth/register` | Регистрация нового пользователя | ❌ |
| POST | `/api/v1/auth/login` | Вход (возвращает access_token) | ❌ |
| POST | `/api/v1/auth/logout` | Выход (инвалидация сессии) | ✅ |
| GET | `/api/v1/auth/me` | Текущий пользователь | ✅ |
| GET | `/api/v1/auth/verify-email/{token}` | Подтверждение email | ❌ |


#### Пример: Регистрация

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword123"}'
```

Ответ (201):
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "user@example.com"
}
```

#### Пример: Вход

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test123456"}'
```

Ответ (200):
```json
{
  "user": {
    "id": "test-user-001",
    "email": "test@test.com",
    "role": "USER",
    "is_verified": true,
    "onboarding_completed": true
  },
  "access_token": "session-token-uuid..."
}
```

### 4.2. Объявления (`/api/v1/advertisements`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/api/v1/advertisements` | Список объявлений с фильтрацией | ✅ |
| GET | `/api/v1/advertisements/{id}` | Детали объявления | ✅ |

**Query-параметры GET /advertisements:**

| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|-------------|
| `currency` | string | Валюта | RUB |
| `direction` | BUY/SELL | Направление | — |
| `payment_methods` | string[] | Фильтр по банкам | — |
| `min_amount` | float | Минимальная сумма | — |
| `max_amount` | float | Максимальная сумма | — |
| `sort_by` | string | Поле сортировки | integral_score |
| `sort_order` | asc/desc | Порядок | desc |
| `limit` | int | Лимит результатов | 200 |

#### Пример: Получение объявлений

```bash
curl -X GET "http://localhost:8000/api/v1/advertisements?currency=RUB&direction=BUY&limit=10" \
  -H "Authorization: Bearer <access_token>"
```

Ответ (200):
```json
{
  "items": [
    {
      "id": "ad-uuid-001",
      "price": 95.50,
      "volume": 10000.0,
      "min_limit": 5000.0,
      "max_limit": 50000.0,
      "direction": "BUY",
      "currency": "RUB",
      "payment_methods": ["Sberbank", "Tinkoff"],
      "is_active": true,
      "risk_score": 3,
      "risk_category": "low",
      "net_yield": 1.25,
      "spread": -0.5,
      "merchant": {
        "id": "merchant-uuid-001",
        "name": "CryptoTrader",
        "rating": 4.5,
        "trades_count": 1200,
        "success_rate": 0.98,
        "is_verified": true
      }
    }
  ],
  "total": 15,
  "reference_price": 96.0,
  "last_updated": "2026-05-14T10:30:00Z"
}
```

### 4.3. Профиль трейдера (`/api/v1/profile`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/api/v1/profile/` | Получить профиль | ✅ |
| PUT | `/api/v1/profile/` | Обновить профиль | ✅ |
| GET | `/api/v1/profile/banks` | Список доступных банков | ✅ |
| GET | `/api/v1/profile/filters` | Сохранённые фильтры | ✅ |
| PUT | `/api/v1/profile/filters` | Обновить фильтры | ✅ |
| POST | `/api/v1/profile/onboarding` | Завершить онбординг | ✅ |

#### Пример: Обновление профиля

```bash
curl -X PUT http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_methods": ["Sberbank", "Tinkoff", "SBP"],
    "min_amount": 10000,
    "max_amount": 100000,
    "risk_profile": "medium",
    "commission_percent": 0.5
  }'
```

### 4.4. Риск-скоринг (`/api/v1/scoring`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/api/v1/scoring/{merchant_id}/explain` | LLM-объяснение риск-скора | ✅ |

#### Пример: Получение объяснения

```bash
curl -X GET http://localhost:8000/api/v1/scoring/merchant-uuid-001/explain \
  -H "Authorization: Bearer <token>"
```

Ответ (200):
```json
{
  "merchant_id": "merchant-uuid-001",
  "merchant_name": "CryptoTrader",
  "risk_score": 3,
  "risk_category": "low",
  "explanation": "Мерчант имеет высокий рейтинг 4.5/5, более 1200 успешных сделок с процентом успеха 98%. Скорость закрытия сделок выше среднего. Риск минимальный."
}
```

### 4.5. Чёрный список (`/api/v1/blacklist`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/api/v1/blacklist` | Список заблокированных мерчантов | ✅ |
| POST | `/api/v1/blacklist` | Добавить в чёрный список | ✅ |
| DELETE | `/api/v1/blacklist/{merchant_id}` | Удалить из чёрного списка | ✅ |

### 4.6. История просмотров (`/api/v1/history`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/api/v1/history` | Последние 50 просмотров | ✅ |
| POST | `/api/v1/history` | Записать просмотр | ✅ |

### 4.7. Администрирование (`/api/v1/admin`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/api/v1/admin/sources` | Статусы источников данных | ✅ ADMIN |
| PUT | `/api/v1/admin/sources/{id}` | Вкл/выкл источник | ✅ ADMIN |
| GET | `/api/v1/admin/monitoring` | Мониторинг за 24 часа | ✅ ADMIN |
| GET | `/api/v1/admin/errors` | Статистика ошибок | ✅ ADMIN |

### 4.8. Health Check

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| GET | `/health` | Статус PostgreSQL и Redis | ❌ |

```bash
curl http://localhost:8000/health
```

Ответ:
```json
{
  "status": "ok",
  "dependencies": {
    "postgres": "ok",
    "redis": "ok"
  }
}
```

---

## 5. Безопасность

### 5.1. Аутентификация

- **Хеширование паролей:** bcrypt (cost factor 12)
- **Сессии:** UUID-токены хранятся в Redis с TTL (24 часа по умолчанию)
- **Передача токена:** Header `Authorization: Bearer <token>`
- **Автопродление:** TTL сессии обновляется при каждом запросе

### 5.2. Авторизация (RBAC)

Реализована через middleware `RoleChecker`:

```python
class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(403, "Insufficient permissions")
        return user
```

- `require_user` — доступ для USER и ADMIN
- `require_admin` — доступ только для ADMIN

### 5.3. CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # из .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.4. Rate Limiting

Кастомный middleware ограничивает количество запросов по IP:
- Хранение счётчиков в Redis
- Настраиваемые лимиты по эндпоинтам

### 5.5. CSRF Protection

Middleware генерирует и проверяет CSRF-токены для мутирующих запросов.

### 5.6. Защита секретов

- Все секреты в `.env` (не в коде)
- `.env` добавлен в `.gitignore`
- `.env.example` содержит шаблон без реальных значений
- Docker Compose читает переменные из `.env` через `env_file`

---

## 6. Интеграция Frontend с Backend

### 6.1. API-клиент (Frontend)

Frontend использует единый модуль `lib/api.ts`:

```typescript
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { ...getHeaders(), ...init?.headers },
  });
  if (res.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Ошибка сервера" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}
```

### 6.2. State Management (Zustand)

Авторизация управляется через Zustand store:

```typescript
export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem("access_token"),
  login: async (email, password) => { /* POST /api/v1/auth/login */ },
  register: async (email, password) => { /* POST /api/v1/auth/register */ },
  logout: () => { /* POST /api/v1/auth/logout + clear localStorage */ },
  fetchUser: async () => { /* GET /api/v1/auth/me */ },
}));
```

### 6.3. Маппинг страниц на API

| Страница | API-вызовы |
|----------|-----------|
| LoginPage | POST /auth/login, POST /auth/register |
| OnboardingPage | POST /profile/onboarding |
| MainPage | GET /advertisements (auto-refresh 15s), POST /blacklist, POST /history |
| ProfilePage | GET /profile, PUT /profile, GET /profile/banks |
| HistoryPage | GET /history |
| BlacklistPage | GET /blacklist, DELETE /blacklist/{id} |
| AdminPage | GET /health, GET /admin/errors |

### 6.4. Обработка ошибок на Frontend

Каждая страница обрабатывает 3 состояния:
1. **Loading** — спиннер
2. **Error** — сообщение + кнопка retry
3. **Empty** — иконка + текст + действие

Глобальная обработка 401 — автоматический редирект на `/login`.

---

## 7. Обработка ошибок и логирование

### 7.1. Backend — обработка ошибок

```python
class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

@app.exception_handler(AppException)
async def app_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "detail": exc.detail},
    )
```

### 7.2. Категории ошибок

| HTTP Code | Ситуация | Обработка |
|-----------|----------|-----------|
| 400 | Невалидные данные | Pydantic validation → detail с описанием |
| 401 | Не аутентифицирован | Redirect на login (frontend) |
| 403 | Нет прав (не ADMIN) | Сообщение "Insufficient permissions" |
| 404 | Ресурс не найден | "Advertisement/Merchant not found" |
| 409 | Конфликт (дубликат) | "Merchant already blacklisted" |
| 429 | Rate limit | "Too many requests" |
| 500 | Внутренняя ошибка | Логируется, возвращается generic message |

### 7.3. Логирование

- **Уровень:** INFO для запросов, ERROR для 5xx и ошибок интеграций
- **Формат:** structlog-совместимый (timestamp, level, message, context)
- **Polling errors:** записываются в таблицу `polling_errors` с агрегацией по часам
- **Доступ к логам:** `docker compose logs backend` или через админ-панель (GET /admin/errors)

### 7.4. Graceful Degradation

| Компонент | При недоступности |
|-----------|------------------|
| LLM (OpenAI) | Числовой скор без объяснения |
| Redis | Fallback на прямые запросы к БД |
| Mock-server | Последние данные + баннер "Данные устарели" |

---

## 8. Тестирование

### 8.1. Backend — тестирование API

```bash
# Запуск тестов бэкенда
docker compose exec backend pytest -v

# Или локально
cd backend && pytest -v
```

### 8.2. Frontend — тестирование компонентов

```bash
cd frontend && npm run test
```

Результат: 23 теста, 4 файла — все проходят.

### 8.3. Ручное тестирование API (curl)

```bash
# 1. Логин
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123456"}' | jq -r '.access_token')

# 2. Получить объявления
curl -s http://localhost:8000/api/v1/advertisements?direction=BUY \
  -H "Authorization: Bearer $TOKEN" | jq '.total'

# 3. Добавить в чёрный список
curl -X POST http://localhost:8000/api/v1/blacklist \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"merchant_id": "merchant-uuid-001"}'

# 4. Проверить health
curl http://localhost:8000/health | jq
```

### 8.4. Использование AI для отладки

При разработке AI-агент (Kiro) использовался для:
- Диагностики ошибок SQLAlchemy (async session management)
- Исправления race condition в polling-задаче
- Анализа логов 5xx ошибок
- Оптимизации SQL-запросов (добавление индексов)

---

## 9. Миграции базы данных

### 9.1. Структура миграций

```
backend/alembic/versions/
├── 96090f785ff2_initial_migration.py      # Таблицы: users, merchants, advertisements, trader_profiles, saved_filters, polling_errors
├── 5f99c66f9127_seed_test_user.py         # Seed: test@test.com, admin@test.com
└── a1b2c3d4e5f6_add_v11_features.py       # Таблицы: merchant_blacklist, view_history + поля onboarding, KYC
```

### 9.2. Команды

```bash
# Применить все миграции
docker compose exec backend alembic upgrade head

# Откатить последнюю
docker compose exec backend alembic downgrade -1

# Создать новую миграцию
docker compose exec backend alembic revision --autogenerate -m "description"

# Посмотреть текущую версию
docker compose exec backend alembic current
```

---

## 10. Процесс разработки с AI

### 10.1. Sequence-диаграмма: Аутентификация и загрузка данных

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant F as Frontend (React)
    participant B as Backend (FastAPI)
    participant R as Redis
    participant DB as PostgreSQL

    U->>F: Открывает /login
    U->>F: Вводит email + password
    F->>B: POST /api/v1/auth/login
    B->>DB: SELECT user WHERE email=...
    B->>B: bcrypt.verify(password)
    B->>R: SET session:{uuid} → user_id (TTL 24h)
    B-->>F: {access_token, user}
    F->>F: localStorage.set("access_token")
    F->>F: redirect → /

    U->>F: Открывает главную
    F->>B: GET /api/v1/advertisements (Bearer token)
    B->>R: GET session:{token} → user_id
    B->>R: EXPIRE session:{token} (extend TTL)
    B->>DB: SELECT ads WHERE is_active=true
    B->>B: Calculate risk_score, net_yield, spread
    B-->>F: {items: [...], total, reference_price}
    F->>F: Render AdCards
```

### 10.2. Sequence-диаграмма: Polling и обновление данных

```mermaid
sequenceDiagram
    participant T as Polling Task (asyncio)
    participant M as Mock Server (:8001)
    participant DB as PostgreSQL
    participant B as Backend API

    loop Каждые 10 секунд
        T->>M: GET /v1/api/advertisements
        M-->>T: [{merchant, price, volume, ...}]
        T->>DB: UPSERT merchants (by external_id)
        T->>DB: UPSERT advertisements (by external_id)
        T->>DB: UPDATE is_active=false (stale ads > 15s)
    end

    Note over T,DB: При ошибке → INSERT polling_errors
```

### 10.3. Инструменты

- **Kiro** — основной AI-агент (IDE с spec-driven workflow)
- **Steering-файлы** — правила проекта для AI (`.kiro/steering/`)
- **Скиллы** — пакеты знаний (fastapi-templates, gof-design-patterns)

### 10.2. Примеры использования AI

**Проектирование БД:**
> "Спроектируй схему PostgreSQL для P2P-агрегатора с таблицами: users, merchants, advertisements, trader_profiles. Используй SQLAlchemy 2 async, Mapped[] типизацию, индексы для фильтрации по currency+direction+is_active."

**Генерация API:**
> "Создай эндпоинт GET /api/v1/advertisements с фильтрацией по currency, direction, payment_methods, min/max amount. Сортировка по price, risk_score, net_yield. Используй Depends() для auth и DB session."

**Отладка:**
> "Ошибка: sqlalchemy.exc.MissingGreenlet при обращении к ad.merchant в цикле. Как исправить?"
> → AI предложил `selectinload(Advertisement.merchant)` в запросе.

**Оптимизация:**
> "Запрос GET /advertisements занимает 2 секунды при 500 объявлениях. Как ускорить?"
> → AI предложил составной индекс и eager loading связей.

### 10.3. Эффективность

| Этап | Без AI | С AI |
|------|--------|------|
| Проектирование БД | 4-6 часов | 1-2 часа |
| Генерация API endpoints | 8-12 часов | 3-4 часа |
| Настройка Docker Compose | 2-3 часа | 30 мин |
| Отладка интеграции | 4-6 часов | 1-2 часа |

---

## 11. Заключение

Реализован полноценный fullstack-проект с self-hosted инфраструктурой:
- **8 таблиц** PostgreSQL с миграциями Alembic
- **20+ API endpoints** (7 модулей: auth, profile, advertisements, scoring, blacklist, history, admin)
- **Безопасность:** bcrypt + JWT-сессии + RBAC + CORS + CSRF + rate limiting
- **Frontend:** React 19 + TypeScript + Tailwind CSS 4, интегрирован с Backend через REST API
- **DevOps:** Docker Compose поднимает весь стек одной командой
- **Мониторинг:** health check, логирование ошибок, админ-панель

Выбор self-hosted обоснован требованиями проекта: server-side polling, вычислительная логика скоринга, LLM-интеграция с кэшированием — функциональность, недоступная в BaaS-решениях типа Supabase.

---

## 12. Скриншоты работающего приложения

> **Инструкция:** Вставьте скриншоты после запуска `docker compose up -d` и проверки end-to-end работы.

### 12.1. Docker Compose — все сервисы запущены

<!-- Скриншот: результат `docker compose ps` — все сервисы в статусе healthy/running -->
![Docker Compose PS](screenshots/docker-compose-ps.png)

### 12.2. Health Check — Backend доступен

<!-- Скриншот: curl http://localhost:8000/health или браузер с JSON-ответом -->
![Health Check](screenshots/health-check.png)

### 12.3. Swagger UI — документация API

<!-- Скриншот: http://localhost:8000/docs — Swagger UI с эндпоинтами -->
![Swagger UI](screenshots/swagger-ui.png)

### 12.4. Frontend — страница логина

<!-- Скриншот: http://localhost:3000/login — форма входа -->
![Login Page](screenshots/login-page.png)

### 12.5. Frontend — главная с реальными данными

<!-- Скриншот: http://localhost:3000/ — карточки объявлений, загруженные с backend -->
![Main Page with Data](screenshots/main-page-data.png)

### 12.6. Frontend — профиль трейдера

<!-- Скриншот: http://localhost:3000/profile — настройки профиля -->
![Profile Page](screenshots/profile-page.png)

### 12.7. Frontend — панель администратора

<!-- Скриншот: http://localhost:3000/admin (логин admin@test.com) — health-статусы -->
![Admin Panel](screenshots/admin-panel.png)

### 12.8. API-запрос — получение объявлений

<!-- Скриншот: http://localhost:8000/docs → GET /api/v1/advertisements → Try it out → Execute → ответ с данными -->
![API Response](screenshots/api-response.png)
