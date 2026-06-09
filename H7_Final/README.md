# MEXC P2P Insight — Финальный проект

> **Курс OTUS «AI-разработка»** | Финальная проектная работа | H7_Final

MEXC P2P Insight — это веб-приложение для мониторинга и анализа P2P-объявлений на бирже MEXC. Агрегирует объявления в реальном времени, рассчитывает риск-скоринг по каждому мерчанту, поддерживает OAuth2-вход через Google и содержит полный DevOps-стек.

---

## Быстрый старт (docker compose)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Rustem81/otus.git
cd otus/H7_Final

# 2. Создать .env
cp .env.example .env
# Открыть .env и выставить SECRET_KEY (любая строка 32+ символа)

# 3. Запустить все сервисы
docker compose up -d

# 4. Убедиться что backend готов
curl http://localhost:8000/health
# → {"status":"ok","version":"1.0.0","dependencies":{"postgres":"ok","redis":"ok","mock_server":"ok"}}
```

| Сервис | URL | Описание |
|--------|-----|----------|
| Frontend | http://localhost:3000 | React приложение |
| Backend API | http://localhost:8000/docs | Swagger UI |
| Grafana | http://localhost:3001 | Метрики (admin/admin) |
| Prometheus | http://localhost:9090 | Scrape targets |

### Тестовые аккаунты

| Email | Пароль | Роль |
|-------|--------|------|
| `test@test.com` | `test123456` | user |
| `admin@test.com` | `admin123456` | admin |

---

## Описание проекта

### Идея

P2P-трейдеры на MEXC тратят время на ручной просмотр десятков объявлений. Приложение агрегирует их в одном месте, сортирует по выгодности и показывает риск-оценку каждого мерчанта на основе его истории.

### Ключевые возможности

- **Живая лента объявлений** — polling каждые 10 секунд, BUY/SELL направления, фильтрация по банкам
- **Риск-скоринг** — алгоритм на основе рейтинга (30%), числа сделок (25%), процента успеха (30%), скорости ответа (15%)
- **Блокировка мерчантов** — персональный черный список, который скрывает объявления нежелательных продавцов
- **История просмотров** — трекинг просмотренных объявлений
- **Google OAuth** — вход через Google-аккаунт без пароля
- **Профиль трейдера** — настройка предпочтительных банков, лимитов, уровня KYC
- **Мониторинг** — Prometheus + Grafana, /health endpoint, structured logging

### Скриншоты

> Добавьте скриншоты в папку `screenshots/` после запуска

| Экран | Описание |
|-------|----------|
| Лента объявлений | Главная страница с картами объявлений |
| Детали объявления | Диалог с подробной информацией о мерчанте |
| Профиль | Настройки трейдера |
| Grafana | Dashboard с метриками приложения |
| CI/CD | GitHub Actions зелёный |

---

## Технологии

| Слой | Стек |
|------|------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Alembic, Redis |
| **Frontend** | React 19, TypeScript, Vite, Zustand, TanStack Query, shadcn/ui |
| **База данных** | PostgreSQL 16 |
| **Кеш / Сессии** | Redis 7 |
| **Мониторинг** | Prometheus, Grafana, structlog (JSON), X-Request-ID |
| **CI/CD** | GitHub Actions (lint, test, audit, smoke-test) |
| **Безопасность** | OWASP audit, CSRF, rate limiting, HttpOnly cookies, security headers |
| **Интеграции** | Google OAuth2, Яндекс.Метрика, Sentry (optional) |

### Схема базы данных

```
users ──────────┐
  id, email     │
  oauth_*       │
                ▼
         trader_profile     saved_filters
         (payment methods,  (filter config)
          risk profile)

merchants ──────┐
  id, name      │
  rating, trades│
                ▼
         advertisements
         (price, volume,
          direction, risk_score)
                ▼
         view_history
         (user_id, ad_id)

merchant_blacklist
  (user_id, merchant_id)
```

---

## Структура проекта

```
H7_Final/
├── backend/               # FastAPI API
│   ├── app/
│   │   ├── api/v1/        # Endpoints: auth, ads, profile, blacklist, scoring, admin
│   │   ├── core/          # Config, DB, Redis, logging, metrics
│   │   ├── middleware/    # CSRF, RateLimit, RequestID, SecurityHeaders
│   │   ├── models/        # SQLAlchemy: User, Merchant, Advertisement, ...
│   │   ├── repositories/  # Data access layer
│   │   ├── services/      # Auth, OAuth, P2P polling, scoring
│   │   └── tasks/         # Background polling task
│   ├── alembic/           # DB migrations
│   ├── tests/             # pytest
│   └── Dockerfile
├── frontend/              # React SPA
│   ├── src/
│   │   ├── components/    # UI: AdCard, AdDetailDialog, RiskIndicator, ...
│   │   ├── pages/         # Login, Main, Profile, Blacklist, History, Admin
│   │   ├── lib/           # API client, analytics, utils
│   │   └── stores/        # Zustand auth store
│   └── Dockerfile
├── mock-server/           # FastAPI P2P data emulator
├── monitoring/            # Prometheus config + Grafana provisioning
├── docker-compose.yml     # Полный локальный стек (7 сервисов)
├── .env.example           # Шаблон переменных окружения
└── README.md              # Этот файл
```

---

## API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/login` | Вход |
| GET | `/api/v1/auth/google` | OAuth2 Google redirect |
| GET | `/api/v1/advertisements` | Список объявлений (фильтры: currency, direction) |
| GET | `/api/v1/scoring/{ad_id}/risk` | Риск-скоринг объявления |
| GET/PUT | `/api/v1/profile/` | Профиль трейдера |
| GET/POST/DELETE | `/api/v1/blacklist` | Черный список мерчантов |
| GET | `/health` | Health check (postgres, redis, mock-server) |
| GET | `/metrics` | Prometheus метрики |

Полная документация: http://localhost:8000/docs (Swagger UI)

---

## Переменные окружения

```env
# Обязательные
DATABASE_URL=postgresql+asyncpg://mexc:mexc_secret@postgres:5432/mexc_p2p
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-min-32-chars

# Опциональные
GOOGLE_CLIENT_ID=          # Google OAuth2
GOOGLE_CLIENT_SECRET=
VITE_YM_COUNTER_ID=        # Яндекс.Метрика
SENTRY_DSN_BACKEND=        # Sentry
```

---

## Использование AI в разработке

Подробная документация: [AI_PROCESS.md](./AI_PROCESS.md)

### Краткая таблица

| Этап | Инструмент | Что сделал AI |
|------|-----------|---------------|
| Архитектура БД | Kiro | Схема таблиц, миграции Alembic |
| Backend API | Kiro | Все endpoints, сервисы, репозитории |
| Frontend компоненты | Kiro | Все страницы и компоненты |
| OAuth2 Google | Kiro | Полный flow (backend + frontend) |
| CI/CD | Kiro | GitHub Actions workflows |
| Аудит безопасности | Kiro | OWASP-анализ, патчи (21 находка) |
| Prometheus + Grafana | Kiro | Auto-provisioned dashboard |
| Документация | Kiro | Все MD-файлы |

---

## CI/CD

```
Push/PR → GitHub Actions (h6-ci.yml) → lint + test + audit
Push main → Railway autodeploy → build + migrate + start
Push main → GitHub Actions (h6-deploy.yml) → smoke-test /health
```

Workflows: `.github/workflows/h6-ci.yml`, `.github/workflows/h6-deploy.yml`

---

## Лицензия

MIT — учебный проект курса OTUS «AI-разработка»
