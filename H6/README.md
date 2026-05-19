# MEXC P2P Insight — H6: CI/CD и интеграция сервисов

Домашнее задание H6 курса OTUS. Проект агрегации P2P-объявлений MEXC с CI/CD, OAuth2, аналитикой и мониторингом.

## Ссылки

| Ресурс | URL |
|--------|-----|
| Репозиторий | https://github.com/Rustem81/otus/tree/main/H6 |
| Frontend (prod) | <!-- TODO: вставить Railway URL --> `https://<frontend>.up.railway.app` |
| Backend API (prod) | <!-- TODO: вставить Railway URL --> `https://<backend>.up.railway.app` |
| Swagger UI | <!-- TODO: вставить Railway URL --> `https://<backend>.up.railway.app/docs` |
| Health Check | <!-- TODO: вставить Railway URL --> `https://<backend>.up.railway.app/health` |
| UptimeRobot | <!-- TODO: вставить UptimeRobot URL --> `https://stats.uptimerobot.com/...` |
| GitHub Actions | https://github.com/Rustem81/otus/actions |

> **Примечание:** После настройки Railway замените `<frontend>` и `<backend>` на реальные поддомены.

## Структура проекта

```
H6/
├── backend/              # FastAPI backend (Python 3.11)
│   ├── app/
│   │   ├── api/v1/      # REST endpoints (ads, auth, health, blacklist)
│   │   ├── core/        # Config, DB, Redis, Security, Logging
│   │   ├── middleware/   # CSRF, Rate Limiter, Request ID
│   │   ├── models/      # SQLAlchemy models
│   │   ├── repositories/ # Data access layer
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic (OAuth, polling)
│   │   └── tasks/       # Background polling
│   ├── alembic/         # Database migrations
│   ├── tests/           # pytest tests
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/             # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/  # UI components (shadcn/ui)
│   │   ├── pages/       # Route pages (login, ads, auth-callback)
│   │   ├── lib/         # API client, analytics, utilities
│   │   └── stores/      # Zustand state
│   ├── Dockerfile
│   └── package.json
│
├── mock-server/          # FastAPI mock P2P API
│   ├── app/
│   ├── Dockerfile
│   └── pyproject.toml
│
├── monitoring/           # Prometheus + Grafana (optional, local only)
│   ├── prometheus/
│   └── grafana/
│
├── docker-compose.yml    # Local development stack
├── .env.example          # Environment variables template
├── security_audit.md     # OWASP security audit report
├── integration_documentation.md  # Integration docs (подробно)
└── README.md             # This file
```

## Быстрый старт

### Предварительные требования

- Docker & Docker Compose v2+
- Git
- (Для OAuth) Google Cloud Console credentials

### Запуск локально

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Rustem81/otus.git
cd otus/H6

# 2. Создать .env из шаблона
cp .env.example .env
# Заполнить SECRET_KEY:
#   echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# 3. Запустить все сервисы
docker compose up -d

# 4. Проверить backend
curl http://localhost:8000/health
# → {"status":"ok","version":"1.0.0","dependencies":{"postgres":"ok","redis":"ok","mock_server":"ok"}}

# 5. Открыть в браузере
# Frontend:    http://localhost:3000
# Backend API: http://localhost:8000/docs (Swagger)
# Mock Server: http://localhost:8001 (internal)
```

### Тестовые аккаунты

| Email | Пароль | Роль |
|-------|--------|------|
| `test@example.com` | `TestPassword123!` | user |
| `admin@example.com` | `AdminPassword123!` | admin |

> Аккаунты создаются при первом запуске через seed-данные. Также можно войти через Google OAuth.

### Запуск тестов

```bash
# Backend
cd H6/backend
pip install -e ".[dev]"
pytest

# Frontend
cd H6/frontend
npm ci
npm run test -- --run
```

## Переменные окружения

### Backend

| Переменная | Обязательная | Описание | Пример / Default |
|------------|:---:|----------|------------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `REDIS_URL` | ✅ | Redis connection string | `redis://redis:6379` |
| `SECRET_KEY` | ✅ | Секрет для JWT/sessions (min 32 chars) | `openssl rand -hex 32` |
| `APP_VERSION` | — | Версия приложения | `1.0.0` |
| `BACKEND_CORS_ORIGINS` | — | Разрешённые origins (через запятую) | `http://localhost:3000,http://localhost:5173` |
| `P2P_MOCK_BASE_URL` | — | URL mock-server | `http://mock-server:8001/v1/api` |
| `P2P_DATA_SOURCE` | — | Источник данных: `mock` или `real` | `mock` |
| `GOOGLE_CLIENT_ID` | — | Google OAuth2 Client ID | из Google Console |
| `GOOGLE_CLIENT_SECRET` | — | Google OAuth2 Client Secret | из Google Console |
| `GOOGLE_REDIRECT_URI` | — | OAuth2 callback URL | `http://localhost:8000/api/v1/auth/google/callback` |
| `SENTRY_DSN_BACKEND` | — | Sentry DSN (опционально) | `https://...@sentry.io/...` |
| `SENTRY_ENVIRONMENT` | — | Sentry environment | `development` |
| `METRICS_ENABLED` | — | Включить Prometheus /metrics | `true` |
| `LOG_FORMAT` | — | Формат логов: `json` / `console` | auto (json на Railway) |

### Frontend

| Переменная | Обязательная | Описание | Пример / Default |
|------------|:---:|----------|------------------|
| `VITE_API_URL` | ✅ | URL backend API | `http://localhost:8000` |
| `VITE_YM_COUNTER_ID` | — | Яндекс.Метрика counter ID | `12345678` |
| `VITE_SENTRY_DSN` | — | Sentry DSN frontend (опционально) | `https://...@sentry.io/...` |

## CI/CD

### Пайплайн

```
Push/PR в H6/**  →  GitHub Actions (h6-ci.yml)  →  Lint + Test + Audit
Push main        →  Railway Autodeploy           →  Build + Deploy
Push main        →  GitHub Actions (h6-deploy.yml) → Smoke-test /health
```

### Ключевые решения

- **GitHub Actions НЕ деплоит** — деплой выполняет Railway через Git Integration
- **Audit steps** — `continue-on-error: true`, не блокируют merge
- **Миграции БД** — выполняются в Dockerfile backend при каждом старте (`alembic upgrade head`)
- **Smoke-test** — проверяет не только HTTP 200, но и `status == "ok"` в теле ответа

## Интеграции

| Интеграция | Описание | Подробнее |
|------------|----------|-----------|
| GitHub Actions CI | Lint, test, audit при push/PR | [h6-ci.yml](../.github/workflows/h6-ci.yml) |
| Railway Deploy | Автодеплой при push в main | [integration_documentation.md](./integration_documentation.md#1-cicd) |
| Google OAuth2 | Вход через Google-аккаунт | [integration_documentation.md](./integration_documentation.md#2-oauth2-google) |
| Яндекс.Метрика | Аналитика поведения пользователей | [integration_documentation.md](./integration_documentation.md#3-яндексметрика) |
| UptimeRobot | Мониторинг доступности /health | [integration_documentation.md](./integration_documentation.md#4-мониторинг-uptimerobot--health-check) |
| structlog | JSON-логирование с X-Request-ID | [integration_documentation.md](./integration_documentation.md#5-логирование-structlog--x-request-id) |
| Sentry (опц.) | Отслеживание ошибок | [integration_documentation.md](./integration_documentation.md#6-sentry-опционально) |
| Prometheus (опц.) | Метрики + Grafana dashboard | [integration_documentation.md](./integration_documentation.md#7-prometheus--grafana-опционально) |

## Документация

- [Integration Documentation](./integration_documentation.md) — подробное описание всех интеграций
- [Security Audit](./security_audit.md) — результаты OWASP-аудита безопасности

## Технологии

| Слой | Технологии |
|------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, structlog, Redis |
| Frontend | React 18, TypeScript, Vite, Zustand, shadcn/ui, TanStack Query |
| Инфраструктура | Docker, Railway, GitHub Actions |
| БД | PostgreSQL, Redis |
| Мониторинг | UptimeRobot, Prometheus + Grafana (local) |
| Безопасность | OWASP audit, pip-audit, npm audit, CORS, CSRF, HttpOnly cookies |
