# План выполнения домашнего задания H6

**Проект:** MEXC P2P Insight (на базе H5)  
**GitHub (общий репозиторий курса):** [github.com/Rustem81/otus](https://github.com/Rustem81/otus)  
**Папка домашки H6:** [github.com/Rustem81/otus/tree/main/H6](https://github.com/Rustem81/otus/tree/main/H6)  
**Цель:** CI/CD, интеграции (OAuth2, аналитика), аудит безопасности, мониторинг и наблюдаемость (Sentry, Prometheus, Grafana).

> **Monorepo:** в одном репозитории лежат `H1`…`H7_Final`. Код приложения для H6 — в **`H6/backend`**, **`H6/frontend`**. CI/CD и деплой настраиваются с учётом **подпапок**, а не корня репозитория.

---

## Содержание

1. [Обзор и артефакты сдачи](#1-обзор-и-артефакты-сдачи)
2. [Структура репозитория и деплой из monorepo](#2-структура-репозитория-и-деплой-из-monorepo)
3. [Этапы и сроки](#3-этапы-и-сроки)
4. [Распределение ролей: разработчик и AI](#4-распределение-ролей-разработчик-и-ai)
5. [Этап 0. Подготовка проекта](#этап-0-подготовка-проекта)
6. [Этап 1. CI/CD (GitHub Actions)](#этап-1-cicd-github-actions)
7. [Этап 2. Аудит безопасности](#этап-2-аудит-безопасности)
8. [Этап 3. OAuth2 (Google)](#этап-3-oauth2-google)
9. [Этап 4. Яндекс.Метрика (обязательно)](#этап-4-яндексметрика-обязательно)
10. [Этап 5. Sentry — error tracking](#этап-5-sentry--error-tracking)
11. [Этап 6. Prometheus + Grafana](#этап-6-prometheus--grafana)
12. [Этап 7. Uptime-мониторинг и Health Check](#этап-7-uptime-мониторинг-и-health-check)
13. [Этап 8. Структурированное логирование](#этап-8-структурированное-логирование)
14. [Этап 9. Деплой: Railway (все сервисы)](#этап-9-деплой-railway-все-сервисы)
15. [Этап 10. Тестирование и документация](#этап-10-тестирование-и-документация)
16. [Чеклист перед сдачей](#чеклист-перед-сдачей)

---

## 1. Обзор и артефакты сдачи

### Обязательные артефакты (по заданию курса)

| Артефакт | Путь | Описание |
|----------|------|----------|
| Код с интеграциями | `H6/backend/`, `H6/frontend/` | OAuth2, Sentry, метрики, аналитика |
| CI/CD | `.github/workflows/` **в корне** [otus](https://github.com/Rustem81/otus) | Сборка, тесты, линт, деплой (paths: `H6/**`) |
| Интеграции | `H6/integration_documentation.md` | CI/CD, OAuth, Метрика, Sentry, Prometheus/Grafana |
| Аудит безопасности | `H6/security_audit.md` | Уязвимости, исправления, рекомендации |
| README | `H6/README.md` | Ссылки на деплой, быстрый старт |
| Работающий деплой | URL frontend + API | Все интеграции в prod/staging |

### Дополнительный стек наблюдаемости (расширение плана)

| Инструмент | Назначение |
|------------|------------|
| **Sentry** | Отлов необработанных исключений (backend + frontend), алерты, stack trace |
| **Prometheus** | Сбор метрик (HTTP, latency, БД, Redis, polling) |
| **Grafana** | Дашборды и визуализация метрик Prometheus |
| **UptimeRobot** (или аналог) | Внешний ping `/health`, алерты при падении |

---

## 2. Структура репозитория и деплой из monorepo

### 2.1. Как устроен ваш репозиторий

```
otus/                          ← корень: https://github.com/Rustem81/otus
├── .github/workflows/         ← CI/CD здесь (НЕ внутри H6/)
│   ├── h6-ci.yml
│   └── h6-deploy.yml
├── .gitignore
├── H1/ … H5/                  ← прошлые домашки
├── H6/                        ← эта домашка
│   ├── backend/
│   ├── frontend/
│   ├── mock-server/
│   ├── docker-compose.yml
│   ├── task/
│   │   └── work_plan.md
│   ├── integration_documentation.md
│   ├── security_audit.md
│   └── README.md
└── H7_Final/
```

Сдача на OTUS: ссылка на репозиторий + папка [H6](https://github.com/Rustem81/otus/tree/main/H6) + URL деплоя frontend/API.

### 2.2. Ansible — нужен ли?

| Сценарий | Нужен | Что использовать |
|----------|-------|------------------|
| Весь стек на **Railway** | **Нет** | Railway UI + GitHub Actions |
| Полный стек на **своём VPS** | По желанию | Ansible playbook |
| Только CI (тесты без деплоя) | Нет | GitHub Actions |

**Решение для H6:** Весь стек на **Railway** (backend + frontend + PostgreSQL + Redis + mock-server). Ansible не нужен.

### 2.3. Деплой из monorepo на Railway

Railway поддерживает monorepo: для каждого сервиса указывается **Root Directory** и **Dockerfile path**.

| Сервис | Root Directory | Dockerfile | Порт |
|--------|---------------|------------|------|
| frontend | `H6/frontend` | `Dockerfile` | 3000 |
| backend | `H6/backend` | `Dockerfile` | 8000 |
| mock-server | `H6/mock-server` | `Dockerfile` | 8001 |
| PostgreSQL | — (managed plugin) | — | 5432 |
| Redis | — (managed plugin) | — | 6379 |

**Настройка в Railway UI:**
1. New Project → Deploy from GitHub → `Rustem81/otus`
2. Для каждого сервиса: Settings → Root Directory → `H6/backend` (и т.д.)
3. Plugins: Add PostgreSQL, Add Redis
4. Variables: задать DATABASE_URL, REDIS_URL и т.д. (Railway автоматически подставляет для plugins)

**Автодеплой:** Railway деплоит при push в `main`. Watch Paths можно ограничить папкой `H6/`.

### 2.4. Path filters в CI (запуск только при изменениях H6)

В `.github/workflows/h6-ci.yml`:

```yaml
on:
  push:
    paths:
      - 'H6/**'
      - '.github/workflows/h6-*.yml'
  pull_request:
    paths:
      - 'H6/**'
```

Так pipeline не будет запускаться при правках только в `H1`…`H5`.

### 2.5. Переменные окружения: где задавать

| Переменная | Локально | Railway (backend) | Railway (frontend) |
|------------|----------|-------------------|-------------------|
| `VITE_API_URL` | `H6/frontend/.env` | — | Build-time variable |
| `VITE_YM_COUNTER_ID` | `.env` | — | Build-time variable |
| `VITE_SENTRY_DSN` | `.env` | — | Build-time variable |
| `DATABASE_URL` | `H6/.env` | Auto from PostgreSQL plugin | — |
| `REDIS_URL` | `H6/.env` | Auto from Redis plugin | — |
| `SECRET_KEY`, `GOOGLE_*` | `H6/.env` | Service variables | — |
| `SENTRY_DSN_BACKEND` | `H6/.env` | Service variables | — |
| `P2P_MOCK_BASE_URL` | `H6/.env` | Internal URL mock-server | — |

---

## 3. Этапы и сроки

| № | Этап | Ориентир | Зависимости |
|---|------|----------|-------------|
| 0 | Подготовка H6 из H5 | 0.5 дня | — |
| 1 | CI/CD | 1–2 дня | 0 |
| 2 | Аудит безопасности | 1 день | 0 |
| 3 | OAuth2 Google | 1 день | 0, 9 (redirect URI) |
| 4 | Яндекс.Метрика | 0.5 дня | 9 (prod URL) |
| 5 | Sentry | 0.5–1 день | 0 |
| 6 | Prometheus + Grafana | 1–2 дня | 0, docker-compose |
| 7 | Uptime + Health | 0.5 дня | 6, 9 |
| 8 | JSON-логирование | 0.5 дня | 5 |
| 9 | Деплой prod/staging | 1 день | 1 |
| 10 | Тесты + документация | 1 день | 1–9 |

**Итого:** ~7–9 рабочих дней.

---

## 4. Распределение ролей: разработчик и AI

В каждом этапе ниже есть подразделы **👤 Разработчик** и **🤖 С помощью AI (Cursor)**.  
Общее правило: **секреты, аккаунты и прод-инфраструктуру** настраивает только человек; **код, конфиги и документацию** — в основном с AI, с обязательной проверкой и ручным тестом разработчиком.

### Что всегда делает разработчик (без делегирования AI)

| Область | Почему только человек |
|---------|------------------------|
| Регистрация в сервисах | Google Cloud, GitHub, Sentry, Metrika, UptimeRobot, хостинг — нужны ваши учётные записи |
| Секреты и ключи | Client ID/Secret, DSN, токены деплоя — в `.env` и GitHub Secrets, **не в git** |
| Выбор хостинга и тарифов | Railway — решение и оплата за вами |
| Ручное тестирование в браузере | OAuth flow, UI, Метрика «в реальном времени» |
| Code review | Проверить сгенерированный код перед merge |
| Сдача ДЗ | Ссылки на репозиторий и деплой на платформе курса |
| Скриншоты для отчёта | Grafana, Sentry Issues, успешный CI — для документации и защиты |

### Что обычно делается с помощью AI (Cursor)

| Область | Типичный результат |
|---------|-------------------|
| Генерация кода интеграций | OAuth endpoints, Sentry init, structlog, custom metrics |
| Конфигурационные файлы | `ci.yml`, `prometheus.yml`, Grafana provisioning |
| Миграции БД | Alembic для полей `oauth_provider`, `oauth_subject` |
| Рефакторинг и исправления | По ошибкам CI, линтера, pytest |
| Аудит безопасности (черновик) | OWASP-чеклист, разбор `auth`/`middleware` |
| Документация (черновик) | `integration_documentation.md`, `security_audit.md` |
| Промпты и примеры | Для отчёта «использование AI» по заданию H6 |
| Отладка | Разбор логов, stack trace из Sentry, failed GitHub Actions |

### Сводная таблица по этапам

| Этап | 👤 Разработчик | 🤖 С помощью AI |
|------|----------------|-----------------|
| **0. Подготовка** | Копирование H5→H6, `git checkout -b`, создание `.env` | Структура каталогов `monitoring/`, шаблон `.env.example` |
| **1. CI/CD** | Репозиторий GitHub, Secrets, просмотр Actions | `ci.yml`, `deploy.yml`, исправление падающих job |
| **2. Security** | Запуск `npm audit` / `pip-audit`, решение что обновлять | OWASP-аудит кода, черновик `security_audit.md`, патчи |
| **3. OAuth2** | Google Console (проект, consent, Client ID, redirect URI), test users | Backend routes, миграция, кнопка на login, тесты |
| **4. Яндекс.Метрика** | Регистрация на metrika.yandex.ru, счётчик, **настройка целей** в UI, проверка «В реальном времени», скриншот | `analytics.ts`, скрипт счётчика, `trackEvent`, Railway env |
| **5. Sentry** | Регистрация sentry.io, копирование DSN, проверка Issues в UI | `sentry_sdk.init`, `@sentry/react`, ErrorBoundary, фильтр PII |
| **6. Prometheus+Grafana** | `docker compose up`, открыть :9090/:3001, сменить пароль admin | instrumentator, custom metrics, `prometheus.yml`, dashboard JSON |
| **7. Uptime** | Регистрация UptimeRobot, URL prod `/health`, email-алерты | Расширение `/health`, `/health/live` |
| **8. Логи** | Сохранить sample логов для отчёта | structlog, middleware request_id, AI-анализ логов в доке |
| **9. Деплой** | Регистрация Railway, привязка `Rustem81/otus`, Root Directory для каждого сервиса, env | `h6-deploy.yml`, path filters, исправление сборки |
| **10. Документация** | Финальная вычитка, скриншоты, публикация ссылок | Черновики MD, README, список промптов для отчёта |

### Как работать с AI на практике (рекомендуемый цикл)

```
1. Разработчик формулирует задачу (1–3 предложения + контекст файлов)
2. AI генерирует код/конфиг
3. Разработчик запускает локально / смотрит diff / правит вручную при необходимости
4. Разработчик коммитит осмысленным сообщением
5. В integration_documentation.md — сохранить промпт и краткий результат (для зачёта)
```

### Условные обозначения в этапах

- **👤** — действия разработчика (ручные, вне IDE или в веб-консолях)
- **🤖** — запросы в Cursor / Chat с последующей проверкой кода человеком

---

## Этап 0. Подготовка проекта

### 👤 Разработчик

- Скопировать каталоги H5 → H6 (команды ниже) или создать ветку `feature/h6-integrations`
- Создать локальный `.env` из `.env.example` (файл **не коммитить**)
- Убедиться, что `docker compose up` из H6 поднимает тот же стек, что и H5
- Зафиксировать в README H6, что проект — продолжение H5

### 🤖 С помощью AI (Cursor)

- Сгенерировать целевую структуру `H6/monitoring/` (prometheus, grafana provisioning)
- Дополнить `.env.example` переменными OAuth, Sentry, Metrika, Prometheus
- Подготовить черновик `H6/README.md` со ссылкой на `task/work_plan.md`

### 0.1. Скопировать код из H5

```bash
# Из корня репозитория OTUS
xcopy /E /I H5\backend H6\backend
xcopy /E /I H5\frontend H6\frontend
xcopy /E /I H5\mock-server H6\mock-server
copy H5\docker-compose.yml H6\docker-compose.yml
copy H5\.env.example H6\.env.example
```

Или через git: отдельная ветка `feature/h6-integrations` от `main`.

### 0.2. Расширить `docker-compose.yml`

Добавить сервисы (на этапах 5–6):

```yaml
# prometheus, grafana — см. Этап 6
# Опционально: sentry не в compose (SaaS), только DSN в .env
```

### 0.3. Обновить `.env.example`

Добавить переменные (заполнить реальные значения только в `.env`, не коммитить):

```env
# OAuth2 Google
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Sentry
SENTRY_DSN_BACKEND=
SENTRY_DSN_FRONTEND=
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1

# Analytics
VITE_YM_COUNTER_ID=

# Prometheus (внутренний scrape)
METRICS_ENABLED=true
```

### 0.4. Структура каталогов H6 после подготовки

```
otus/                              # https://github.com/Rustem81/otus
├── .github/workflows/
│   ├── h6-ci.yml
│   └── h6-deploy.yml
├── H1/ … H5/
└── H6/
    ├── backend/
    ├── frontend/
    ├── mock-server/
    ├── monitoring/
    │   ├── prometheus/prometheus.yml
    │   └── grafana/...
    ├── docker-compose.yml
    ├── integration_documentation.md
    ├── security_audit.md
    ├── README.md
    └── task/
        ├── task.md
        └── work_plan.md
```

---

## Этап 1. CI/CD (GitHub Actions)

### 👤 Разработчик

- Создать/привязать репозиторий на GitHub, сделать `git push`
- В **Settings → Secrets and variables → Actions** добавить все секреты деплоя
- Зарегистрироваться на Railway, создать проект
- Открыть вкладку **Actions** после push — убедиться, что pipeline зелёный
- При падении job — скопировать лог ошибки (для AI или ручного fix)
- После merge в `main` — проверить, что prod URL открывается (`curl /health`)

### 🤖 С помощью AI (Cursor)

- Сгенерировать `.github/workflows/ci.yml` (lint, test, audit)
- Сгенерировать `.github/workflows/deploy.yml` под выбранный хостинг
- Исправить пути monorepo (`H6/backend`, `H6/frontend`), кэш npm/pip
- Добавить smoke-test шаг после деплоя
- Подготовить фрагмент для `integration_documentation.md` (схема pipeline)

**Пример промпта:**  
> «Сгенерируй GitHub Actions для H6: backend FastAPI (ruff, pytest, pip-audit), frontend React Vite (eslint, vitest, npm audit). Отдельный deploy.yml на push в main: все сервисы на Railway.»

### 1.1. Репозиторий GitHub (у вас уже есть)

Используется существующий репозиторий: **[Rustem81/otus](https://github.com/Rustem81/otus)**.

1. Локально: `git remote -v` — должен указывать на `https://github.com/Rustem81/otus.git`  
2. Работа в ветке: `git checkout -b feature/h6-integrations`  
3. Коммиты только в `H6/` (+ workflows в `.github/workflows/`)  
4. `git push -u origin feature/h6-integrations` → Pull Request в `main`  
5. После merge — Actions и Railway деплоят из `main`

### 1.2. Файл `.github/workflows/h6-ci.yml` (в **корне** репозитория)

**Триггеры:** `push` и `pull_request` на ветки `main`, `develop`.

**Jobs:**

| Job | Шаги |
|-----|------|
| `backend-lint-test` | `working-directory: H6/backend` → pip → ruff → pytest |
| `backend-security` | `working-directory: H6/backend` → pip-audit |
| `frontend-lint-test` | `working-directory: H6/frontend` → npm ci → lint → test |
| `frontend-audit` | `working-directory: H6/frontend` → npm audit |

**Path filter:** запуск только при изменениях `H6/**` (см. [раздел 2.4](#24-path-filters-в-ci-запуск-только-при-изменениях-h6)).

### 1.3. Файл `.github/workflows/h6-deploy.yml`

**Триггер:** `push` только в `main`.

**Шаги деплоя (рекомендуемая схема):**

| Компонент | Платформа | Секреты в GitHub |
|-----------|----------|------------------|
| Frontend | Railway | `RAILWAY_TOKEN`, `VITE_API_URL` |
| Backend | Railway | `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `GOOGLE_*`, `SENTRY_DSN_*` |

**После деплоя:** smoke-test `curl https://<api>/health`.

### 1.4. GitHub Secrets

В репозитории [Rustem81/otus](https://github.com/Rustem81/otus): **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `SENTRY_DSN_BACKEND`, `SENTRY_DSN_FRONTEND`
- `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`
- `RAILWAY_TOKEN`

### 1.5. Проверка

1. Сделать тестовый коммит с пустым комментарием в README  
2. Убедиться, что CI зелёный  
3. После merge в `main` — деплой прошёл, приложение открывается

---

## Этап 2. Аудит безопасности

### 👤 Разработчик

- Локально выполнить `pip-audit` и `npm audit`, сохранить вывод в файл
- Принять решение по каждой уязвимости: обновить / принять риск / ложное срабатывание
- Проверить вручную: CORS, cookies, CSRF, что `.env` не в git
- Вычитать и подписать итоговый `security_audit.md` перед сдачей
- Закоммитить исправления с понятными сообщениями

### 🤖 С помощью AI (Cursor)

- Промпт по OWASP Top 10 для `backend/app/api`, `middleware`, `services/auth`
- Составить таблицу находок для `security_audit.md`
- Предложить патчи (secure headers в nginx, `before_send` в Sentry, OAuth state)
- Объяснить, как безопасно обновить зависимости с breaking changes

**Пример промпта:**  
> «Проведи аудит безопасности FastAPI-проекта H6/backend по OWASP Top 10. Укажи файл:строка, severity, рекомендацию. Отдельно проверь JWT-сессии в Redis и CSRF middleware.»

### 2.1. Зависимости

```bash
# Backend
cd H6/backend
pip install pip-audit
pip-audit

# Frontend
cd H6/frontend
npm audit
npm audit fix   # только после просмотра diff
```

### 2.3. Чеклист исправлений

| Область | Действие |
|---------|----------|
| Секреты | Только в `.env` / GitHub Secrets |
| Пароли | bcrypt, минимум 8 символов |
| Сессии | HttpOnly cookie, Secure в prod, SameSite=Lax |
| CORS | Белый список origin (не `*` в prod) |
| CSRF | Уже есть middleware — проверить исключения только для `/health`, OAuth callback |
| Headers | nginx: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` |
| Rate limit | Сохранить на auth endpoints |
| OAuth state | Одноразовый `state` в Redis, TTL 10 мин |

### 2.4. Артефакт `security_audit.md`

Структура:

1. Методология (инструменты + AI)  
2. Таблица находок: ID | Severity | Описание | Статус | Коммит  
3. Рекомендации на будущее  

---

## Этап 3. OAuth2 (Google)

### 👤 Разработчик

- Пройти все шаги в Google Cloud Console (раздел 3.1 ниже) — **только в браузере**
- Скопировать Client ID и Client Secret в `.env` и GitHub Secrets
- Добавить свой Google-email в **Test users** (пока приложение в Testing)
- Проверить вход в браузере: успех, отмена, пользователь не из test users
- После деплоя — **добавить prod redirect URI** в Credentials (URI должны совпадать побайтно)
- Решить политику «email уже зарегистрирован по паролю» (связка или отдельные аккаунты)

### 🤖 С помощью AI (Cursor)

- Alembic-миграция: `oauth_provider`, `oauth_subject` в `users`
- Роуты `GET /auth/google`, `GET /auth/google/callback` (authlib/httpx)
- Хранение `state` в Redis, создание JWT-сессии как при обычном login
- Кнопка «Войти через Google» на `login.tsx`, страница `/auth/callback`
- Unit/integration тесты callback (mock Google token endpoint)
- Раздел в `integration_documentation.md` с описанием flow

**Пример промпта:**  
> «Добавь Google OAuth2 в H6/backend: authlib, state в Redis, callback создаёт/находит User. Frontend: кнопка на login.tsx. Redirect URI: http://localhost:8000/api/v1/auth/google/callback.»

### 3.1. Регистрация приложения в Google Cloud Console

#### Шаг 1. Войти в консоль

1. Открыть https://console.cloud.google.com/  
2. Войти под Google-аккаунтом (желательно тот же, что для деплоя)

#### Шаг 2. Создать проект

1. Вверху: выпадающий список проектов → **New Project**  
2. **Project name:** `MEXC P2P Insight` (или `mexc-p2p-dev`)  
3. **Create** → дождаться создания → выбрать этот проект

#### Шаг 3. Настроить экран согласия (OAuth consent screen)

1. Меню ☰ → **APIs & Services** → **OAuth consent screen**  
2. **User Type:**  
   - **External** — для тестирования с любым Google-аккаунтом (до 100 тестовых пользователей)  
   - **Internal** — только если у вас Google Workspace  
3. **Create**  
4. Заполнить обязательные поля:  
   - **App name:** `MEXC P2P Insight`  
   - **User support email:** ваш email  
   - **Developer contact information:** ваш email  
5. **Scopes** → **Add or Remove Scopes** → добавить:  
   - `openid`  
   - `.../auth/userinfo.email`  
   - `.../auth/userinfo.profile`  
6. **Save and Continue**  
7. **Test users** (для External в режиме Testing):  
   - **Add users** → добавить email(ы), с которыми будете тестировать вход  
8. **Save and Continue** → **Back to Dashboard**

> Пока приложение в статусе **Testing**, войти смогут только добавленные test users. Для публичного доступа нужна верификация Google (для учебного проекта достаточно Testing).

#### Шаг 4. Создать OAuth 2.0 Client ID

1. **APIs & Services** → **Credentials**  
2. **+ Create Credentials** → **OAuth client ID**  
3. **Application type:** `Web application`  
4. **Name:** `MEXC P2P Web Client`  
5. **Authorized JavaScript origins** (откуда идёт redirect на Google — обычно frontend):

   | Среда | URL |
   |-------|-----|
   | Local dev | `http://localhost:5173` |
   | Local dev (alt) | `http://localhost:3000` |
   | Production | `https://<your-frontend-domain>` |

6. **Authorized redirect URIs** (куда Google вернёт `code` — **backend callback**):

   | Среда | URL |
   |-------|-----|
   | Local | `http://localhost:8000/api/v1/auth/google/callback` |
   | Production | `https://<your-api-domain>/api/v1/auth/google/callback` |

7. **Create**  
8. Скопировать **Client ID** и **Client Secret** → в `.env` (не в git!)

#### Шаг 5. Включить Google+ API (если потребуется)

Обычно для userinfo достаточно scopes из шага 3. Если ошибка `access_denied` — проверить, что в Credentials выбран тип **Web application**, а redirect URI **совпадает побайтно** с тем, что в коде.

### 3.2. Реализация на Backend (FastAPI)

#### Зависимости

```
authlib>=1.3.0
httpx>=0.27.0
```

#### Новые эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/auth/google` | Генерация `state`, redirect на Google |
| GET | `/api/v1/auth/google/callback` | Обмен `code` → токен → userinfo → JWT-сессия |

#### Логика callback

1. Проверить `state` (сравнить с Redis)  
2. Обменять `code` на access token (POST `https://oauth2.googleapis.com/token`)  
3. GET `https://www.googleapis.com/oauth2/v2/userinfo`  
4. Найти `User` по `email` или создать (`oauth_provider=google`, `oauth_subject=sub`)  
5. Создать сессию в Redis (как при обычном login)  
6. Redirect на frontend: `https://<frontend>/auth/callback?success=1` или установить HttpOnly cookie

#### Миграция Alembic

```sql
ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(32);
ALTER TABLE users ADD COLUMN oauth_subject VARCHAR(255);
CREATE UNIQUE INDEX ix_users_oauth ON users (oauth_provider, oauth_subject)
  WHERE oauth_provider IS NOT NULL;
```

### 3.3. Реализация на Frontend

1. На странице `login.tsx` — кнопка **«Войти через Google»**  
2. По клику: `window.location.href = `${API_URL}/api/v1/auth/google``  
3. Страница `/auth/callback` — обработка успеха/ошибки, редирект на `/` или `/onboarding`

### 3.4. Тестирование OAuth2

| Сценарий | Ожидание |
|----------|----------|
| Успешный вход (test user) | Редирект в приложение, `/api/v1/auth/me` → 200 |
| Отмена на экране Google | Редирект с `error=access_denied`, сообщение в UI |
| Неверный `state` | 400, лог в Sentry |
| Email уже есть (local + Google) | Связать аккаунт или показать понятную ошибку |
| Пользователь не в test users | `access_denied` (в режиме Testing) |

### 3.5. OAuth2 Yandex ID (опционально, второй провайдер)

Если нужен второй сервис для зачёта:

1. https://oauth.yandex.ru/ → **Создать приложение**  
2. Права: доступ к email, имени, аватару  
3. **Callback URL:** `https://<api>/api/v1/auth/yandex/callback`  
4. Аналогичный flow на backend

---

## Этап 4. Яндекс.Метрика (обязательно)

> **Требование H6:** аналитика — одна из обязательных интеграций (минимум 2: OAuth2 + аналитика). Яндекс.Метрика — основной выбор для этого проекта.

### 👤 Разработчик

- Пройти регистрацию и настройку счётчика (раздел 4.1) — **только в браузере**
- Создать **цели** в интерфейсе Метрики (раздел 4.2) — имена должны совпадать с `reachGoal` в коде
- Добавить `VITE_YM_COUNTER_ID` в Railway → frontend service → Variables
- После деплоя на Railway — указать в счётчике **реальный URL** `https://<frontend>.up.railway.app`
- Проверить визиты и цели в отчёте **«В реальном времени»**
- Сделать **2 скриншота** для отчёта: счётчик в списке + цели/визиты в реальном времени
- Убедиться, что на localhost счётчик **не мешает** (отключён или отдельный тестовый счётчик)

### 🤖 С помощью AI (Cursor)

- Файл `H6/frontend/src/lib/analytics.ts` — `initMetrika()`, `trackEvent()`, `trackPageView()`
- Компонент `MetrikaProvider` или вставка в `index.html` / `main.tsx`
- Вызовы `trackEvent` в `login.tsx`, `main.tsx`, `blacklist.tsx` и т.д.
- Типы `window.ym` в `vite-env.d.ts`
- Раздел **«Яндекс.Метрика»** в `H6/integration_documentation.md` (таблица целей)

**Пример промпта:**  
> «Интегрируй Яндекс.Метрику в H6/frontend (Vite React): VITE_YM_COUNTER_ID, загрузка tag.js только в production, reachGoal через trackEvent. Добавь pageview на смену роута.»

---

### 4.1. Регистрация и настройка счётчика (пошагово)

#### Шаг 1. Вход

1. Открыть https://metrika.yandex.ru/  
2. Войти под **Яндекс-ID** (тот же аккаунт, что для почты/Диска)

#### Шаг 2. Добавить счётчик

1. Кнопка **«Добавить счётчик»**  
2. Заполнить поля:

| Поле | Значение для H6 |
|------|-----------------|
| Имя счётчика | `MEXC P2P Insight` |
| Адрес сайта | Сначала `http://localhost:5173` (для отладки), после деплоя — `https://<frontend>.up.railway.app` |
| Часовой пояс | Ваш (например, Москва) |
| Валюта | RUB (опционально) |

3. **Создать счётчик**

#### Шаг 3. Настройки счётчика (рекомендуется)

В карточке счётчика → **Настройки**:

- **Вебвизор** — включить (удобно для отладки UX, опционально для ДЗ)  
- **Карта кликов** — включить (опционально)  
- **Автоматические цели** — можно включить «Просмотр страниц», но **основные цели** лучше задать вручную (раздел 4.2)  
- **Фильтры** → исключить свои визиты с office IP (опционально)

#### Шаг 4. Скопировать номер счётчика

1. На главной Метрики — колонка **«Номер»** (например `12345678`)  
2. Записать в:
   - локально: `H6/frontend/.env` → `VITE_YM_COUNTER_ID=12345678`
   - Railway: frontend service → Variables → `VITE_YM_COUNTER_ID`

#### Шаг 5. Код счётчика (справочно)

В Метрика → **Настройка** → **Код счётчика** — там официальный snippet.  
В проекте его заменяет инициализация через Vite/env (генерирует AI), но номер счётчика **тот же**.

Документация: [Справка Яндекс.Метрики](https://yandex.ru/support/metrica/).

---

### 4.2. Настройка целей в интерфейсе Метрики

Цели типа **«JavaScript-событие»** (идентификатор = имя, которое передаёте в `reachGoal`).

1. Счётчик → **Цели** → **Добавить цель**  
2. Тип: **JavaScript-событие**  
3. Создать цели с идентификаторами:

| Идентификатор цели | Описание | Где вызывать в приложении |
|--------------------|----------|---------------------------|
| `login` | Успешный вход по email | После `POST /auth/login` OK |
| `register` | Регистрация | После регистрации OK |
| `oauth_login` | Вход через Google | После OAuth callback OK |
| `view_ad` | Просмотр объявления | Открытие `AdDetailDialog` |
| `blacklist_add` | Блокировка мерчанта | Успешный `POST /blacklist` |
| `llm_explain` | Запрос AI-объяснения | Успешный ответ scoring/explain |

4. **Сохранить** каждую цель  
5. Важно: идентификатор в Метрике и строка в `trackEvent('login')` должны **совпадать**.

---

### 4.3. Интеграция во Frontend (что делает AI)

**Файлы:**

- `H6/frontend/src/lib/analytics.ts` — логика  
- `H6/frontend/src/main.tsx` — вызов `initMetrika()`  
- `H6/frontend/src/vite-env.d.ts` — `VITE_YM_COUNTER_ID`

**Пример API (ориентир):**

```typescript
// H6/frontend/src/lib/analytics.ts
const COUNTER_ID = import.meta.env.VITE_YM_COUNTER_ID;

export function initMetrika() {
  if (!import.meta.env.PROD || !COUNTER_ID) return;
  // загрузка https://mc.yandex.ru/metrika/tag.js + ym(COUNTER_ID, 'init', ...)
}

export function trackEvent(goal: string, params?: Record<string, unknown>) {
  if (!import.meta.env.PROD || !COUNTER_ID) return;
  if (typeof window.ym === 'function') {
    window.ym(Number(COUNTER_ID), 'reachGoal', goal, params);
  }
}
```

**Просмотры страниц (SPA):** при смене роута React Router вызывать `ym(id, 'hit', url)` — иначе в SPA будет только первый pageview.

---

### 4.4. Переменные окружения

| Переменная | Где задать | Пример |
|------------|------------|--------|
| `VITE_YM_COUNTER_ID` | `H6/frontend/.env` (локально, не в git) | `12345678` |
| `VITE_YM_COUNTER_ID` | Railway → frontend service → Variables | тот же номер |

После изменения env на Railway — сервис автоматически пересобирается.

---

### 4.5. Проверка (чеклист разработчика)

1. Деплой frontend на Railway открывается по HTTPS  
2. В Метрике указан **тот же домен**, что у Railway frontend  
3. **Отчёты → В реальном времени** — открыть сайт в другой вкладке → появился визит (1–3 мин)  
4. Выполнить **логин** → в реальном времени или **Отчёты → Цели** — сработала цель `login`  
5. Выполнить `view_ad`, `blacklist_add` — цели срабатывают  
6. На `localhost` при `npm run dev` — в консоли нет ошибок; события **не отправляются** (если `PROD` only)  
7. Скриншоты сохранены в `H6/report.md` или приложены к сдаче  

**Частые проблемы:**

| Проблема | Решение |
|----------|---------|
| Нет визитов | Блокировщик рекламы, неверный домен в счётчике, не тот `VITE_YM_COUNTER_ID` на Vercel |
| Визиты есть, целей нет | Цель не создана в Метрике или другое имя события |
| Цели на localhost | Отдельный счётчик для dev или тестировать только на Vercel prod |

---

### 4.6. Связь с деплоем (порядок работ)

```
Деплой Railway (Этап 9) → узнать URL frontend → обновить «Адрес сайта» в Метрике
→ добавить VITE_YM_COUNTER_ID в Railway frontend variables → redeploy → проверка (4.5)
```

Метрику **можно** подключить в коде раньше, но **финальную проверку** делать только после появления prod-URL.

---

## Этап 5. Sentry — error tracking

### 👤 Разработчик

- Зарегистрироваться на https://sentry.io/, создать 2 проекта (Python + React)
- Скопировать DSN в `.env` / GitHub Secrets / env хостинга
- Настроить алерты (email при новом issue) — по желанию
- **Вручную** вызвать тестовую ошибку на backend и frontend, убедиться в Issues
- Проверить, что в Sentry **не попадают** пароли и полные токены
- Скриншот issue со stack trace — для отчёта H6

### 🤖 С помощью AI (Cursor)

- `sentry_sdk.init` в `main.py` с FastAPI + SQLAlchemy integrations
- `@sentry/react` + `ErrorBoundary` в `main.tsx`
- `before_send` — маскирование `password`, `authorization`, cookie
- Dev-only endpoint или кнопка «Test Sentry» (отключить в prod)
- Опционально: шаг `sentry-cli` в deploy workflow для releases
- Раздел «Sentry» в `integration_documentation.md`

**Пример промпта:**  
> «Подключи Sentry к H6 backend (FastAPI) и frontend (React 19). before_send фильтрует PII. ErrorBoundary с fallback UI.»

### 5.1. Регистрация в Sentry

1. https://sentry.io/ → Sign up (бесплатный Developer план)  
2. **Create Project** → платформа **Python** (для backend)  
3. Скопировать **DSN** → `SENTRY_DSN_BACKEND`  
4. **Create Project** → **React** (для frontend)  
5. DSN → `SENTRY_DSN_FRONTEND`  
6. **Settings** → **Projects** → для каждого:  
   - **Environments:** `development`, `staging`, `production`  
   - **Alerts:** New issue → Email/Slack (опционально)

### 5.2. Backend (FastAPI)

```bash
pip install sentry-sdk[fastapi]
```

```python
# app/main.py (до создания app)
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

if settings.SENTRY_DSN_BACKEND:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN_BACKEND,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
    )
```

- Не отправлять в Sentry: пароли, полные JWT, PII без необходимости  
- `before_send` — фильтрация чувствительных полей  
- Тест: `GET /api/v1/debug/sentry-test` (только в dev) → проверить issue в Sentry

### 5.3. Frontend (React)

```bash
npm install @sentry/react
```

```typescript
// src/main.tsx
import * as Sentry from '@sentry/react';

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.MODE,
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: 0.1,
  });
}
```

Обернуть роутер в `Sentry.ErrorBoundary` с fallback UI.

### 5.4. Связка с CI/CD

- В prod secrets: `SENTRY_DSN_BACKEND`, `VITE_SENTRY_DSN`  
- Release tracking (опционально): `sentry-cli releases new $GITHUB_SHA` в deploy job

### 5.5. Проверка

1. Вызвать тестовую ошибку на backend и frontend  
2. В Sentry → **Issues** — два события с stack trace  
3. Убедиться, что `environment=production` на prod

---

## Этап 6. Prometheus + Grafana

### 👤 Разработчик

- Запустить `docker compose up` с prometheus + grafana
- Открыть http://localhost:9090/targets — target `fastapi` в статусе **UP**
- Открыть Grafana http://localhost:3001 — **сменить пароль admin**
- Import community dashboard или открыть свой `mexc-p2p.json`
- Убедиться, что `/metrics` **не торчит в публичный интернет** на prod (VPN, internal network, basic auth)
- Скриншот дашборда (RPS, latency, polling) — для документации

### 🤖 С помощью AI (Cursor)

- `prometheus-fastapi-instrumentator` + endpoint `/metrics`
- Кастомные метрики: `p2p_polling_*`, `p2p_ads_active_total`, `auth_logins_total`, `llm_requests_total`
- Файлы `monitoring/prometheus/prometheus.yml`, сервисы в `docker-compose.yml`
- Grafana provisioning: datasource + dashboard JSON
- nginx snippet: закрыть `/metrics` снаружи
- Раздел в `integration_documentation.md` (порты, scrape interval, список метрик)

**Пример промпта:**  
> «Добавь Prometheus metrics в H6/backend: instrumentator на /metrics, custom counters для polling и LLM. Создай docker-compose сервисы prometheus+grafana и dashboard JSON.»

### 6.1. Архитектура

```
FastAPI (/metrics) ──scrape──► Prometheus ──datasource──► Grafana
     │                              │
     └── redis, postgres exporters (опционально)
```

### 6.2. Метрики Backend

Установить:

```bash
pip install prometheus-fastapi-instrumentator
```

```python
# app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

**Кастомные метрики (примеры):**

| Метрика | Тип | Описание |
|---------|-----|----------|
| `p2p_polling_duration_seconds` | Histogram | Время цикла polling |
| `p2p_ads_active_total` | Gauge | Число активных объявлений |
| `p2p_polling_errors_total` | Counter | Ошибки опроса mock/P2P API |
| `llm_requests_total` | Counter | Запросы к OpenAI |
| `auth_logins_total` | Counter | Входы (label: `method=password\|google`) |

### 6.3. Файл `monitoring/prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "fastapi"
    metrics_path: /metrics
    static_configs:
      - targets: ["backend:8000"]

  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
```

### 6.4. Docker Compose — сервисы мониторинга

Добавить в `docker-compose.yml` (или `docker-compose.monitoring.yml`):

```yaml
  prometheus:
    image: prom/prometheus:v2.52.0
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:11.0.0
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin  # сменить в prod!
    volumes:
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - prometheus
```

> **Важно:** `/metrics` не публиковать в интернет без auth. В prod — только внутренняя сеть Docker/VPN или nginx basic auth.

### 6.5. Grafana — первичная настройка

1. Открыть http://localhost:3001  
2. Логин: `admin` / `admin` (сменить пароль)  
3. **Connections** → **Data sources** → **Prometheus**  
   - URL: `http://prometheus:9090` (внутри compose)  
4. **Dashboards** → **Import**  
   - ID **16110** или **16237** — FastAPI/Starlette (community)  
   - Либо свой `monitoring/grafana/dashboards/mexc-p2p.json`

**Панели дашборда MEXC P2P (минимум):**

- RPS и latency (`http_request_duration_seconds`)  
- 4xx/5xx rate  
- `p2p_ads_active_total`  
- `p2p_polling_errors_total`  
- Health: postgres/redis (через custom gauge или blackbox)

### 6.6. Проверка

```bash
docker compose up -d prometheus grafana backend
curl http://localhost:8000/metrics   # метрики есть
open http://localhost:9090/targets    # fastapi — UP
open http://localhost:3001            # графики отображаются
```

---

## Этап 7. Uptime-мониторинг и Health Check

### 👤 Разработчик

- Зарегистрироваться на UptimeRobot (или аналог)
- Создать HTTP-монитор на prod URL `https://<api>/health`
- Настроить email/Telegram-алерт при downtime
- Искусственно остановить backend (локально или staging) — убедиться, что алерт приходит
- Проверить, что UptimeRobot не бьёт слишком часто по `/metrics` (только `/health`)

### 🤖 С помощью AI (Cursor)

- Расширить ответ `/health` (version, mock_server status)
- Добавить лёгкий `GET /health/live` для liveness probe
- Опционально: Grafana alert rule `up == 0`
- Описание мониторинга в `integration_documentation.md`

**Пример промпта:**  
> «Расширь /health в H6/backend: проверка mock-server, поле version из settings. Добавь /health/live без проверки БД.»

### 7.1. Расширить `/health` (уже есть в H5)

Добавить в ответ (опционально):

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

Отдельный лёгкий эндпоинт для UptimeRobot: `GET /health/live` → `{"status":"ok"}` без тяжёлых проверок.

### 7.2. UptimeRobot

1. https://uptimerobot.com/ → Register  
2. **Add New Monitor**  
   - Type: **HTTP(s)**  
   - URL: `https://<api-domain>/health`  
   - Interval: 5 minutes  
   - Alert contacts: Email / Telegram  
3. При `status != ok` или timeout — алерт

### 7.3. Связь с Grafana (опционально)

Alert rule в Grafana: `up{job="fastapi"} == 0` → webhook/email.

---

## Этап 8. Структурированное логирование

### 👤 Разработчик

- Запустить backend, сгенерировать несколько запросов и одну ошибку
- Сохранить 10–20 строк JSON-логов в файл `logs/sample.json` (для отчёта, можно в `.gitignore`)
- Прочитать вывод AI-анализа и **проверить**, совпадает ли с реальностью
- При необходимости скорректировать уровни логирования (меньше шума в prod)

### 🤖 С помощью AI (Cursor)

- Настроить `structlog` + JSON formatter
- Middleware `X-Request-ID` (генерация + проброс в логи и Sentry)
- Заменить часть `logging.info` в polling/services на structlog events
- Промпт-анализ: «вот логи за час — найди аномалии» → вставить в `integration_documentation.md`
- Пример nginx log format (если нужен)

**Пример промпта:**  
> «Переведи логирование H6/backend на structlog JSON. Добавь middleware request_id. Покажи пример лога для успешного запроса и ошибки polling.»

### 8.1. Backend — JSON-логи

```bash
pip install structlog
```

- Формат: `{"timestamp", "level", "event", "request_id", ...}`  
- Middleware: генерировать `X-Request-ID`, прокидывать в логи и Sentry  
- Уровни: INFO (запросы), WARNING (degraded health), ERROR (исключения)

### 8.3. nginx access log (frontend container)

Формат combined или JSON — для корреляции с backend `request_id` (если передаётся заголовок).

---

## Этап 9. Деплой: Railway (все сервисы)

Схема: весь стек на **Railway** — frontend, backend, mock-server, PostgreSQL, Redis в одном проекте. Репозиторий: [Rustem81/otus](https://github.com/Rustem81/otus).

### 👤 Разработчик

- Зарегистрироваться на Railway, привязать GitHub-аккаунт
- Создать проект, добавить 3 сервиса (backend, frontend, mock-server) из GitHub
- Для каждого указать **Root Directory** (`H6/backend`, `H6/frontend`, `H6/mock-server`)
- Добавить plugins: PostgreSQL, Redis
- Задать переменные окружения (DATABASE_URL, REDIS_URL, CORS, OAuth, Sentry, Метрика)
- Generate Domain для frontend и backend
- Обновить Google OAuth redirect URI и Яндекс.Метрику под prod-URL
- Проверить приложение end-to-end, записать ссылки в `H6/README.md`

### 🤖 С помощью AI (Cursor)

- `railway.toml` для каждого сервиса (опционально, можно через UI)
- `.github/workflows/h6-deploy.yml` с Railway CLI
- Исправить ошибки сборки по логам Railway
- Чеклист env в `H6/README.md`

---

### 9.1. Регистрация и настройка Railway (пошагово)

#### Шаг 1. Создать аккаунт

1. Открыть https://railway.app/
2. **Login** → **Continue with GitHub**
3. Разрешить Railway доступ к репозиториям

#### Шаг 2. Создать проект

1. Dashboard → **New Project** → **Deploy from GitHub repo**
2. Выбрать `Rustem81/otus`
3. Railway создаст первый сервис — можно сразу настроить как backend

#### Шаг 3. Настроить сервисы

Для каждого сервиса (backend, frontend, mock-server):

1. В проекте → **New** → **GitHub Repo** → `Rustem81/otus`
2. **Settings** → **Source**:
   - **Root Directory:** `H6/backend` (или `H6/frontend`, `H6/mock-server`)
   - **Watch Paths:** `H6/backend/**` (деплой только при изменениях в этой папке)
3. **Settings** → **Build**:
   - Builder: **Dockerfile** (автоопределение)
4. **Settings** → **Networking**:
   - **Generate Domain** → получить публичный URL

#### Шаг 4. Добавить PostgreSQL и Redis

1. В проекте → **New** → **Database** → **PostgreSQL**
2. В проекте → **New** → **Database** → **Redis**
3. Railway автоматически создаёт переменные `DATABASE_URL`, `REDIS_URL`

#### Шаг 5. Переменные окружения (backend)

В сервисе backend → **Variables**:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (Railway reference) |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` (Railway reference) |
| `SECRET_KEY` | сгенерировать случайную строку |
| `BACKEND_CORS_ORIGINS` | `https://<frontend-domain>.up.railway.app` |
| `GOOGLE_CLIENT_ID` | из Google Console |
| `GOOGLE_CLIENT_SECRET` | из Google Console |
| `GOOGLE_REDIRECT_URI` | `https://<backend-domain>.up.railway.app/api/v1/auth/google/callback` |
| `SENTRY_DSN_BACKEND` | из Sentry |
| `P2P_MOCK_BASE_URL` | `http://mock-server.railway.internal:8001/v1/api` |
| `P2P_DATA_SOURCE` | `mock` |
| `POLLING_INTERVAL_SEC` | `15` |

#### Шаг 6. Переменные окружения (frontend)

В сервисе frontend → **Variables** (build-time для Vite):

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://<backend-domain>.up.railway.app` |
| `VITE_YM_COUNTER_ID` | номер из Яндекс.Метрики |
| `VITE_SENTRY_DSN` | DSN frontend из Sentry |

#### Шаг 7. Internal networking (mock-server)

Mock-server не нужен публичный домен — backend обращается к нему по внутренней сети Railway:
- Mock-server → Settings → Networking → **не генерировать** публичный домен
- Backend переменная: `P2P_MOCK_BASE_URL=http://mock-server.railway.internal:8001/v1/api`

#### Шаг 8. Проверка после деплоя

- [ ] Frontend открывается без белого экрана
- [ ] `curl https://<backend>/health` → `{"status": "ok"}`
- [ ] Логин работает (test@test.com / test123456)
- [ ] Объявления загружаются
- [ ] В Network нет CORS-ошибок

### 9.2. Автодеплой

Railway автоматически деплоит при push в ветку (по умолчанию `main`). Watch Paths ограничивают деплой только при изменениях в соответствующей папке.

### 9.3. GitHub Actions deploy (опционально)

Если нужен деплой через CI (а не через Railway Git Integration):

```yaml
# .github/workflows/h6-deploy.yml
- name: Deploy to Railway
  uses: bervProject/railway-deploy@main
  with:
    railway_token: ${{ secrets.RAILWAY_TOKEN }}
    service: backend
```

Но для H6 достаточно Railway Git Integration (автодеплой из main).

### 9.4. После деплоя — обновить интеграции

| Сервис | Действие |
|--------|----------|
| **Google OAuth** | Redirect URI с Railway backend URL |
| **Яндекс.Метрика** | Адрес сайта = Railway frontend URL |
| **UptimeRobot** | Monitor → `https://<backend>/health` |
| **Sentry** | `SENTRY_ENVIRONMENT=production` |

### 9.5. Что указать в `H6/README.md`

```markdown
## Деплой

- Репозиторий: https://github.com/Rustem81/otus/tree/main/H6
- Frontend: https://<frontend>.up.railway.app
- Backend API: https://<backend>.up.railway.app
- Swagger: https://<backend>.up.railway.app/docs
- Хостинг: Railway (все сервисы в одном проекте)
```

---

## Этап 10. Тестирование и документация

### 👤 Разработчик

- Пройти **весь** ручной чеклист ниже (галочки в блокноте)
- Сделать скриншоты: CI green, Sentry issue, Grafana, Metrika, UptimeRobot UP
- Вычитать `integration_documentation.md` и `security_audit.md`
- Загрузить ссылку на GitHub и деплой на платформу OTUS
- Подготовить 3–5 примеров промптов с результатами (требование курса по AI)

### 🤖 С помощью AI (Cursor)

- Собрать черновики `integration_documentation.md`, `security_audit.md` из артефактов этапов 1–9
- Сгенерировать раздел «Использование AI» с таблицей: промпт → файл → результат
- Проверить README: команды запуска актуальны (`docker compose`, тестовые аккаунты)
- Найти устаревшие инструкции и предложить правки

**Пример промпта:**  
> «Собери integration_documentation.md для H6 из разделов: CI/CD, OAuth, Metrika, Sentry, Prometheus/Grafana, Uptime, логи. Добавь таблицу промптов для отчёта AI.»

### 10.1. Интеграционные тесты (ручной чеклист)

- [ ] CI: push → lint + test green  
- [ ] Deploy: main → prod обновился  
- [ ] Login email/password  
- [ ] Login Google (test user)  
- [ ] **Яндекс.Метрика:** визит в «Реальном времени» + цели `login`, `view_ad`  
- [ ] Sentry: тестовая ошибка видна  
- [ ] Prometheus: target UP, метрики растут  
- [ ] Grafana: дашборд показывает RPS/latency  
- [ ] UptimeRobot: monitor UP  
- [ ] `/health`: postgres + redis ok  

### 10.2. `integration_documentation.md`

Разделы:

1. CI/CD (схема, secrets, как перезапустить деплой)  
2. Google OAuth2 (ссылка на этот план + prod redirect)  
3. **Яндекс.Метрика** (счётчик, цели в UI, события в коде, скриншоты)  
4. Sentry (проекты, DSN, sampling, alerts)  
5. Prometheus + Grafana (порты, scrape config, дашборды)  
6. UptimeRobot  
7. Логирование + пример AI-анализа  

### 10.3. Шаблон таблицы «Использование AI» (для отчёта)

Заполняет разработчик на основе реальной работы с Cursor; черновик может подготовить AI.

| № | Этап | Промпт (кратко) | Что сделал AI | Что проверил/исправил разработчик |
|---|------|-----------------|---------------|-----------------------------------|
| 1 | CI/CD | «GitHub Actions monorepo…» | `ci.yml`, `deploy.yml` | Запустил Actions, добавил Secrets |
| 2 | Security | «OWASP аудит auth…» | `security_audit.md` | Прогнал pip-audit, внёс фиксы |
| 3 | OAuth | «Google OAuth2 FastAPI…» | routes, migration, UI | Тест в браузере, Google Console |
| 4 | Metrika | «Яндекс.Метрика Vite…» | `analytics.ts` | Счётчик, скрин «в реальном времени» |
| 5 | Sentry | «Sentry FastAPI React…» | init, ErrorBoundary | Тестовый issue в UI |
| 6 | Monitoring | «Prometheus instrumentator…» | compose, dashboard | Targets UP, скрин Grafana |
| 7 | Logs | «structlog + анализ логов» | config, AI-разбор | Сверил с реальными логами |
| 8 | Docs | «integration_documentation…» | черновик MD | Вычитка, скриншоты, сдача |

---


## Чеклист перед сдачей

### Обязательно по заданию H6

- [ ] CI/CD работает (сборка + тесты + деплой на push в main)  
- [ ] Минимум 2 интеграции: **OAuth2** + **Аналитика**  
- [ ] Аудит безопасности + `security_audit.md`  
- [ ] Мониторинг: UptimeRobot + Health Check  
- [ ] Логирование (JSON) + пример AI-анализа  
- [ ] `integration_documentation.md`  
- [ ] Приложение задеплоено, ссылки в README  
- [ ] AI-процесс задокументирован  

### Расширения этого плана

- [ ] **Sentry** подключён (backend + frontend), тестовый issue виден  
- [ ] **Prometheus** скрейпит `/metrics`  
- [ ] **Grafana** дашборд с latency, errors, polling metrics  
- [ ] `/metrics` не доступен публично без защиты  

---

## Порядок выполнения (кратко)

```
0. Подготовка H6
   ↓
1. CI (без деплоя) → 2. Security audit
   ↓
5. Sentry (локально) + 8. JSON logs
   ↓
6. Prometheus + Grafana (docker compose local)
   ↓
3. OAuth Google (local redirect URIs)
   ↓
4. Код Метрики (локально) → 9. Deploy Vercel → обновить URL в Метрике → проверка целей (4.5)
   ↓
9. Deploy prod → OAuth URIs, VITE_* на Vercel, backend Railway
   ↓
7. UptimeRobot на prod /health
   ↓
1. CI deploy job → 10. Документация + чеклист
```

---

## Полезные ссылки

| Ресурс | URL |
|--------|-----|
| Google Cloud Console | https://console.cloud.google.com/ |
| Google OAuth 2.0 docs | https://developers.google.com/identity/protocols/oauth2 |
| Sentry FastAPI | https://docs.sentry.io/platforms/python/integrations/fastapi/ |
| Sentry React | https://docs.sentry.io/platforms/javascript/guides/react/ |
| Prometheus | https://prometheus.io/docs/introduction/overview/ |
| Grafana docs | https://grafana.com/docs/ |
| prometheus-fastapi-instrumentator | https://github.com/trallnag/prometheus-fastapi-instrumentator |
| Яндекс.Метрика | https://yandex.ru/support/metrica/ |
| Vercel (monorepo) | https://vercel.com/docs/monorepos |
| Vercel env vars | https://vercel.com/docs/projects/environment-variables |
| Репозиторий OTUS | https://github.com/Rustem81/otus |
| Папка H6 | https://github.com/Rustem81/otus/tree/main/H6 |
| UptimeRobot | https://uptimerobot.com/ |
| GitHub Actions | https://docs.github.com/en/actions |

---

*Документ создан как рабочий план H6. При изменении доменов или провайдеров деплоя — обновлять redirect URI и секции 3.1, 9.2.*
