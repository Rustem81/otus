# Документ требований — H6: CI/CD и интеграция сервисов

## Введение

Домашнее задание H6 курса OTUS для проекта «MEXC P2P Insight». Цель — настроить CI/CD пайплайн, провести аудит безопасности, интегрировать внешние сервисы (OAuth2, аналитика, мониторинг, логирование) и задеплоить приложение на Railway. Проект представляет собой monorepo (`github.com/Rustem81/otus`) с папками H1–H7. Код H6 базируется на H5 (FastAPI backend, React/Vite frontend, mock-server).

Задачи разделены на:
- 🤖 **AI (Kiro)** — генерация кода, конфигов, документации
- 👤 **Разработчик** — регистрация в сервисах, секреты, ручное тестирование, финальная проверка

## Глоссарий

- **CI_Pipeline** — GitHub Actions workflow для автоматической сборки, тестирования и линтинга кода при push/PR
- **Deploy_Pipeline** — GitHub Actions workflow для автоматического деплоя на Railway при push в main
- **Backend** — FastAPI-приложение в `H6/backend/`
- **Frontend** — React/Vite-приложение в `H6/frontend/`
- **Mock_Server** — FastAPI-сервис эмуляции P2P API в `H6/mock-server/`
- **Railway** — PaaS-платформа для деплоя всех сервисов
- **Health_Endpoint** — HTTP-эндпоинт проверки состояния приложения и зависимостей
- **OAuth_Module** — модуль авторизации через Google OAuth2
- **Analytics_Module** — модуль интеграции Яндекс.Метрики во Frontend
- **Logging_Module** — модуль структурированного JSON-логирования на Backend
- **Security_Auditor** — процесс проверки зависимостей и кода на уязвимости
- **Monitoring_Service** — внешний сервис (UptimeRobot) для мониторинга доступности

## Требования

### Требование 1: CI/CD пайплайн — сборка и тестирование

**User Story:** Как разработчик, я хочу автоматическую проверку кода при каждом push/PR, чтобы ошибки обнаруживались до попадания в main.

**Роли:** 🤖 генерация workflow-файлов | 👤 настройка GitHub Secrets, проверка Actions

#### Acceptance Criteria

1. WHEN код изменяется в `H6/**` или `.github/workflows/h6-*.yml`, THE CI_Pipeline SHALL запускаться автоматически при push и pull_request
2. THE CI_Pipeline SHALL выполнять линтинг Backend с помощью ruff в рабочей директории `H6/backend`
3. THE CI_Pipeline SHALL выполнять тесты Backend с помощью pytest в рабочей директории `H6/backend`
4. THE CI_Pipeline SHALL выполнять проверку зависимостей Backend с помощью pip-audit
5. THE CI_Pipeline SHALL выполнять линтинг Frontend с помощью eslint в рабочей директории `H6/frontend`
6. THE CI_Pipeline SHALL выполнять тесты Frontend с помощью vitest в рабочей директории `H6/frontend`
7. THE CI_Pipeline SHALL выполнять проверку зависимостей Frontend с помощью npm audit
8. WHEN изменения находятся только вне `H6/**`, THE CI_Pipeline SHALL пропускать выполнение (path filter)

### Требование 2: CI/CD пайплайн — деплой

**User Story:** Как разработчик, я хочу автоматический деплой при merge в main, чтобы production всегда содержал актуальную версию.

**Роли:** 🤖 генерация deploy workflow | 👤 регистрация Railway, настройка секретов, проверка деплоя

#### Acceptance Criteria

1. WHEN код в `H6/**` попадает в ветку main, THE Deploy_Pipeline SHALL инициировать деплой на Railway
2. THE Deploy_Pipeline SHALL деплоить Backend с Root Directory `H6/backend`
3. THE Deploy_Pipeline SHALL деплоить Frontend с Root Directory `H6/frontend`
4. THE Deploy_Pipeline SHALL деплоить Mock_Server с Root Directory `H6/mock-server`
5. WHEN деплой завершён, THE Deploy_Pipeline SHALL выполнять smoke-test запрос к `/health`
6. IF деплой завершается ошибкой, THEN THE Deploy_Pipeline SHALL сообщать статус failed в GitHub Actions

### Требование 3: Аудит безопасности

**User Story:** Как разработчик, я хочу провести аудит безопасности проекта, чтобы устранить известные уязвимости и задокументировать результаты.

**Роли:** 🤖 OWASP-анализ кода, генерация security_audit.md, патчи | 👤 запуск pip-audit/npm audit, принятие решений по уязвимостям, финальная вычитка

#### Acceptance Criteria

1. THE Security_Auditor SHALL проверять Python-зависимости Backend с помощью pip-audit
2. THE Security_Auditor SHALL проверять npm-зависимости Frontend с помощью npm audit
3. THE Security_Auditor SHALL анализировать код Backend по OWASP Top 10 (XSS, CSRF, SQL injection, broken auth)
4. WHEN уязвимость обнаружена, THE Security_Auditor SHALL документировать её в `H6/security_audit.md` с полями: ID, Severity, Описание, Статус, Коммит
5. WHEN уязвимость имеет доступное исправление, THE Security_Auditor SHALL применять исправление (обновление зависимости или патч кода)
6. THE Security_Auditor SHALL формировать итоговый документ `H6/security_audit.md` с разделами: Методология, Таблица находок, Рекомендации

### Требование 4: OAuth2 авторизация (Google)

**User Story:** Как пользователь, я хочу входить в приложение через Google-аккаунт, чтобы не создавать отдельный пароль.

**Роли:** 🤖 backend routes, миграция Alembic, frontend кнопка, тесты | 👤 Google Cloud Console, Client ID/Secret, test users, ручное тестирование

#### Acceptance Criteria

1. WHEN пользователь нажимает «Войти через Google», THE OAuth_Module SHALL перенаправлять на Google OAuth consent screen с параметром state
2. THE OAuth_Module SHALL хранить одноразовый state в Redis с TTL 10 минут
3. WHEN Google возвращает authorization code, THE OAuth_Module SHALL обменивать code на access token и получать userinfo (email, name)
4. WHEN пользователь с данным email не существует, THE OAuth_Module SHALL создавать нового пользователя с полями oauth_provider и oauth_subject
5. WHEN пользователь с данным email уже существует, THE OAuth_Module SHALL связывать OAuth-данные с существующим аккаунтом
6. WHEN авторизация успешна, THE OAuth_Module SHALL создавать JWT-сессию в Redis и перенаправлять на Frontend
7. IF пользователь отменяет авторизацию на экране Google, THEN THE OAuth_Module SHALL перенаправлять на страницу логина с сообщением об отмене
8. IF параметр state не совпадает с сохранённым в Redis, THEN THE OAuth_Module SHALL возвращать HTTP 400 и логировать попытку
9. THE Backend SHALL содержать Alembic-миграцию добавляющую поля oauth_provider (VARCHAR 32) и oauth_subject (VARCHAR 255) в таблицу users с уникальным индексом

### Требование 5: Интеграция аналитики (Яндекс.Метрика)

**User Story:** Как владелец продукта, я хочу отслеживать поведение пользователей через Яндекс.Метрику, чтобы понимать использование приложения.

**Роли:** 🤖 analytics.ts, trackEvent, SPA pageview | 👤 регистрация счётчика, настройка целей в UI Метрики, проверка «В реальном времени»

#### Acceptance Criteria

1. THE Analytics_Module SHALL загружать скрипт Яндекс.Метрики (tag.js) только в production-режиме
2. THE Analytics_Module SHALL инициализировать счётчик с ID из переменной окружения VITE_YM_COUNTER_ID
3. WHEN пользователь переходит между страницами SPA, THE Analytics_Module SHALL отправлять событие hit с текущим URL
4. WHEN пользователь выполняет целевое действие (login, register, oauth_login, view_ad, blacklist_add), THE Analytics_Module SHALL вызывать reachGoal с соответствующим идентификатором
5. WHILE приложение работает в development-режиме, THE Analytics_Module SHALL пропускать отправку событий без ошибок в консоли
6. THE Frontend SHALL объявлять типы для window.ym в файле vite-env.d.ts

### Требование 6: Мониторинг и Health Check

**User Story:** Как DevOps-инженер, я хочу получать уведомления при недоступности приложения, чтобы быстро реагировать на инциденты.

**Роли:** 🤖 расширение /health, добавление /health/live | 👤 регистрация UptimeRobot, настройка алертов, проверка уведомлений

#### Acceptance Criteria

1. THE Health_Endpoint SHALL отвечать на GET `/health` JSON-объектом с полями: status, version, dependencies (postgres, redis, mock_server)
2. WHEN все зависимости доступны, THE Health_Endpoint SHALL возвращать status "ok" и HTTP 200
3. IF хотя бы одна зависимость недоступна, THEN THE Health_Endpoint SHALL возвращать status "degraded" и HTTP 200 с указанием недоступной зависимости
4. THE Backend SHALL предоставлять лёгкий эндпоинт GET `/health/live` возвращающий `{"status":"ok"}` без проверки зависимостей (для liveness probe)
5. THE Monitoring_Service SHALL проверять доступность production URL `/health` каждые 5 минут
6. WHEN Health_Endpoint не отвечает или возвращает ошибку, THE Monitoring_Service SHALL отправлять алерт на email

### Требование 7: Структурированное логирование

**User Story:** Как разработчик, я хочу структурированные JSON-логи с request ID, чтобы эффективно отлаживать проблемы в production.

**Роли:** 🤖 настройка structlog, middleware X-Request-ID, пример AI-анализа логов | 👤 проверка формата логов, сохранение sample для отчёта

#### Acceptance Criteria

1. THE Logging_Module SHALL форматировать все логи Backend в JSON с полями: timestamp, level, event, request_id
2. THE Logging_Module SHALL генерировать уникальный X-Request-ID для каждого входящего HTTP-запроса через middleware
3. WHEN входящий запрос содержит заголовок X-Request-ID, THE Logging_Module SHALL использовать переданный ID вместо генерации нового
4. THE Logging_Module SHALL прокидывать request_id во все логи в рамках одного запроса
5. THE Logging_Module SHALL использовать уровни логирования: INFO для запросов, WARNING для degraded состояний, ERROR для исключений
6. THE Logging_Module SHALL интегрироваться с Sentry для передачи request_id в контекст ошибок (при наличии Sentry)

### Требование 8: Деплой на Railway

**User Story:** Как разработчик, я хочу развернуть все сервисы на Railway, чтобы приложение было доступно по публичному URL для сдачи ДЗ.

**Роли:** 🤖 Dockerfile проверка/исправление, railway.toml (опционально) | 👤 регистрация Railway, создание проекта, настройка сервисов, переменные окружения, генерация доменов

#### Acceptance Criteria

1. THE Backend SHALL быть развёрнут на Railway с Root Directory `H6/backend` и доступен по HTTPS
2. THE Frontend SHALL быть развёрнут на Railway с Root Directory `H6/frontend` и доступен по HTTPS
3. THE Mock_Server SHALL быть развёрнут на Railway с Root Directory `H6/mock-server` и доступен по внутренней сети Railway (без публичного домена)
4. THE Backend SHALL подключаться к managed PostgreSQL и Redis через переменные Railway
5. WHEN код в `H6/**` попадает в main, THE Railway SHALL автоматически пересобирать и деплоить изменённые сервисы
6. THE Frontend SHALL использовать build-time переменные VITE_API_URL, VITE_YM_COUNTER_ID для подключения к Backend и Метрике

### Требование 9: Документация

**User Story:** Как проверяющий курса, я хочу видеть полную документацию интеграций и процесса использования AI, чтобы оценить выполнение ДЗ.

**Роли:** 🤖 черновики всех MD-файлов | 👤 вычитка, скриншоты, финальная публикация

#### Acceptance Criteria

1. THE Backend SHALL содержать файл `H6/integration_documentation.md` с разделами: CI/CD, OAuth2, Яндекс.Метрика, Мониторинг, Логирование
2. THE Backend SHALL содержать файл `H6/security_audit.md` с разделами: Методология, Таблица находок, Рекомендации
3. THE Backend SHALL содержать файл `H6/README.md` со ссылками на: репозиторий, деплой frontend, деплой backend API, Swagger
4. THE Backend SHALL содержать в документации таблицу «Использование AI» с колонками: Этап, Промпт, Результат, Проверка разработчиком
5. WHEN интеграция добавляется или изменяется, THE документация SHALL обновляться с описанием конфигурации и инструкцией по воспроизведению

### Требование 10 (опционально): Sentry — отслеживание ошибок

**User Story:** Как разработчик, я хочу автоматически получать уведомления об ошибках в production с полным stack trace, чтобы быстро находить и исправлять баги.

**Роли:** 🤖 sentry_sdk.init, ErrorBoundary, before_send фильтр | 👤 регистрация Sentry, DSN, проверка Issues

#### Acceptance Criteria

1. WHERE Sentry интегрирован, THE Backend SHALL инициализировать sentry-sdk с FastAPI и SQLAlchemy integrations
2. WHERE Sentry интегрирован, THE Frontend SHALL инициализировать @sentry/react с browserTracingIntegration
3. WHERE Sentry интегрирован, THE Frontend SHALL оборачивать роутер в ErrorBoundary с fallback UI
4. WHERE Sentry интегрирован, THE Backend SHALL фильтровать PII (password, authorization, cookie) через before_send
5. WHERE Sentry интегрирован, THE Backend SHALL передавать request_id из Logging_Module в контекст Sentry

### Требование 11 (опционально): Prometheus + Grafana

**User Story:** Как DevOps-инженер, я хочу видеть метрики приложения на дашборде, чтобы отслеживать производительность и нагрузку.

**Роли:** 🤖 instrumentator, custom metrics, prometheus.yml, dashboard JSON | 👤 docker compose up, проверка targets, смена пароля Grafana

#### Acceptance Criteria

1. WHERE Prometheus интегрирован, THE Backend SHALL экспортировать метрики на эндпоинте `/metrics` через prometheus-fastapi-instrumentator
2. WHERE Prometheus интегрирован, THE Backend SHALL экспортировать кастомные метрики: p2p_polling_duration_seconds, p2p_ads_active_total, auth_logins_total
3. WHERE Prometheus интегрирован, THE docker-compose.yml SHALL содержать сервисы prometheus и grafana с volume для конфигурации
4. WHERE Grafana интегрирована, THE Grafana SHALL содержать provisioned datasource Prometheus и dashboard с панелями RPS, latency, errors
5. WHERE Prometheus интегрирован, THE эндпоинт `/metrics` SHALL быть недоступен из публичного интернета (только внутренняя сеть Docker)
