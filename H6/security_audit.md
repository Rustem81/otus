# Аудит безопасности H6

## Методология

### Подход
Ручной аудит исходного кода (SAST) по методологии OWASP Top 10 (2021).

### Область аудита
| Компонент | Путь | Описание |
|-----------|------|----------|
| API endpoints | `app/api/v1/endpoints/` | REST API (auth, profile, ads, scoring, blacklist, history, admin) |
| Middleware | `app/middleware/` | CSRF, Rate Limiter |
| Services | `app/services/` | Auth, P2P polling, scoring, LLM |
| Core | `app/core/` | Config, security, database, Redis |
| Repositories | `app/repositories/` | Data access layer (SQLAlchemy ORM) |

### Категории OWASP Top 10 (2021)
1. A01 — Broken Access Control
2. A02 — Cryptographic Failures
3. A03 — Injection
4. A04 — Insecure Design
5. A05 — Security Misconfiguration
6. A06 — Vulnerable and Outdated Components
7. A07 — Identification and Authentication Failures
8. A08 — Software and Data Integrity Failures
9. A09 — Security Logging and Monitoring Failures
10. A10 — Server-Side Request Forgery (SSRF)

### Severity Policy
- **Critical / High** — обязательное исправление или явное исключение с обоснованием
- **Medium** — документировать, планировать исправление
- **Low / Info** — документировать, решение по усмотрению

---

## Находки

| ID | Severity | OWASP | Компонент | Описание | Статус | Коммит |
|----|----------|-------|-----------|----------|--------|--------|
| SEC-01 | Medium | A05 | `core/config.py` | SECRET_KEY имеет дефолтное значение `"change-me-in-production"`. При забытой переменной окружения приложение запустится с предсказуемым ключом | ✅ Fixed | — |
| SEC-02 | Medium | A05 | `middleware/csrf.py` | CSRF cookie устанавливается с `secure=False`. В production (HTTPS) cookie должен быть Secure | ✅ Fixed | — |
| SEC-03 | Medium | A05 | `main.py` | CORS `allow_methods=["*"]` и `allow_headers=["*"]` — слишком широкие разрешения. Рекомендуется ограничить до используемых методов | ✅ Fixed | — |
| SEC-04 | Low | A05 | `main.py` | Отсутствуют security headers (X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security, X-XSS-Protection) | ✅ Fixed | — |
| SEC-05 | Low | A07 | `schemas/auth.py` | `UserLoginRequest.password` не имеет ограничения `max_length`, что теоретически позволяет DoS через очень длинный пароль при bcrypt хешировании | ✅ Fixed | — |
| SEC-06 | Low | A04 | `middleware/rate_limiter.py` | Rate limiter fail-open при недоступности Redis. Это осознанное решение для availability, но стоит логировать | ✅ Fixed | — |
| SEC-07 | Info | A09 | `tasks/polling.py` | `logger.exception()` может включать stack trace с внутренними путями. Не содержит секретов, но стоит учитывать | Accepted | — |
| SEC-08 | Info | A06 | `pyproject.toml` | Зависимости указаны с `>=` (open ranges). Рекомендуется pin-версии для reproducibility | Documented | — |
| SEC-09 | Low | A02 | `core/security.py` | Session token 32 bytes (256 bit) — достаточно. Bcrypt используется корректно | ✅ OK | — |
| SEC-10 | Info | A03 | `repositories/` | SQLAlchemy ORM используется повсеместно (параметризованные запросы). SQL injection не обнаружен | ✅ OK | — |
| SEC-11 | Info | A01 | `api/dependencies.py` | RBAC реализован через `RoleChecker`. Admin endpoints защищены `require_admin` | ✅ OK | — |
| SEC-12 | Info | A09 | Logging | Логирование не содержит паролей, токенов или cookies. `logger.error()` выводит только тип исключения | ✅ OK | — |
| SEC-13 | Medium | A05 | `main.py` | Нет ограничения размера request body. Потенциальный DoS через большие payload | ✅ Fixed | — |
| SEC-14 | Low | A07 | `services/auth_service.py` | Session хранится в Redis с TTL 24h и продлевается при активности. Нет механизма logout-all (отмечено как TODO) | Documented | — |
| SEC-15 | Info | A10 | `services/p2p_source/mock_client.py` | HTTP клиент обращается к настраиваемому URL. В production URL фиксирован через env var — SSRF риск минимален | ✅ OK | — |
| SEC-16 | Medium | A06 | `pip` (venv) | pip 23.2.1 имеет 6 CVE (PYSEC-2023-228, CVE-2025-8869, CVE-2026-1703, CVE-2026-3219, CVE-2026-6357). Fix: обновить до pip>=26.1 | Accepted | — |
| SEC-17 | High | A06 | `fast-uri` (npm) | Path traversal via percent-encoded dot segments (GHSA-q3j6-qgpj-74h6). Fix: `npm audit fix` | ✅ Fixed | — |
| SEC-18 | Medium | A06 | `hono` (npm) | 5 уязвимостей: CSS injection, JWT validation, cache leakage, bodyLimit bypass, HTML injection. Fix: `npm audit fix` | ✅ Fixed | — |
| SEC-19 | Medium | A06 | `postcss` (npm) | XSS via unescaped `</style>` in CSS stringify (GHSA-qx2v-qp2m-jg93). Fix: `npm audit fix` | ✅ Fixed | — |
| SEC-20 | Medium | A06 | `brace-expansion` (npm) | Large numeric range defeats max DoS protection (GHSA-jxxr-4gwj-5jf2). Fix: `npm audit fix` | ✅ Fixed | — |
| SEC-21 | Medium | A06 | `ip-address` (npm) | XSS in Address6 HTML-emitting methods (GHSA-v2v4-37r5-5v8g). Fix: `npm audit fix` | ✅ Fixed | — |

---

## Детали находок

### SEC-01: Предсказуемый SECRET_KEY по умолчанию
**Риск:** Если переменная окружения не установлена, приложение использует `"change-me-in-production"` — атакующий может подделать сессии.
**Исправление:** Добавлена валидация — приложение не запустится с дефолтным ключом в production.

### SEC-02: CSRF cookie без флага Secure
**Риск:** Cookie может быть перехвачен при MitM на HTTP.
**Исправление:** Флаг `secure` устанавливается динамически на основе наличия HTTPS (определяется по env var).

### SEC-03: Широкие CORS разрешения
**Риск:** `allow_methods=["*"]` разрешает все HTTP методы включая PATCH, TRACE. `allow_headers=["*"]` разрешает произвольные заголовки.
**Исправление:** Ограничено до `["GET", "POST", "PUT", "DELETE", "OPTIONS"]` и конкретных заголовков.

### SEC-04: Отсутствие Security Headers
**Риск:** Без заголовков безопасности браузер не применяет дополнительные защиты (clickjacking, MIME sniffing, XSS).
**Исправление:** Добавлен `SecurityHeadersMiddleware`.

### SEC-05: Неограниченная длина пароля при логине
**Риск:** Bcrypt имеет ограничение 72 байта, но обработка очень длинной строки до хеширования может потреблять ресурсы.
**Исправление:** Добавлено `max_length=128` для поля password в `UserLoginRequest`.

### SEC-06: Rate limiter fail-open
**Риск:** При недоступности Redis rate limiting отключается.
**Исправление:** Добавлено логирование при fail-open для мониторинга.

---

## Рекомендации

### Приоритет 1 (реализовано в этом аудите)
1. ✅ Валидация SECRET_KEY при старте (не допускать дефолтное значение)
2. ✅ Security headers middleware (X-Content-Type-Options, X-Frame-Options, HSTS)
3. ✅ Ограничение CORS methods/headers до необходимого минимума
4. ✅ Secure flag для CSRF cookie в production
5. ✅ Ограничение длины пароля при логине
6. ✅ Логирование fail-open в rate limiter

### Приоритет 2 (рекомендации для будущих итераций)
1. Реализовать logout-all-sessions (инвалидация всех сессий пользователя)
2. Добавить Content-Security-Policy header для frontend
3. Pin-версии зависимостей в pyproject.toml
4. Добавить request body size limit на уровне reverse proxy (nginx/Railway)
5. Рассмотреть добавление `Referrer-Policy: strict-origin-when-cross-origin`
6. Добавить audit log для административных действий

### Приоритет 3 (долгосрочные)
1. Внедрить SAST в CI pipeline (bandit, semgrep)
2. Регулярный `pip-audit` / `npm audit` в CI (уже реализовано в h6-ci.yml)
3. Рассмотреть переход на JWT с refresh tokens для stateless auth
4. Добавить WAF правила на уровне CDN/reverse proxy

---

## Заключение

Общий уровень безопасности приложения — **удовлетворительный** для MVP/учебного проекта:
- ✅ SQL injection защита через ORM (SQLAlchemy)
- ✅ Аутентификация через bcrypt + Redis sessions
- ✅ CSRF protection (double-submit cookie)
- ✅ Rate limiting на auth endpoints
- ✅ RBAC для admin endpoints
- ✅ Логирование не содержит секретов

Основные улучшения применены в рамках этого аудита (SEC-01 — SEC-06, SEC-13).
