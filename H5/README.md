# H5: Развертывание Backend и интеграция с Frontend

## MEXC P2P Агрегатор — Fullstack Application

Веб-приложение для мониторинга и анализа P2P-объявлений криптобиржи MEXC. Работает в режиме read-only.

### Стек

| Слой | Технология |
|------|-----------|
| Frontend | React 19 + TypeScript + Tailwind CSS 4 + shadcn/ui |
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2 (async) |
| БД | PostgreSQL 16 |
| Кэш | Redis 7 |
| Контейнеризация | Docker + Docker Compose |

### Быстрый старт

```bash
# 1. Создать .env
cp .env.example .env

# 2. Запустить весь стек
docker compose up -d

# 3. Проверить
curl http://localhost:8000/health
# → {"status": "ok", "dependencies": {"postgres": "ok", "redis": "ok"}}

# 4. Открыть приложение
# Frontend: http://localhost:3000
# Backend Swagger: http://localhost:8000/docs
```

### Тестовые учётные записи

| Email | Пароль | Роль |
|-------|--------|------|
| test@test.com | test123456 | USER |
| admin@test.com | admin1234 | ADMIN |

### Структура проекта

```
H5/
├── backend/           # FastAPI backend (из H2)
│   ├── app/           # Исходный код
│   ├── alembic/       # Миграции БД
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/          # React frontend (из H4)
│   ├── src/           # Исходный код
│   ├── Dockerfile
│   └── nginx.conf
├── mock-server/       # Эмулятор P2P API
├── docker-compose.yml # Весь стек одной командой
├── .env.example       # Шаблон переменных окружения
├── backend_documentation.md  # Полная документация
└── README.md          # Этот файл
```

### Документация

- [backend_documentation.md](backend_documentation.md) — архитектура, API, развёртывание, безопасность

### API Endpoints (основные)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/v1/auth/login | Вход |
| POST | /api/v1/auth/register | Регистрация |
| GET | /api/v1/advertisements | Список объявлений |
| GET | /api/v1/profile/ | Профиль трейдера |
| PUT | /api/v1/profile/ | Обновить профиль |
| GET | /api/v1/scoring/{id}/explain | LLM-объяснение риска |
| POST | /api/v1/blacklist | Заблокировать мерчанта |
| GET | /api/v1/history | История просмотров |
| GET | /api/v1/admin/errors | Ошибки (ADMIN) |
| GET | /health | Health check |

### Тесты

```bash
# Frontend (23 теста)
cd frontend && npm run test

# Backend
docker compose exec backend pytest -v
```
