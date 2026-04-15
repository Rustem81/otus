# MEXC P2P Агрегатор

Веб-приложение для мониторинга и анализа P2P-объявлений криптобиржи MEXC. Работает в режиме read-only — не совершает торговых операций и не требует API-ключей MEXC.

## Стек технологий

| Слой | Технология |
|------|-----------|
| Фронтенд | Vue.js 3 + Quasar 2 + TypeScript |
| Бэкенд | Python 3.12 + FastAPI + Pydantic v2 |
| БД | PostgreSQL 16 + SQLAlchemy 2 (async) + Alembic |
| Кэш | Redis 7 |
| LLM | OpenAI API (GPT-4o-mini) |
| Mock-сервер | FastAPI (эмуляция P2P API) |
| Контейнеризация | Docker + Docker Compose |

## Быстрый старт

### 1. Клонировать и настроить окружение

```bash
cp .env.example .env
# Отредактировать .env при необходимости (по умолчанию всё работает с mock-server)
```

### 2. Запуск в режиме разработки

```bash
docker compose -f docker-compose.dev.yml up --build -d
```

После запуска:
- Фронтенд: http://localhost:9000
- Бэкенд API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Mock-сервер: http://localhost:8001
- PostgreSQL: localhost:5432
- Redis: localhost:6379

Тестовые аккаунты:
- Пользователь: `test@test.com` / `test123456`
- Администратор: `admin@test.com` / `admin1234`

## Два docker-compose файла

В проекте два файла конфигурации Docker Compose для разных сценариев.

### docker-compose.dev.yml — полный стек для разработки

Это основной файл для работы. Включает все сервисы с правильным порядком запуска:

```
postgres → redis → migrations → mock-server → backend → frontend (nginx)
```

Особенности:
- Автоматический запуск миграций (сервис `migrations` выполняет `alembic upgrade head` перед стартом бэкенда)
- Mock-сервер с healthcheck — бэкенд стартует только после готовности mock-server
- Бэкенд с healthcheck — фронтенд стартует только после готовности бэкенда
- Фронтенд раздаётся через nginx из предсобранного `dist/spa` (нужен предварительный `npm run build`)
- Volume mount для hot-reload бэкенда и mock-сервера (`--reload`)
- Переменные окружения для связи между контейнерами прописаны явно

Когда использовать: основная работа, демонстрация, тестирование полного стека.

### docker-compose.yml — упрощённый стек

Минимальная конфигурация без оркестрации зависимостей:

```
postgres + redis + mock-server + backend + frontend (quasar dev)
```

Особенности:
- Нет сервиса миграций — нужно запускать вручную
- Нет healthcheck — сервисы стартуют параллельно (бэкенд может упасть если БД ещё не готова)
- Фронтенд запускается через `npx quasar dev` (hot-reload с HMR, но медленнее старт)
- Volume mount для всех сервисов

Когда использовать: быстрый запуск для разработки фронтенда с HMR, когда инфраструктура уже поднята.

### Сравнение

| Аспект | docker-compose.yml | docker-compose.dev.yml |
|--------|-------------------|----------------------|
| Миграции | Вручную | Автоматически |
| Healthcheck | Только postgres/redis | Все сервисы |
| Порядок запуска | Частичный | Полный (зависимости) |
| Фронтенд | Quasar dev (HMR) | Nginx + предсобранный SPA |
| Hot-reload бэкенд | Да (`--reload`) | Да (`--reload`) |
| Надёжность старта | Может потребовать перезапуск | Стабильный |

## Ручной запуск миграций

Если используете `docker-compose.yml` (без автомиграций):

```bash
docker compose exec backend alembic upgrade head
```

## Структура проекта

```
H2/
├── backend/                 # FastAPI бэкенд
│   ├── app/
│   │   ├── api/v1/endpoints/  # REST эндпоинты
│   │   ├── core/              # Конфигурация, БД, Redis, безопасность
│   │   ├── middleware/        # CSRF, rate limiting
│   │   ├── models/            # SQLAlchemy модели
│   │   ├── repositories/     # Слой доступа к данным
│   │   ├── schemas/           # Pydantic схемы
│   │   ├── services/          # Бизнес-логика
│   │   └── tasks/             # Фоновые задачи (polling)
│   ├── alembic/               # Миграции БД
│   └── Dockerfile
├── frontend/                # Vue.js + Quasar фронтенд
│   ├── src/
│   │   ├── api/               # API-клиент
│   │   ├── components/        # Vue-компоненты
│   │   ├── layouts/           # Layouts (Main, Auth)
│   │   ├── pages/             # Страницы
│   │   ├── router/            # Маршрутизация + guard
│   │   └── stores/            # Pinia stores
│   └── Dockerfile
├── mock-server/             # Эмуляция P2P API
│   ├── app/
│   │   ├── generator.py       # Генерация объявлений
│   │   └── merchants.py       # Пул мерчантов
│   └── Dockerfile
├── docker-compose.yml       # Упрощённый стек
├── docker-compose.dev.yml   # Полный стек с оркестрацией
├── .env.example             # Шаблон переменных окружения
└── readme.md
```

## API эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/login` | Вход |
| POST | `/api/v1/auth/logout` | Выход |
| GET | `/api/v1/auth/me` | Текущий пользователь |
| GET | `/api/v1/profile/` | Профиль трейдера |
| PUT | `/api/v1/profile/` | Обновить профиль |
| POST | `/api/v1/profile/onboarding` | Завершить онбординг |
| GET | `/api/v1/profile/banks` | Список банков |
| GET | `/api/v1/profile/filters` | Сохранённые фильтры |
| PUT | `/api/v1/profile/filters` | Обновить фильтры |
| GET | `/api/v1/advertisements` | Список объявлений (с фильтрацией) |
| GET | `/api/v1/advertisements/{id}` | Детали объявления |
| GET | `/api/v1/scoring/{ad_id}/explain` | LLM-объяснение риск-скора |
| GET | `/api/v1/blacklist` | Чёрный список мерчантов |
| POST | `/api/v1/blacklist` | Добавить в чёрный список |
| DELETE | `/api/v1/blacklist/{merchant_id}` | Убрать из чёрного списка |
| GET | `/api/v1/history` | История просмотров |
| POST | `/api/v1/history` | Записать просмотр |
| GET | `/api/v1/admin/*` | Админ-панель (ADMIN only) |
| GET | `/health` | Healthcheck |

## Конфигурация

Все параметры задаются через переменные окружения (файл `.env`). См. `.env.example` для полного списка.

Ключевые параметры:

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| `P2P_DATA_SOURCE` | Источник данных: `mock` или `p2p_army` | `mock` |
| `POLLING_INTERVAL_SEC` | Интервал опроса P2P API (сек) | `10` |
| `INACTIVE_TTL_SEC` | TTL неактивных объявлений (сек) | `15` |
| `OPENAI_API_KEY` | Ключ OpenAI для LLM-объяснений | — |
| `LLM_CACHE_TTL_SEC` | Кэш LLM-ответов в Redis (сек) | `600` |

## Сборка фронтенда

Для `docker-compose.dev.yml` нужен предсобранный SPA:

```bash
cd frontend
npm install
npx quasar build
cd ..
```

После этого `docker compose -f docker-compose.dev.yml up` раздаст собранный SPA через nginx.

## Лицензия

Учебный проект OTUS.
