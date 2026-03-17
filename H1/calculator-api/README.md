# Calculator API

REST API для выполнения арифметических операций (сложение, вычитание, умножение, деление), построенный на [FastAPI](https://fastapi.tiangolo.com/).

Проект следует паттернам из скила **fastapi-templates**: versioned API router, dependency injection, lifespan context manager, service layer.

## Содержание

- [Структура проекта](#структура-проекта)
- [Запуск локально](#запуск-локально)
- [Запуск через Docker](#запуск-через-docker)
- [API-эндпоинты](#api-эндпоинты)
- [Конфигурация](#конфигурация)
- [Тестирование](#тестирование)

## Структура проекта

```
app/
├── api/                        # API routes (versioned)
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── calculator.py   # POST /api/v1/calculate
│   │   │   └── health.py       # GET /api/v1/health
│   │   └── router.py           # Versioned API router
│   └── dependencies.py         # Shared dependencies
├── core/                       # Core configuration
│   ├── config.py               # Settings via pydantic-settings
│   └── logging.py              # Logging configuration
├── schemas/                    # Pydantic schemas
│   └── calculator.py           # Request/Response models
├── services/                   # Business logic
│   └── calculator.py           # CalculatorService class
├── middleware.py                # Logging middleware
└── main.py                     # Application entry (lifespan pattern)
```

## Запуск локально

### Предварительные требования

- Python 3.11+
- pip

### Установка зависимостей

```bash
# Активация виртуального окружения (пример для Windows)
C:\Project\OTUS\venv\Scripts\activate

# Установка зависимостей
pip install .

# Для разработки (включая pytest, httpx, hypothesis)
pip install ".[dev]"
```

### Запуск сервера

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

С автоперезагрузкой при изменении кода:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

После запуска API доступен по адресу: http://localhost:8000

Swagger-документация: http://localhost:8000/docs

## Запуск через Docker

### Production

```bash
docker compose up --build
```

### Development (с монтированием исходного кода и автоперезагрузкой)

```bash
docker compose -f docker-compose.dev.yml up --build
```

В dev-режиме директория `./app` монтируется в контейнер, поэтому изменения в коде применяются автоматически без пересборки образа.

## API-эндпоинты

### POST /api/v1/calculate

Выполняет арифметическую операцию над двумя числами.

**Запрос:**

```json
{
  "a": 10,
  "b": 3,
  "operation": "add"
}
```

Допустимые значения `operation`: `add`, `subtract`, `multiply`, `divide`.

**Успешный ответ (200):**

```json
{
  "a": 10.0,
  "b": 3.0,
  "operation": "add",
  "result": 13.0
}
```

**Ошибка — деление на ноль (400):**

```json
{
  "detail": "Division by zero is not allowed"
}
```

**Ошибка валидации (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "a"],
      "msg": "Input should be a valid number",
      "type": "float_parsing"
    }
  ]
}
```

### GET /api/v1/health

Проверка работоспособности сервиса.

**Ответ (200):**

```json
{
  "status": "ok"
}
```

## Конфигурация

Приложение настраивается через переменные окружения. Можно также использовать файл `.env` в корне проекта (см. `.env.example`).

| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `APP_HOST` | str | `0.0.0.0` | Хост для привязки сервера |
| `APP_PORT` | int | `8000` | Порт для привязки сервера |
| `LOG_LEVEL` | str | `INFO` | Уровень логирования (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DEBUG` | bool | `false` | Режим отладки |
| `API_V1_PREFIX` | str | `/api/v1` | Префикс версионированного API |

## Тестирование

### Установка dev-зависимостей

```bash
pip install ".[dev]"
```

### Запуск тестов

```bash
pytest -v
```
