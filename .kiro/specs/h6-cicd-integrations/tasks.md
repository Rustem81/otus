# Задачи — H6: CI/CD и интеграция сервисов

## Условные обозначения
- 🤖 — задача выполняется AI (Kiro)
- 👤 — задача выполняется разработчиком вручную (с инструкцией)
- 🤖+👤 — совместная: AI генерирует, разработчик проверяет/дополняет

---

## Фаза 0: Подготовка проекта

- [-] 1. 🤖 Копирование H5 → H6 и подготовка структуры
  - [ ] 1.1 Скопировать `H5/backend/` → `H6/backend/`
  - [ ] 1.2 Скопировать `H5/frontend/` → `H6/frontend/`
  - [ ] 1.3 Скопировать `H5/mock-server/` → `H6/mock-server/`
  - [ ] 1.4 Скопировать `H5/docker-compose.yml` → `H6/docker-compose.yml`
  - [ ] 1.5 Создать `H6/.env.example` с переменными: DATABASE_URL, REDIS_URL, SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, SENTRY_DSN_BACKEND, SENTRY_DSN_FRONTEND, VITE_YM_COUNTER_ID, METRICS_ENABLED, LOG_FORMAT, APP_VERSION
  - [ ] 1.6 Создать черновик `H6/README.md` со структурой проекта и ссылками-заглушками
  - [ ] 1.7 Создать `H6/monitoring/prometheus/prometheus.yml` и `H6/monitoring/grafana/provisioning/` (заглушки для опциональной фазы)

- [ ] 2. 👤 Локальная проверка и git

  **Инструкция для разработчика:**
  1. Создать файл `H6/.env` из `H6/.env.example`, заполнить реальные значения (DATABASE_URL, REDIS_URL, SECRET_KEY — можно из H5)
  2. Запустить `docker compose up` из `H6/` — убедиться, что backend, frontend, mock-server, postgres, redis поднимаются
  3. Проверить: `curl http://localhost:8000/health` → 200
  4. Проверить: `http://localhost:5173` открывается в браузере
  5. Создать ветку: `git checkout -b feature/h6-integrations`
  6. Закоммитить: `git add H6/ && git commit -m "feat(H6): init from H5"`
  7. Push: `git push -u origin feature/h6-integrations`
  8. **НЕ коммитить** `.env` — только `.env.example`

---

## Фаза 1: CI/CD

- [ ] 3. 🤖 Создать GitHub Actions CI workflow
  - [ ] 3.1 Создать `.github/workflows/h6-ci.yml` с path filter `H6/**` и `.github/workflows/h6-*.yml`
  - [ ] 3.2 Job `backend-lint-test`: setup python 3.11, pip install, ruff check, pytest (working-directory: H6/backend)
  - [ ] 3.3 Job `backend-security`: pip-audit с `continue-on-error: true`
  - [ ] 3.4 Job `frontend-lint-test`: setup node 20, npm ci, npm run lint, npm run test -- --run (working-directory: H6/frontend)
  - [ ] 3.5 Job `frontend-audit`: npm audit --audit-level=high с `continue-on-error: true`
  - [ ] 3.6 Добавить `permissions: contents: read` на уровне workflow (principle of least privilege)

- [ ] 4. 🤖 Создать Post-Deploy Verification workflow
  - [ ] 4.1 Создать `.github/workflows/h6-deploy.yml` (trigger: push main, paths H6/**)
  - [ ] 4.2 Job `smoke-test`: sleep 180, curl /health, проверка `jq .status == "ok"`

- [ ] 5. 👤 Настройка GitHub и Railway для CI/CD

  **Инструкция для разработчика:**
  1. Зайти в https://github.com/Rustem81/otus → Settings → Secrets and variables → Actions
  2. Добавить Repository variable: `BACKEND_URL` = `https://<backend>.up.railway.app` (после создания Railway, пока заглушка)
  3. Зайти в https://railway.app/ → Login with GitHub
  4. New Project → Deploy from GitHub repo → выбрать `Rustem81/otus`
  5. Создать 3 сервиса:
     - backend: Settings → Root Directory = `H6/backend`, Watch Paths = `H6/backend/**`
     - frontend: Settings → Root Directory = `H6/frontend`, Watch Paths = `H6/frontend/**`
     - mock-server: Settings → Root Directory = `H6/mock-server`, Watch Paths = `H6/mock-server/**`
  6. Добавить plugins: PostgreSQL, Redis
  7. Для backend → Variables:
     - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
     - `REDIS_URL` = `${{Redis.REDIS_URL}}`
     - `SECRET_KEY` = сгенерировать (например `openssl rand -hex 32`)
     - `BACKEND_CORS_ORIGINS` = URL frontend (после generate domain)
     - `P2P_MOCK_BASE_URL` = `http://mock-server.railway.internal:8001`
     - `P2P_DATA_SOURCE` = `mock`
     - `APP_VERSION` = `1.0.0`
  8. Для frontend → Variables:
     - `VITE_API_URL` = URL backend (после generate domain)
  9. Generate Domain для backend и frontend (Settings → Networking → Generate Domain)
  10. mock-server: **НЕ** генерировать публичный домен (internal only)
  11. Обновить `BACKEND_URL` в GitHub Variables на реальный Railway URL
  12. Сделать push в main → проверить что Railway автодеплоит
  13. Проверить: `curl https://<backend>.up.railway.app/health` → 200
  14. Проверить: GitHub Actions → h6-ci зелёный, h6-deploy smoke-test зелёный

---

## Фаза 2: Аудит безопасности

- [ ] 6. 🤖 OWASP-аудит кода и генерация security_audit.md
  - [ ] 6.1 Проанализировать `H6/backend/app/api/`, `middleware/`, `services/` по OWASP Top 10
  - [ ] 6.2 Проверить: CORS настройки, CSRF middleware, JWT/session хранение, SQL injection protection
  - [ ] 6.3 Проверить: логирование не содержит секретов (пароли, токены, cookies не попадают в stdout/structlog)
  - [ ] 6.4 Создать `H6/security_audit.md` с разделами: Методология, Таблица находок, Рекомендации
  - [ ] 6.5 Применить исправления в коде (secure headers, OAuth state validation, etc.)

- [ ] 7. 👤 Запуск audit инструментов и финализация отчёта

  **Инструкция для разработчика:**
  1. Backend: `cd H6/backend && pip install pip-audit && pip-audit` → сохранить вывод
  2. Frontend: `cd H6/frontend && npm audit` → сохранить вывод
  3. Просмотреть `H6/security_audit.md` (сгенерирован AI)
  4. Для каждой находки High/Critical — принять решение: fix или exception с обоснованием
  5. Обновить колонку "Статус" и "Коммит" в таблице находок
  6. Проверить: `.env` не в git (`git status` не показывает .env файлы)
  7. Проверить: в workflow файлах нет hardcoded секретов (только `${{ secrets.* }}` и `${{ vars.* }}`)
  8. Закоммитить: `git commit -m "security: audit and fixes"`

---

## Фаза 3: Структурированное логирование

- [ ] 8. 🤖 Настройка structlog и middleware X-Request-ID
  - [ ] 8.1 Добавить `structlog>=24.1.0` в `H6/backend/pyproject.toml`
  - [ ] 8.2 Создать `H6/backend/app/core/logging_config.py`: configure_logging() с JSON/console renderer (auto по RAILWAY_ENVIRONMENT)
  - [ ] 8.3 Создать `H6/backend/app/middleware/request_id.py`: RequestIDMiddleware (генерация/проброс X-Request-ID, bind в structlog contextvars)
  - [ ] 8.4 Подключить middleware и configure_logging() в `main.py`
  - [ ] 8.5 Заменить стандартные logging-вызовы в ключевых местах на structlog (health, auth, polling)

- [ ] 9. 👤 Проверка логирования

  **Инструкция для разработчика:**
  1. Запустить backend локально: `cd H6/backend && uvicorn app.main:app --reload`
  2. Сделать несколько запросов: `curl http://localhost:8000/health`, `curl http://localhost:8000/api/v1/ads`
  3. Проверить в терминале: логи в формате pretty console (цветные, читаемые)
  4. Проверить наличие `request_id` в каждой строке лога
  5. Проверить: `curl -H "X-Request-ID: test-123" http://localhost:8000/health` → в логах `request_id: test-123`
  6. Проверить response header: `X-Request-ID` присутствует
  7. Сохранить 10-20 строк логов в файл для отчёта (не коммитить, для integration_documentation.md)
  8. Закоммитить: `git commit -m "feat(H6): structured logging with structlog"`

---

## Фаза 4: Health Check

- [ ] 10. 🤖 Расширение /health и добавление /health/live
  - [ ] 10.1 Модифицировать `H6/backend/app/api/v1/endpoints/health.py`: добавить проверку mock_server, поле version из settings.APP_VERSION
  - [ ] 10.2 Возвращать `{"status": "ok"|"degraded", "version": "...", "dependencies": {...}}`
  - [ ] 10.3 Добавить endpoint `GET /health/live` → `{"status": "ok"}` без проверки зависимостей
  - [ ] 10.4 Добавить `APP_VERSION` в config.py (default "1.0.0")
  - [ ] 10.5 Написать unit-тесты: all deps ok → "ok", one dep down → "degraded", /health/live always 200

- [ ] 11. 👤 Настройка UptimeRobot

  **Инструкция для разработчика:**
  1. Зайти на https://uptimerobot.com/ → Register (бесплатный план)
  2. Add New Monitor:
     - Type: HTTP(s)
     - Friendly Name: `MEXC P2P Backend`
     - URL: `https://<backend>.up.railway.app/health`
     - Monitoring Interval: 5 minutes
  3. Alert Contacts → добавить свой email
  4. Create Monitor
  5. Подождать 5-10 минут → убедиться что статус UP (зелёный)
  6. (Опционально) Остановить backend на Railway → проверить что алерт приходит на email
  7. Скриншот UptimeRobot dashboard → для отчёта

---

## Фаза 5: OAuth2 Google

- [ ] 12. 🤖 Backend OAuth2 — сервис и роуты
  - [ ] 12.1 Добавить `authlib>=1.3.0`, `httpx>=0.27.0` в `pyproject.toml`
  - [ ] 12.2 Добавить в `config.py`: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
  - [ ] 12.3 Создать `H6/backend/app/services/oauth_google.py`: GoogleOAuthService с методами get_authorization_url(), handle_callback(), _exchange_code(), _get_userinfo()
  - [ ] 12.4 Создать `H6/backend/app/api/v1/endpoints/auth_oauth.py`: GET /auth/google (redirect), GET /auth/google/callback (verify state, set cookie, redirect to frontend)
  - [ ] 12.5 Подключить роуты в router.py

- [ ] 13. 🤖 Alembic миграция для OAuth полей
  - [ ] 13.1 Создать миграцию: `alembic revision --autogenerate -m "add_oauth_fields"`
  - [ ] 13.2 Добавить поля `oauth_provider` (VARCHAR 32, nullable) и `oauth_subject` (VARCHAR 255, nullable) в модель User
  - [ ] 13.3 Создать уникальный partial index `ix_users_oauth` на (oauth_provider, oauth_subject) WHERE oauth_provider IS NOT NULL
  - [ ] 13.4 Проверить downgrade: drop index, drop columns

- [ ] 14. 🤖 Модификация Dockerfile для миграций
  - [ ] 14.1 Изменить CMD в `H6/backend/Dockerfile`: `CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]`

- [ ] 15. 🤖 Frontend OAuth — кнопка и callback page
  - [ ] 15.1 Модифицировать `login.tsx`: добавить кнопку "Войти через Google" → `window.location.href = VITE_API_URL + '/api/v1/auth/google'`
  - [ ] 15.2 Создать `H6/frontend/src/pages/auth-callback.tsx`: читает query params (success/error), показывает spinner, при success redirect на `/`
  - [ ] 15.3 Добавить route `/auth/callback` в роутер

- [ ] 16. 🤖 Unit-тесты OAuth
  - [ ] 16.1 Тест: get_authorization_url генерирует state и сохраняет в Redis
  - [ ] 16.2 Тест: callback с невалидным state → 400
  - [ ] 16.3 Тест: callback с валидным state → создаёт user, возвращает session cookie
  - [ ] 16.4 Тест: существующий user по email → связывает oauth_provider/oauth_subject

- [ ] 17. 👤 Настройка Google Cloud Console и тестирование OAuth

  **Инструкция для разработчика:**
  1. Открыть https://console.cloud.google.com/
  2. Создать проект: `MEXC P2P Insight`
  3. APIs & Services → OAuth consent screen:
     - User Type: External
     - App name: `MEXC P2P Insight`
     - User support email: ваш email
     - Scopes: `openid`, `email`, `profile`
     - Test users: добавить свой Google email
  4. APIs & Services → Credentials → Create Credentials → OAuth client ID:
     - Application type: Web application
     - Name: `MEXC P2P Web Client`
     - Authorized JavaScript origins: `http://localhost:5173`, `https://<frontend>.up.railway.app`
     - Authorized redirect URIs: `http://localhost:8000/api/v1/auth/google/callback`, `https://<backend>.up.railway.app/api/v1/auth/google/callback`
  5. Скопировать Client ID и Client Secret
  6. Добавить в `H6/.env`:
     ```
     GOOGLE_CLIENT_ID=<your-client-id>
     GOOGLE_CLIENT_SECRET=<your-client-secret>
     GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
     ```
  7. Добавить в Railway backend Variables: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI (с prod URL)
  8. Добавить в GitHub Secrets: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
  9. Тестирование локально:
     - Запустить backend + frontend
     - Нажать "Войти через Google" → должен открыться Google consent
     - Авторизоваться → redirect обратно в приложение
     - Проверить: `/api/v1/auth/me` → 200 с данными пользователя
  10. Тестирование на Railway:
     - Push в main → дождаться деплоя
     - Повторить OAuth flow на prod URL
  11. Закоммитить: `git commit -m "feat(H6): Google OAuth2 integration"`

---

## Фаза 6: Яндекс.Метрика

- [ ] 18. 🤖 Интеграция Яндекс.Метрики во Frontend
  - [ ] 18.1 Создать `H6/frontend/src/lib/analytics.ts`: initMetrika(), trackPageView(), trackEvent() — no-op если не PROD или нет COUNTER_ID
  - [ ] 18.2 Добавить типы `window.ym` в `vite-env.d.ts`
  - [ ] 18.3 Вызвать `initMetrika()` в `main.tsx`
  - [ ] 18.4 Добавить `trackPageView` в корневой layout (useEffect на location change)
  - [ ] 18.5 Добавить `trackEvent('login')` в login.tsx после успешного POST /auth/login
  - [ ] 18.6 Добавить `trackEvent('oauth_login')` в auth-callback.tsx при success
  - [ ] 18.7 Добавить `trackEvent('view_ad')` в AdDetailDialog при открытии
  - [ ] 18.8 Добавить `trackEvent('blacklist_add')` после успешного POST /blacklist

- [ ] 19. 👤 Регистрация счётчика и настройка целей

  **Инструкция для разработчика:**
  1. Открыть https://metrika.yandex.ru/ → войти под Яндекс-ID
  2. Добавить счётчик:
     - Имя: `MEXC P2P Insight`
     - Адрес сайта: `https://<frontend>.up.railway.app` (или localhost для начала)
     - Часовой пояс: ваш
  3. Скопировать номер счётчика (например `12345678`)
  4. Настройки счётчика → включить Вебвизор (опционально)
  5. Цели → Добавить цель (тип: JavaScript-событие) для каждого:
     - `login` — Успешный вход
     - `register` — Регистрация
     - `oauth_login` — Вход через Google
     - `view_ad` — Просмотр объявления
     - `blacklist_add` — Блокировка мерчанта
  6. Добавить в `H6/frontend/.env`: `VITE_YM_COUNTER_ID=<номер>`
  7. Добавить в Railway frontend Variables: `VITE_YM_COUNTER_ID=<номер>`
  8. Дождаться redeploy на Railway
  9. Проверка:
     - Открыть prod frontend в браузере (без блокировщика рекламы!)
     - В Метрике → Отчёты → В реальном времени → должен появиться визит (1-3 мин)
     - Выполнить логин → проверить цель `login` в реальном времени
     - Открыть объявление → проверить цель `view_ad`
  10. На localhost: убедиться что в консоли нет ошибок (Метрика не загружается в dev)
  11. Сделать 2 скриншота: счётчик в списке + цели в реальном времени
  12. Закоммитить: `git commit -m "feat(H6): Yandex.Metrika analytics integration"`

---

## Фаза 7: Sentry (опционально)

- [ ]* 20. 🤖 Интеграция Sentry в Backend и Frontend
  - [ ]* 20.1 Добавить `sentry-sdk[fastapi]>=2.0.0` в `pyproject.toml`
  - [ ]* 20.2 В `main.py`: `sentry_sdk.init()` с FastApiIntegration, SqlalchemyIntegration, before_send фильтр PII
  - [ ]* 20.3 Передача request_id в Sentry context
  - [ ]* 20.4 Добавить `@sentry/react` в `package.json`
  - [ ]* 20.5 В `main.tsx`: `Sentry.init()` с browserTracingIntegration
  - [ ]* 20.6 Создать `ErrorBoundary.tsx` с fallback UI, обернуть роутер

- [ ]* 21. 👤 Регистрация Sentry и проверка

  **Инструкция для разработчика:**
  1. Зайти на https://sentry.io/ → Sign up (бесплатный Developer план)
  2. Create Project → Python → скопировать DSN → `SENTRY_DSN_BACKEND`
  3. Create Project → React → скопировать DSN → `VITE_SENTRY_DSN`
  4. Добавить в `H6/.env`: SENTRY_DSN_BACKEND, SENTRY_ENVIRONMENT=development
  5. Добавить в `H6/frontend/.env`: VITE_SENTRY_DSN
  6. Добавить в Railway: backend → SENTRY_DSN_BACKEND, SENTRY_ENVIRONMENT=production; frontend → VITE_SENTRY_DSN
  7. Тестирование: вызвать ошибку (например `GET /api/v1/debug/sentry-test` если есть)
  8. Проверить в Sentry → Issues → должен появиться issue со stack trace
  9. Убедиться: в issue нет паролей/токенов (before_send фильтрует)
  10. Скриншот Sentry issue → для отчёта

---

## Фаза 8: Prometheus + Grafana (опционально)

- [ ]* 22. 🤖 Prometheus метрики и Grafana dashboard
  - [ ]* 22.1 Добавить `prometheus-fastapi-instrumentator>=7.0.0` в `pyproject.toml`
  - [ ]* 22.2 В `main.py`: `Instrumentator().instrument(app).expose(app, endpoint="/metrics")` — обернуть в `if settings.METRICS_ENABLED`
  - [ ]* 22.3 Добавить кастомные метрики: p2p_polling_duration_seconds, p2p_ads_active_total, auth_logins_total
  - [ ]* 22.4 Заполнить `H6/monitoring/prometheus/prometheus.yml` (scrape backend:8000/metrics)
  - [ ]* 22.5 Создать Grafana provisioning: datasource prometheus, dashboard config
  - [ ]* 22.6 Создать `H6/monitoring/grafana/dashboards/mexc-p2p.json` (панели: RPS, latency, errors, polling)
  - [ ]* 22.7 Добавить сервисы prometheus и grafana в `H6/docker-compose.yml`
  - [ ]* 22.8 Добавить `METRICS_ENABLED` в config.py (default True локально, можно отключить на Railway если не нужен публичный /metrics)

- [ ]* 23. 👤 Проверка Prometheus и Grafana

  **Инструкция для разработчика:**
  1. `cd H6 && docker compose up -d` (с prometheus и grafana)
  2. Проверить: `curl http://localhost:8000/metrics` → метрики есть
  3. Открыть http://localhost:9090/targets → target `fastapi` в статусе UP
  4. Открыть http://localhost:3001 → Grafana (admin/admin → сменить пароль!)
  5. Dashboards → должен быть provisioned dashboard `MEXC P2P`
  6. Сделать несколько запросов к backend → графики обновляются
  7. Скриншот Grafana dashboard → для отчёта
  8. Закоммитить: `git commit -m "feat(H6): Prometheus + Grafana monitoring"`

---

## Фаза 9: Документация

- [ ] 24. 🤖 Генерация integration_documentation.md
  - [ ] 24.1 Создать `H6/integration_documentation.md` с разделами: CI/CD, OAuth2, Яндекс.Метрика, Мониторинг, Логирование
  - [ ] 24.2 Для каждого раздела: описание, конфигурация, инструкция по воспроизведению
  - [ ] 24.3 Добавить раздел "Sentry" (если интегрирован)
  - [ ] 24.4 Добавить раздел "Prometheus + Grafana" (если интегрирован)
  - [ ] 24.5 Добавить таблицу "Использование AI": Этап | Промпт | Результат | Проверка разработчиком

- [ ] 25. 🤖 Финализация README.md
  - [ ] 25.1 Обновить `H6/README.md`: ссылки на репозиторий, деплой frontend, деплой backend, Swagger
  - [ ] 25.2 Добавить секцию "Быстрый старт" (docker compose, тестовые аккаунты)
  - [ ] 25.3 Добавить секцию "Переменные окружения" (таблица)

- [ ] 26. 👤 Финальная проверка и сдача

  **Инструкция для разработчика:**
  1. Вычитать `H6/integration_documentation.md` — проверить что все разделы заполнены
  2. Вычитать `H6/security_audit.md` — проверить статусы находок
  3. Проверить `H6/README.md` — ссылки рабочие
  4. Заполнить таблицу "Использование AI" реальными промптами из сессий работы
  5. Добавить скриншоты в отчёт (или в отдельную папку):
     - CI green (GitHub Actions)
     - Railway dashboard (сервисы running)
     - OAuth flow (Google consent → приложение)
     - Яндекс.Метрика "В реальном времени"
     - UptimeRobot UP
     - (Опционально) Sentry issue, Grafana dashboard
  6. Чеклист перед сдачей:
     - [ ] CI/CD работает (push → lint + test green)
     - [ ] Deploy: push main → Railway обновляет сервисы
     - [ ] Smoke-test: h6-deploy.yml green
     - [ ] OAuth2: вход через Google работает на prod
     - [ ] Метрика: визиты и цели видны
     - [ ] /health: возвращает "ok" с dependencies
     - [ ] UptimeRobot: monitor UP
     - [ ] Логи: JSON формат на Railway, request_id присутствует
     - [ ] security_audit.md: заполнен
     - [ ] integration_documentation.md: все разделы
  7. Merge PR в main: `git checkout main && git merge feature/h6-integrations && git push`
  8. Сдать на платформе OTUS: ссылка на репозиторий + ссылки на деплой
