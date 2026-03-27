---
inclusion: manual
---

# Правила Docker и инфраструктуры сборки

Этот файл активируется вручную через `#04-docker-rules` когда пользователь просит настроить Docker, Docker Compose или инфраструктуру сборки.

## Структура

```
project-root/
├── frontend/
│   ├── Dockerfile
│   └── .dockerignore
├── backend/
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml          # Development
├── docker-compose.prod.yml     # Production overrides
├── .env.example
└── nginx/
    └── nginx.conf              # Reverse proxy для prod
```

## Docker Compose (development)

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    ports:
      - "9000:9000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    env_file:
      - .env
    depends_on:
      - backend
    command: npx quasar dev

  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: mexc_p2p
      POSTGRES_USER: ${POSTGRES_USER:-mexc}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-mexc_secret}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-mexc}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

## Dockerfile бэкенда (multi-stage)

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

FROM base AS development
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"
COPY . .

FROM base AS production
COPY pyproject.toml ./
RUN pip install --no-cache-dir .
COPY . .
RUN adduser --disabled-password --no-create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dockerfile фронтенда (multi-stage)

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base
WORKDIR /app

FROM base AS development
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 9000

FROM base AS build
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx quasar build

FROM nginx:alpine AS production
COPY --from=build /app/dist/spa /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

## .env.example

```env
# Database
DATABASE_URL=postgresql+asyncpg://mexc:mexc_secret@postgres:5432/mexc_p2p
POSTGRES_USER=mexc
POSTGRES_PASSWORD=mexc_secret

# Redis
REDIS_URL=redis://redis:6379

# Auth
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# MEXC Polling
POLLING_INTERVAL_SEC=10
INACTIVE_TTL_SEC=15

# LLM
OPENAI_API_KEY=sk-...
LLM_CACHE_TTL_SEC=600
LLM_MAX_CHARS=300

# Scoring
SCORING_WEIGHT_RATING=0.3
SCORING_WEIGHT_TRADES=0.25
SCORING_WEIGHT_SUCCESS_RATE=0.3
SCORING_WEIGHT_SPEED=0.15

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

## Правила

- Multi-stage builds обязательны: development (с hot-reload) и production (минимальный образ)
- Healthcheck для postgres и redis обязательны в compose
- Volumes для данных БД и Redis — именованные, не bind mounts
- `.dockerignore` в каждом проекте: исключить `node_modules`, `__pycache__`, `.git`, `.env`
- Секреты — через `.env` файл (не в Dockerfile и не в compose)
- Production: non-root user в контейнере бэкенда
