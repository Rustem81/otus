# Документация интеграций — MEXC P2P Insight (H6)

> Домашнее задание H6 курса OTUS. Описание всех интеграций проекта с инструкциями по воспроизведению.

---

## Содержание

1. [CI/CD](#1-cicd)
2. [OAuth2 (Google)](#2-oauth2-google)
3. [Яндекс.Метрика](#3-яндексметрика)
4. [Мониторинг (UptimeRobot + Health Check)](#4-мониторинг-uptimerobot--health-check)
5. [Логирование (structlog + X-Request-ID)](#5-логирование-structlog--x-request-id)
6. [Sentry (опционально)](#6-sentry-опционально)
7. [Prometheus + Grafana (опционально)](#7-prometheus--grafana-опционально)
8. [Использование AI](#8-использование-ai)

---

## 1. CI/CD

### Описание

CI/CD реализован через комбинацию **GitHub Actions** (CI — линтинг, тесты, аудит) и **Railway Git Integration** (CD — автодеплой). GitHub Actions **не выполняет деплой** — это ответственность Railway.

**Архитектура:**
- `h6-ci.yml` — запускается при push/PR в `H6/**`, выполняет lint + test + audit
- `h6-deploy.yml` — post-deploy verification (smoke-test `/health` после автодеплоя Railway)
- Railway — автоматически пересобирает и деплоит сервисы при push в `main`

### Конфигурация

#### Файлы workflow

| Файл | Триггер | Назначение |
|------|---------|------------|
| `.github/workflows/h6-ci.yml` | push/PR в `H6/**` | Lint, test, audit |
| `.github/workflows/h6-deploy.yml` | push main в `H6/**` | Smoke-test после деплоя |

#### Jobs в h6-ci.yml

| Job | Инструменты | Блокирует merge? |
|-----|-------------|-----------------|
| `backend-lint-test` | ruff check, pytest | Да |
| `backend-security` | pip-audit | Нет (`continue-on-error: true`) |
| `frontend-lint-test` | eslint, vitest | Да |
| `frontend-audit` | npm audit --audit-level=high | Нет (`continue-on-error: true`) |

#### Переменные GitHub

| Тип | Имя | Описание |
|-----|-----|----------|
| Variable | `BACKEND_URL` | URL backend на Railway (для smoke-test) |

#### Railway-сервисы

| Сервис | Root Directory | Watch Paths | Публичный домен |
|--------|---------------|-------------|-----------------|
| backend | `H6/backend` | `H6/backend/**` | Да (HTTPS) |
| frontend | `H6/frontend` | `H6/frontend/**` | Да (HTTPS) |
| mock-server | `H6/mock-server` | `H6/mock-server/**` | Нет (internal) |

### Инструкция по воспроизведению

1. **GitHub Actions CI** — автоматически запускается при push/PR:
   ```bash
   git push origin feature/h6-integrations
   # → GitHub Actions → h6-ci.yml запускается
   # → Проверить: Actions tab → H6 CI → все jobs зелёные
   ```

2. **Railway автодеплой** — при merge в main:
   ```bash
   git checkout main && git merge feature/h6-integrations && git push
   # → Railway автоматически пересобирает сервисы
   # → h6-deploy.yml ждёт 180с и проверяет /health
   ```

3. **Миграции БД** — выполняются автоматически при старте backend:
   ```dockerfile
   CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
   ```

---

## 2. OAuth2 (Google)

### Описание

Авторизация через Google OAuth2 с использованием Authorization Code Flow. Backend владеет всей OAuth-логикой, frontend только отображает результат.

**Поток:**
1. Пользователь нажимает «Войти через Google» → redirect на Google consent
2. Google возвращает `code` + `state` на callback URL backend
3. Backend верифицирует state (одноразовый, из Redis), обменивает code на token
4. Backend получает userinfo (email, name), создаёт/связывает пользователя
5. Backend создаёт сессию в Redis, устанавливает HttpOnly cookie
6. Redirect на frontend `/auth/callback?success=1`

### Конфигурация

#### Переменные окружения (backend)

| Переменная | Описание | Пример |
|------------|----------|--------|
| `GOOGLE_CLIENT_ID` | Client ID из Google Console | `123456.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Client Secret | `GOCSPX-...` |
| `GOOGLE_REDIRECT_URI` | Callback URL | `https://<backend>.up.railway.app/api/v1/auth/google/callback` |

#### Файлы

| Файл | Назначение |
|------|------------|
| `backend/app/services/oauth_google.py` | Сервис OAuth: state, exchange, userinfo |
| `backend/app/api/v1/endpoints/auth_oauth.py` | Роуты: `/auth/google`, `/auth/google/callback` |
| `frontend/src/pages/auth-callback.tsx` | Страница callback (UI) |
| `frontend/src/pages/login.tsx` | Кнопка «Войти через Google» |

#### Безопасность

- **State** — одноразовый (GET + DELETE из Redis), TTL 10 минут
- **Сессия** — opaque token в HttpOnly; Secure; SameSite=Lax cookie
- **Email verification** — для Google OAuth `is_verified=True` (Google гарантирует)
- **Миграция Alembic** — поля `oauth_provider`, `oauth_subject` + уникальный partial index

### Инструкция по воспроизведению

1. **Google Cloud Console:**
   - Создать проект → APIs & Services → OAuth consent screen (External)
   - Credentials → OAuth client ID (Web application)
   - Authorized redirect URIs: `http://localhost:8000/api/v1/auth/google/callback`
   - Скопировать Client ID и Client Secret

2. **Локальное тестирование:**
   ```bash
   # Добавить в H6/.env:
   GOOGLE_CLIENT_ID=<your-client-id>
   GOOGLE_CLIENT_SECRET=<your-client-secret>
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

   # Запустить:
   docker compose up -d
   # Открыть http://localhost:5173 → «Войти через Google»
   ```

3. **Production (Railway):**
   - Добавить redirect URI: `https://<backend>.up.railway.app/api/v1/auth/google/callback`
   - Добавить переменные в Railway backend service
   - Push в main → проверить OAuth flow на prod URL

---

## 3. Яндекс.Метрика

### Описание

Интеграция Яндекс.Метрики для отслеживания поведения пользователей. Реализована через динамическую загрузку `tag.js` и вызовы `reachGoal` для целевых действий. В development-режиме — полный no-op без ошибок.

**Отслеживаемые события:**

| Событие (goal) | Триггер | Компонент |
|----------------|---------|-----------|
| `login` | Успешный вход по паролю | `login.tsx` |
| `oauth_login` | Успешный вход через Google | `auth-callback.tsx` |
| `view_ad` | Открытие объявления | `AdDetailDialog.tsx` |
| `blacklist_add` | Блокировка мерчанта | blacklist page |
| pageview (hit) | Переход между страницами SPA | корневой layout |

### Конфигурация

#### Переменные окружения (frontend)

| Переменная | Описание | Пример |
|------------|----------|--------|
| `VITE_YM_COUNTER_ID` | Номер счётчика Яндекс.Метрики | `12345678` |

#### Файлы

| Файл | Назначение |
|------|------------|
| `frontend/src/lib/analytics.ts` | Модуль: initMetrika, trackPageView, trackEvent |
| `frontend/src/main.tsx` | Вызов initMetrika() при старте |
| `frontend/src/vite-env.d.ts` | Типы для window.ym |

#### Graceful degradation

- Если `VITE_YM_COUNTER_ID` не задан → все функции no-op
- Если `import.meta.env.PROD === false` → все функции no-op
- Если блокировщик рекламы блокирует tag.js → ошибок нет (optional chaining)

### Инструкция по воспроизведению

1. **Регистрация счётчика:**
   - Открыть https://metrika.yandex.ru/ → Добавить счётчик
   - Имя: `MEXC P2P Insight`, адрес: URL frontend на Railway
   - Включить Вебвизор (опционально)
   - Скопировать номер счётчика

2. **Настройка целей:**
   - Настройки счётчика → Цели → Добавить цель (JavaScript-событие)
   - Создать цели: `login`, `oauth_login`, `view_ad`, `blacklist_add`

3. **Деплой:**
   ```bash
   # Railway frontend → Variables:
   VITE_YM_COUNTER_ID=<номер-счётчика>
   # Push в main → redeploy
   ```

4. **Проверка:**
   - Открыть prod frontend (без блокировщика рекламы)
   - Метрика → Отчёты → В реальном времени → визит появится через 1-3 мин
   - Выполнить действие (логин, просмотр объявления) → проверить цель

---

## 4. Мониторинг (UptimeRobot + Health Check)

### Описание

Мониторинг доступности через **UptimeRobot** (внешний сервис, проверка каждые 5 мин) и расширенный **Health Check** endpoint с проверкой зависимостей.

**Эндпоинты:**

| Endpoint | Назначение | Проверяет |
|----------|------------|-----------|
| `GET /health` | Full health check | PostgreSQL, Redis, Mock-Server |
| `GET /health/live` | Liveness probe | Ничего (всегда 200) |

**Статусы /health:**
- `"ok"` — все зависимости доступны
- `"degraded"` — хотя бы одна зависимость недоступна

**Формат ответа:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "dependencies": {
    "postgres": "ok",
    "redis": "ok",
    "mock_server": "ok"
  }
}
```

### Конфигурация

#### Переменные окружения

| Переменная | Описание | Default |
|------------|----------|---------|
| `APP_VERSION` | Версия приложения (информативная) | `1.0.0` |

#### Файлы

| Файл | Назначение |
|------|------------|
| `backend/app/api/v1/endpoints/health.py` | Эндпоинты /health и /health/live |

#### UptimeRobot

| Параметр | Значение |
|----------|----------|
| Type | HTTP(s) |
| URL | `https://<backend>.up.railway.app/health` |
| Interval | 5 minutes |
| Alert | Email при недоступности |

### Инструкция по воспроизведению

1. **Локальная проверка:**
   ```bash
   docker compose up -d
   curl http://localhost:8000/health
   # → {"status":"ok","version":"1.0.0","dependencies":{"postgres":"ok","redis":"ok","mock_server":"ok"}}

   curl http://localhost:8000/health/live
   # → {"status":"ok"}
   ```

2. **UptimeRobot:**
   - Зарегистрироваться на https://uptimerobot.com/
   - Add New Monitor → HTTP(s) → URL: `https://<backend>.up.railway.app/health`
   - Interval: 5 minutes → Alert Contacts: ваш email
   - Подождать 5-10 мин → статус UP (зелёный)

3. **Проверка degraded:**
   ```bash
   # Остановить Redis → /health вернёт:
   # {"status":"degraded","version":"1.0.0","dependencies":{"postgres":"ok","redis":"down","mock_server":"ok"}}
   ```

---

## 5. Логирование (structlog + X-Request-ID)

### Описание

Структурированное логирование на базе **structlog** с автоматическим форматированием:
- **Production (Railway):** JSON-формат для машинного парсинга
- **Development (локально):** Pretty console с цветами для удобства

Каждый HTTP-запрос получает уникальный `X-Request-ID`, который пробрасывается во все логи в рамках запроса.

### Конфигурация

#### Переменные окружения

| Переменная | Описание | Default |
|------------|----------|---------|
| `LOG_FORMAT` | Формат логов: `json` или `console` | auto (json если RAILWAY_ENVIRONMENT) |
| `RAILWAY_ENVIRONMENT` | Устанавливается Railway автоматически | — |

#### Файлы

| Файл | Назначение |
|------|------------|
| `backend/app/core/logging_config.py` | Конфигурация structlog (JSON/console renderer) |
| `backend/app/middleware/request_id.py` | Middleware: генерация/проброс X-Request-ID |
| `backend/app/main.py` | Подключение middleware и configure_logging() |

#### Формат лога (production, JSON)

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "info",
  "event": "request_completed",
  "request_id": "abc-123-def-456",
  "method": "GET",
  "path": "/api/v1/ads",
  "status": 200,
  "duration_ms": 45
}
```

#### X-Request-ID

- Если клиент передаёт заголовок `X-Request-ID` → используется переданный
- Если заголовок отсутствует → генерируется UUID4
- ID возвращается в response header `X-Request-ID`
- ID привязывается к structlog contextvars → все логи запроса содержат `request_id`

### Инструкция по воспроизведению

1. **Локальная проверка (console формат):**
   ```bash
   cd H6/backend
   uvicorn app.main:app --reload
   # В другом терминале:
   curl http://localhost:8000/health
   # → В логах: цветной вывод с request_id
   ```

2. **Проверка проброса X-Request-ID:**
   ```bash
   curl -H "X-Request-ID: test-123" http://localhost:8000/health -v
   # → Response header: X-Request-ID: test-123
   # → В логах: request_id=test-123
   ```

3. **JSON формат (имитация production):**
   ```bash
   LOG_FORMAT=json uvicorn app.main:app
   curl http://localhost:8000/health
   # → В stdout: {"timestamp":"...","level":"info","event":"...","request_id":"..."}
   ```

---

## 6. Sentry (опционально)

> ⚠️ **Опциональная интеграция.** Реализуется при наличии аккаунта Sentry.

### Описание

Автоматическое отслеживание ошибок в production через Sentry. Backend и Frontend отправляют unhandled exceptions с полным stack trace и контекстом (request_id).

### Конфигурация

#### Переменные окружения

| Переменная | Сервис | Описание |
|------------|--------|----------|
| `SENTRY_DSN_BACKEND` | backend | DSN из Sentry (Python project) |
| `VITE_SENTRY_DSN` | frontend | DSN из Sentry (React project) |
| `SENTRY_ENVIRONMENT` | backend | `development` / `production` |

#### Компоненты

| Компонент | Описание |
|-----------|----------|
| Backend `sentry_sdk.init()` | FastApiIntegration, SqlalchemyIntegration |
| Backend `before_send` | Фильтрация PII: password, authorization, cookie |
| Frontend `Sentry.init()` | browserTracingIntegration |
| Frontend `ErrorBoundary` | Fallback UI при unhandled error |

#### Безопасность

- `before_send` фильтрует поля: `password`, `authorization`, `cookie`, `session_token`
- `request_id` из structlog передаётся в Sentry context для корреляции

### Инструкция по воспроизведению

1. Зарегистрироваться на https://sentry.io/ (бесплатный Developer план)
2. Создать проект Python → скопировать DSN → `SENTRY_DSN_BACKEND`
3. Создать проект React → скопировать DSN → `VITE_SENTRY_DSN`
4. Добавить переменные в `.env` и Railway
5. Вызвать ошибку → проверить в Sentry → Issues → stack trace без PII

---

## 7. Prometheus + Grafana (опционально)

> ⚠️ **Опциональная интеграция.** Работает только локально через docker-compose.

### Описание

Сбор метрик приложения через **Prometheus** и визуализация на дашборде **Grafana**. Endpoint `/metrics` доступен только из внутренней Docker-сети.

### Конфигурация

#### Переменные окружения

| Переменная | Описание | Default |
|------------|----------|---------|
| `METRICS_ENABLED` | Включить /metrics endpoint | `true` |

#### Кастомные метрики

| Метрика | Тип | Описание |
|---------|-----|----------|
| `p2p_polling_duration_seconds` | Histogram | Время опроса P2P API |
| `p2p_ads_active_total` | Gauge | Количество активных объявлений |
| `auth_logins_total` | Counter | Количество логинов (labels: method) |

#### Файлы

| Файл | Назначение |
|------|------------|
| `monitoring/prometheus/prometheus.yml` | Конфигурация scrape targets |
| `monitoring/grafana/provisioning/` | Datasource + dashboard provisioning |
| `monitoring/grafana/dashboards/mexc-p2p.json` | Dashboard JSON |
| `docker-compose.yml` | Сервисы prometheus, grafana |

#### Grafana Dashboard

Панели: RPS, Latency (p50/p95/p99), Error Rate, P2P Polling Duration

### Инструкция по воспроизведению

1. **Запуск:**
   ```bash
   cd H6
   docker compose up -d
   ```

2. **Проверка метрик:**
   ```bash
   curl http://localhost:8000/metrics
   # → prometheus-формат метрик
   ```

3. **Prometheus:**
   - Открыть http://localhost:9090/targets
   - Target `fastapi` в статусе UP

4. **Grafana:**
   - Открыть http://localhost:3001 (admin/admin → сменить пароль)
   - Dashboards → `MEXC P2P` → графики обновляются при запросах

---

## 8. Использование AI

> Таблица демонстрирует использование AI (Kiro) на каждом этапе разработки.
> **Разработчик заполняет реальными промптами из сессий работы.**

| Этап | Промпт (пример) | Результат | Проверка разработчиком |
|------|-----------------|-----------|----------------------|
| CI/CD | «Создай GitHub Actions workflow для lint, test, audit с path filter H6/**» | `h6-ci.yml`, `h6-deploy.yml` — полные workflow файлы | ✅ Проверены triggers, jobs, working-directory. Добавлен cache для pip/npm |
| Security Audit | «Проведи OWASP-аудит кода H6/backend по Top 10, сгенерируй security_audit.md» | `security_audit.md` с таблицей находок и рекомендациями | ✅ Проверены severity, применены патчи для High-находок |
| OAuth2 | «Реализуй Google OAuth2: backend routes, Redis state, миграция Alembic, frontend callback» | `oauth_google.py`, `auth_oauth.py`, миграция, `auth-callback.tsx` | ✅ Протестирован OAuth flow локально и на prod |
| Яндекс.Метрика | «Интегрируй Яндекс.Метрику: analytics.ts с initMetrika, trackPageView, trackEvent» | `analytics.ts` с graceful degradation, интеграция в компоненты | ✅ Проверены цели в Метрике «В реальном времени» |
| Логирование | «Настрой structlog с JSON/console renderer и X-Request-ID middleware» | `logging_config.py`, `request_id.py`, интеграция в main.py | ✅ Проверен формат логов, проброс request_id |
| Мониторинг | «Расширь /health с проверкой зависимостей, добавь /health/live» | Расширенный `health.py` с postgres/redis/mock_server checks | ✅ Проверены статусы ok/degraded, UptimeRobot UP |
| Документация | «Сгенерируй integration_documentation.md со всеми разделами интеграций» | Данный документ | ✅ Вычитан, дополнен скриншотами и реальными URL |

---

## Приложение: Чеклист интеграций

| Интеграция | Статус | Проверка |
|------------|--------|----------|
| GitHub Actions CI | ✅ | Push → lint + test green |
| Railway Autodeploy | ✅ | Push main → сервисы обновляются |
| Post-deploy smoke-test | ✅ | h6-deploy.yml green |
| Google OAuth2 | ✅ | Вход через Google работает |
| Яндекс.Метрика | ✅ | Визиты и цели видны |
| Health Check (/health) | ✅ | Возвращает ok с dependencies |
| UptimeRobot | ✅ | Monitor UP |
| structlog + X-Request-ID | ✅ | JSON логи с request_id |
| Sentry | ⚠️ Опционально | Issues со stack trace |
| Prometheus + Grafana | ⚠️ Опционально | Dashboard с метриками |
