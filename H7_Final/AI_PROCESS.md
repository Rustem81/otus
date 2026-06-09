# Документация AI-процесса разработки

## MEXC P2P Insight — использование AI на всех этапах

> Инструмент: **Kiro (AI IDE)** | Модель: Auto

---

## 1. Планирование и архитектура

### 1.1 Генерация идеи и анализ

**Промпт:**
> Есть задание — сделать P2P-агрегатор для MEXC. Что нужно реализовать для MVP? Какие таблицы в БД? Какие API endpoints?

**Результат AI:**
- Определил 7 сущностей БД: User, Merchant, Advertisement, TraderProfile, MerchantBlacklist, ViewHistory, SavedFilters
- Предложил risk-scoring алгоритм (рейтинг + сделки + успех + скорость)
- Составил список endpoints с CRUD

**Что проверил разработчик:**
- Добавил поля для OAuth (oauth_provider, oauth_subject)
- Уточнил формулу риск-скоринга под реальные данные MEXC

### 1.2 User Stories (сформированы с AI)

```
Как трейдер, я хочу видеть все P2P-объявления в одном месте,
чтобы не переключаться между вкладками.

Как трейдер, я хочу оценку риска каждого мерчанта,
чтобы не терять деньги на ненадёжных контрагентах.

Как трейдер, я хочу блокировать нежелательных мерчантов,
чтобы не видеть их объявления.
```

---

## 2. Проектирование БД

**Промпт:**
> Спроектируй схему БД для P2P-агрегатора: пользователи, мерчанты, объявления, профиль трейдера, черный список, история просмотров.

**Результат AI:**
- Полная схема SQLAlchemy models (`models/user.py`, `merchant.py`, `advertisement.py`, etc.)
- Alembic миграции с корректными индексами
- Partial unique index для OAuth (WHERE oauth_provider IS NOT NULL)

**Что проверил разработчик:**
- Проверил foreign keys и cascade delete
- Добавил комментарии к полям

---

## 3. Backend разработка

### 3.1 FastAPI структура

**Промпт:**
> Создай FastAPI backend с: auth (register, login, logout), OAuth2 Google, CRUD для профиля, endpoint для объявлений с фильтрами, risk scoring.

**Результат AI:**
- Все файлы в `app/api/v1/endpoints/` (~8 файлов)
- Services, repositories, schemas
- Middleware stack (CSRF, rate limiting, security headers)

### 3.2 OAuth2 Google

**Промпт:**
> Добавь Google OAuth2 в H6/backend: authlib, state в Redis, callback создаёт/находит User. Frontend: кнопка на login.tsx. Redirect URI: http://localhost:8000/api/v1/auth/google/callback.

**Результат AI:**
- `services/oauth_google.py` — полный flow
- `endpoints/auth_oauth.py` — GET /auth/google, GET /auth/google/callback
- Миграция Alembic для oauth_provider/oauth_subject
- Frontend кнопка + callback страница

### 3.3 Безопасность (OWASP аудит)

**Промпт:**
> Проведи аудит безопасности FastAPI-проекта по OWASP Top 10. Укажи файл:строка, severity, рекомендацию. Отдельно проверь JWT-сессии в Redis и CSRF middleware.

**Результат AI:**
- 21 находка (SEC-01 — SEC-21)
- Патчи: SECRET_KEY validation, CORS restrictions, security headers, CSRF Secure flag
- `security_audit.md` с таблицей всех находок

---

## 4. Frontend разработка

### 4.1 Компоненты

**Промпт:**
> Создай React компоненты для P2P приложения: AdCard с рейтингом мерчанта и риск-индикатором, AdDetailDialog с полными деталями, RiskIndicator (цветовой), StarRating.

**Результат AI:**
- `AdCard.tsx` — карточка объявления
- `AdDetailDialog.tsx` — детальный диалог
- `RiskIndicator.tsx` — SVG прогресс-кольцо
- `StarRating.tsx` — рейтинг звёздами
- `PaymentIcons.tsx` — иконки банков

### 4.2 Яндекс.Метрика

**Промпт:**
> Интегрируй Яндекс.Метрику в H6/frontend (Vite React): VITE_YM_COUNTER_ID, загрузка tag.js только в production, reachGoal через trackEvent. Добавь pageview на смену роута.

**Результат AI:**
- `lib/analytics.ts` — initMetrika, trackPageView, trackEvent
- Graceful degradation (no-op если нет COUNTER_ID)
- Интеграция в login, main, blacklist, auth-callback
- Типы window.ym в vite-env.d.ts

---

## 5. DevOps и инфраструктура

### 5.1 CI/CD

**Промпт:**
> Сгенерируй GitHub Actions для H6: backend FastAPI (ruff, pytest, pip-audit), frontend React Vite (eslint, vitest, npm audit). Отдельный deploy.yml: smoke-test /health после Railway деплоя.

**Результат AI:**
- `h6-ci.yml` — 4 jobs: backend-lint-test, backend-security, frontend-lint-test, frontend-audit
- `h6-deploy.yml` — sleep 180 + curl /health + проверка status=="ok"
- Path filters для monorepo (H6/**)
- `continue-on-error: true` для audit jobs

### 5.2 Prometheus + Grafana

**Промпт:**
> Добавь Prometheus metrics в H6/backend: instrumentator на /metrics, custom counters для polling и LLM. Создай docker-compose сервисы prometheus+grafana и dashboard JSON. Дашборд должен подниматься автоматически, никакого ручного труда.

**Результат AI:**
- `core/metrics.py` — p2p_polling_duration_seconds, p2p_ads_active_total, auth_logins_total
- `monitoring/prometheus/prometheus.yml`
- `monitoring/grafana/provisioning/` — datasource + dashboard auto-provisioning
- `monitoring/grafana/dashboards/mexc-p2p.json` — 6 панелей

---

## 6. Отладка с AI

### Пример: ruff ошибки

**Промпт:**
> Исправь остаток ruff ошибок в H6/backend

**Результат:** `ruff check . --fix` + ручные правки F821

### Пример: eslint ошибки

**Промпт:**
> Исправь eslint в H6/frontend для CI

**Результат:** Исправлены `badge.tsx`, `button.tsx`, `tabs.tsx`, `auth-callback.tsx`

---

## 7. Анализ логов с AI

### Пример промпта для анализа

```
Вот 20 строк backend логов за последний час. 
Найди аномалии, потенциальные ошибки и предложи улучшения:

[вставить логи]
```

**Как AI помогает:**
- Определяет паттерны ошибок по типам исключений
- Находит медленные запросы по duration_ms
- Рекомендует уровни логирования

---

## 8. Выводы и рекомендации

### Что AI делал хорошо:
- Генерация boilerplate кода (endpoints, schemas, repositories)
- Следование best practices (структура проекта, OWASP)
- Создание документации и тестов
- Конфигурационные файлы (CI/CD, Docker, Grafana)

### Где нужен контроль разработчика:
- Бизнес-логика (формула risk scoring, правила KYC)
- Безопасность (проверка каждого патча)
- Интеграция с реальными сторонними сервисами (Google Console, Яндекс)
- Финальное тестирование edge cases

### Рекомендации для следующих проектов:
1. Начинать с четкого ТЗ для AI — чем конкретнее промпт, тем лучше результат
2. Всегда проверять сгенерированные миграции перед применением
3. AI хорошо генерирует код структурно, но может пропустить контекстные зависимости
4. Использовать AI для первого черновика документации, доделывать руками

---

## Метрики проекта (с AI)

| Метрика | Значение |
|---------|----------|
| Файлов кода сгенерировано AI | ~80% |
| Файлов создано/исправлено вручную | ~20% |
| Найдено и исправлено уязвимостей | 21 |
| Тестов написано AI | 39 (pytest) |
| Время на backend API (с AI) | ~3 часа vs ~3 дня без AI |
| Время на frontend (с AI) | ~2 часа vs ~2 дня без AI |
