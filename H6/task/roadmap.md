# H6 — Roadmap (прогресс)

**Проект:** MEXC P2P Insight  
**Репозиторий:** [github.com/Rustem81/otus](https://github.com/Rustem81/otus)  
**Папка ДЗ:** [github.com/Rustem81/otus/tree/main/H6](https://github.com/Rustem81/otus/tree/main/H6)  
**Детальный план:** [work_plan.md](./work_plan.md)  
**Хостинг:** Railway (все сервисы в одном проекте)

**Легенда:** `[ ]` не начато · `[/]` в работе · `[x]` готово · `[-]` пропущено (опционально)

---

## Сводка

| Показатель | Значение |
|------------|----------|
| Обязательных этапов (task.md 1–4, 6–7) | 6 |
| Выполнено обязательных | 0 / 6 |
| Доп. этапов (Sentry, Prometheus) | 2 |
| Выполнено доп. | 0 / 2 |
| Готовность к сдаче | ⬜ Нет |

**Деплой frontend:** _URL пока нет_  
**Деплой backend API:** _URL пока нет_  
**Последнее обновление roadmap:** _—_

---

## Схема деплоя (Railway)

```
GitHub: Rustem81/otus (main)
    │
    └─► Railway Project "MEXC P2P Insight"
         ├── Service: frontend (Docker, H6/frontend) → https://frontend-xxx.up.railway.app
         ├── Service: backend (Docker, H6/backend)   → https://backend-xxx.up.railway.app
         ├── Service: mock-server (Docker, H6/mock-server)
         ├── PostgreSQL (managed plugin)
         └── Redis (managed plugin)
```

---

## Фаза 0 — Подготовка (блокер для всего остального)

| # | Задача | Статус | Дата | Заметки |
|---|--------|--------|------|---------|
| 0.1 | Скопировать `H5` → `H6` (backend, frontend, mock-server, docker-compose) | [ ] | | |
| 0.2 | Локально: `docker compose up` в `H6/` работает | [ ] | | |
| 0.3 | Создать `H6/.env` из `.env.example` (не в git) | [ ] | | |
| 0.4 | Черновик `H6/README.md` | [ ] | | |
| 0.5 | Push в GitHub — в H6 видны `backend/`, `frontend/` | [ ] | | |

**Фаза 0 завершена:** [ ]

---

## Фаза 1 — CI/CD (обязательно, task.md шаг 1)

| # | Задача | 👤 / 🤖 | Статус | Дата | Заметки |
|---|--------|---------|--------|------|---------|
| 1.1 | `.github/workflows/h6-ci.yml` (lint, test, audit) | 🤖 | [ ] | | path filter `H6/**` |
| 1.2 | `.github/workflows/h6-deploy.yml` (Railway deploy on push main) | 🤖 | [ ] | | |
| 1.3 | GitHub Secrets (`RAILWAY_TOKEN`, OAuth, Sentry) | 👤 | [ ] | | |
| 1.4 | CI зелёный на тестовом push | 👤 | [ ] | | |
| 1.5 | Deploy после push в `main` успешен | 👤 | [ ] | | |

**Фаза 1 завершена:** [ ]

---

## Фаза 2 — Аудит безопасности (обязательно, task.md шаг 2)

| # | Задача | 👤 / 🤖 | Статус | Дата | Заметки |
|---|--------|---------|--------|------|---------|
| 2.1 | `pip-audit` / `npm audit` — вывод сохранён | 👤 | [ ] | | |
| 2.2 | AI-аудит OWASP (auth, CSRF, CORS) | 🤖 | [ ] | | |
| 2.3 | Исправления в коде / зависимостях | 🤖+👤 | [ ] | | |
| 2.4 | Файл `H6/security_audit.md` | 🤖+👤 | [ ] | | |

**Фаза 2 завершена:** [ ]

---

## Фаза 3 — OAuth2 Google (обязательно, task.md шаг 3)

| # | Задача | 👤 / 🤖 | Статус | Дата | Заметки |
|---|--------|---------|--------|------|---------|
| 3.1 | Google Cloud: проект, consent screen, Client ID | 👤 | [ ] | | |
| 3.2 | Test users добавлены | 👤 | [ ] | | |
| 3.3 | Backend: routes + миграция `oauth_*` | 🤖 | [ ] | | |
| 3.4 | Frontend: кнопка Google, callback | 🤖 | [ ] | | |
| 3.5 | Тест: успех / отмена / ошибка | 👤 | [ ] | | |
| 3.6 | Prod redirect URI (Railway URL) | 👤 | [ ] | | |

**Фаза 3 завершена:** [ ]

---

## Фаза 4 — Яндекс.Метрика (обязательно, task.md шаг 4)

| # | Задача | 👤 / 🤖 | Статус | Дата | Заметки |
|---|--------|---------|--------|------|---------|
| 4.1 | Счётчик на metrika.yandex.ru | 👤 | [ ] | | ID: |
| 4.2 | Цели в UI (`login`, `view_ad`, …) | 👤 | [ ] | | |
| 4.3 | Код: `analytics.ts`, `trackEvent`, SPA hit | 🤖 | [ ] | | |
| 4.4 | `VITE_YM_COUNTER_ID` в Railway env + redeploy | 👤 | [ ] | | |
| 4.5 | Проверка «В реальном времени» + скриншот | 👤 | [ ] | | |

**Фаза 4 завершена:** [ ]

---

## Фаза 5 — Деплой Railway (обязательно для сдачи)

| # | Задача | 👤 / 🤖 | Статус | Дата | Заметки |
|---|--------|---------|--------|------|---------|
| 5.1 | Railway: создать проект, привязать GitHub `Rustem81/otus` | 👤 | [ ] | | |
| 5.2 | Service: backend (Root = `H6/backend`, Dockerfile) | 👤 | [ ] | | |
| 5.3 | Service: frontend (Root = `H6/frontend`, Dockerfile) | 👤 | [ ] | | |
| 5.4 | Service: mock-server (Root = `H6/mock-server`, Dockerfile) | 👤 | [ ] | | |
| 5.5 | Plugin: PostgreSQL + Redis | 👤 | [ ] | | |
| 5.6 | Variables: DATABASE_URL, REDIS_URL, CORS, OAuth, Sentry | 👤 | [ ] | | |
| 5.7 | Generate domains для frontend и backend | 👤 | [ ] | | |
| 5.8 | `VITE_API_URL` → backend Railway URL | 👤 | [ ] | | |
| 5.9 | E2E на prod: login, ads, OAuth | 👤 | [ ] | | |
| 5.10 | URL записаны в `H6/README.md` | 👤 | [ ] | | |

**Фаза 5 завершена:** [ ]

---

## Фаза 6 — Мониторинг (обязательно, task.md шаг 6)

| # | Задача | 👤 / 🤖 | Статус | Дата | Заметки |
|---|--------|---------|--------|------|---------|
| 6.1 | `/health` проверяет Postgres + Redis | 🤖 | [ ] | | из H5 |
| 6.2 | UptimeRobot на prod `/health` | 👤 | [ ] | | |
| 6.3 | Алерт email/Telegram проверен | 👤 | [ ] | | |

**Фаза 6 завершена:** [ ]

---

## Фаза 7 — Логирование (обязательно, task.md шаг 7)

| # | Задача | 👤 / 🤖 | Статус | Дата | Заметки |
|---|--------|---------|--------|------|---------|
| 7.1 | structlog JSON на backend | 🤖 | [ ] | | |
| 7.2 | `X-Request-ID` middleware | 🤖 | [ ] | | |
| 7.3 | AI-анализ sample логов → в документацию | 🤖+👤 | [ ] | | |

**Фаза 7 завершена:** [ ]

---

## Фаза 8 — Дополнительно (не в обязательных критериях)

| # | Задача | Статус | Дата | Заметки |
|---|--------|--------|------|---------|
| 8.1 | Sentry backend + frontend | [ ] | | |
| 8.2 | Prometheus + Grafana (только локально, docker-compose) | [ ] | | |
| 8.3 | Платежи (ЮKassa) | [-] | | опционально |

---

## Фаза 9 — Документация и сдача (task.md шаги 8–9)

| # | Задача | Статус | Дата | Заметки |
|---|--------|--------|------|---------|
| 9.1 | `H6/integration_documentation.md` | [ ] | | |
| 9.2 | `H6/security_audit.md` (финальная вычитка) | [ ] | | |
| 9.3 | `H6/README.md` — ссылки repo + deploy | [ ] | | |
| 9.4 | `H6/report.md` — скриншоты, таблица AI-промптов | [ ] | | |
| 9.5 | Сдача на платформе OTUS | [ ] | | |

**Фаза 9 завершена:** [ ]

---

## Чеклист «Принято»

- [ ] CI/CD работает (build + test + lint + deploy)
- [ ] ≥2 интеграции: **OAuth2** + **аналитика (Яндекс.Метрика)**
- [ ] Аудит безопасности + исправления + `security_audit.md`
- [ ] Мониторинг (UptimeRobot) + логи JSON + `/health`
- [ ] AI задокументирован (CI, аудит, логи)
- [ ] Приложение на Railway, ссылки в README
- [ ] Все артефакты в H6 на GitHub

**Готов к сдаче:** [ ]

---

## Журнал сессий

| Дата | Что сделано | Следующий шаг |
|------|-------------|---------------|
| | | |

---

*Обновляйте `[ ]` → `[x]` по мере выполнения.*
