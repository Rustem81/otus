# H6 — ручные задачи (полный учебный гайд)

> **Для кого:** вы впервые настраиваете CI/CD, деплой, OAuth и аналитику.  
> **Что в репозитории:** код, тесты и документы уже сгенерированы AI — вам нужно **поднять окружение, зарегистрироваться на сервисах и проверить**, что всё работает.  
> **Спецификация курса:** `.kiro/specs/h6-cicd-integrations/tasks.md`  
> **Путь проекта на диске:** `C:\Project\OTUS\H6`  
> **Python venv:** `C:\Project\OTUS\H6\venv` (команды backend — через него)

---

## Как пользоваться этим файлом

1. Идите **по шагам 0 → 12**, не перескакивайте.
2. После каждого шага ставьте `[x]` в чеклистах.
3. Если застряли — в чате Cursor пишите: **«Делаем шаг N»** (например, «Делаем шаг 3 — Railway»).
4. Сохраняйте скриншоты в папку `H6/screenshots/` (создайте её сами, в git не обязательно).
5. **Никогда не коммитьте** файлы `.env` с паролями и ключами.

---

## Словарь (кратко)

| Термин | Простыми словами |
|--------|------------------|
| **CI** | GitHub при каждом push сам запускает lint и тесты |
| **CD / деплой** | Railway сам пересобирает сайт после push в `main` |
| **`.env`** | Файл с секретами **только на вашем ПК** и на сервере Railway |
| **Smoke-test** | Workflow после деплоя проверяет `/health` на prod |
| **OAuth** | «Войти через Google» — ключи выдаёт Google Cloud |
| **Переменная окружения** | Настройка для программы (URL базы, ключ API) |

---

## Условные обозначения

| Символ | Значение |
|--------|----------|
| 👤 | Сделать вручную (обязательно) |
| ⚠️ | Блокер — без этого CI или сдача не пройдут |
| 🔶 | Опционально (доп. баллы / отчёт) |
| 🤖 | Уже сделано AI — повторять не нужно |

---

## Что уже сделано AI (не дублируйте)

- [x] Папка H6 (backend, frontend, mock-server), `docker-compose.yml`
- [x] GitHub Actions: `h6-ci.yml`, `h6-deploy.yml`
- [x] structlog, `X-Request-ID`, `/health`, `/health/live`
- [x] Код Google OAuth, миграция БД, кнопка на frontend
- [x] Код Яндекс.Метрики, Sentry, Prometheus/Grafana
- [x] `security_audit.md`, `integration_documentation.md`, черновик `README.md`
- [x] Коммит на локальной ветке `main`: `feat(H6): init project with CI/CD...`

**Не делайте снова:** `git commit -m "feat(H6): init from H5"` — init уже в истории.

---

## Фактическое состояние репозитория (на момент составления гайда)

| Что проверяли | Результат |
|---------------|-----------|
| `H6/.env` | Старый файл от H5 — **пересоздать** из `.env.example` |
| Docker | Контейнеры **не были запущены** |
| Git | `main`, **+2 коммита** не на GitHub; ветки `feature/h6-integrations` нет |
| `README.md` | URL — заглушки `<!-- TODO -->` |
| `integration_documentation.md` | Галочки ✅ **не подтверждены** реальной настройкой |
| `npm run lint` | **4 ошибки** → CI красный |
| `ruff check` | **112 замечаний** (большинство чинится `--fix`) |
| Railway, Google, Метрика, UptimeRobot | **Не настроены** |

---

## Карта шагов (порядок важен)

| Шаг | Название | Зачем |
|-----|----------|--------|
| **0** ⚠️ | Починить lint → зелёный CI | Иначе GitHub Actions красный |
| **1** 👤 | Локально: `.env` + Docker | Проверка «у меня на ПК работает» |
| **2** 👤 | Push на GitHub | Код виден преподавателю / Railway |
| **3** 👤 | Railway + переменная `BACKEND_URL` | Prod-сервер в интернете |
| **4** 👤 | README и честная документация | Ссылки не врут |
| **5** 👤 | pip-audit, npm audit | Отчёт по безопасности |
| **6** 👤 | Проверка логов `request_id` | Задание по structlog |
| **7** 👤 | UptimeRobot | Внешний мониторинг (нужен prod URL) |
| **8** 👤 | Google OAuth | Вход через Google |
| **9** 👤 | Яндекс.Метрика | Аналитика на prod |
| **10** 🔶 | Sentry | По желанию |
| **11** 🔶 | Prometheus + Grafana | По желанию, локально |
| **12** 👤 | Сдача OTUS | Скриншоты + ссылки |

---

# Шаг 0. ⚠️ Починить CI (lint)

### Зачем

Workflow **H6 CI** на GitHub запускает `ruff check` и `npm run lint`. Сейчас они падают → вся сдача выглядит невыполненной.

### 0.1 Backend — ruff

**Что делаем:** автоматически исправляем стиль кода, остаток — вручную или с AI.

```powershell
cd C:\Project\OTUS\H6\backend
..\venv\Scripts\ruff.exe check . --fix
..\venv\Scripts\ruff.exe check .
```

- [ ] Первая команда (`--fix`) выполнилась
- [ ] Вторая команда — **0 errors** (или вы знаете, что осталось и попросили AI помочь)

**Если остались ошибки F821 / E712** — напишите в чат: «Исправь остаток ruff в H6/backend».

### 0.2 Frontend — eslint

```powershell
cd C:\Project\OTUS\H6\frontend
npm run lint
```

Типичные файлы с ошибками:

- `src/pages/auth-callback.tsx`
- `src/components/ui/badge.tsx`, `button.tsx`, `tabs.tsx`

- [ ] `npm run lint` — **без ошибок** (exit code 0)

**Если не знаете, как чинить** — в чат: «Исправь eslint в H6/frontend для CI».

### 0.3 Отправить на GitHub и проверить Actions

```powershell
cd C:\Project\OTUS
git add -A
git status
```

Убедитесь: в списке **нет** `H6/.env`, `H6/frontend/.env`.

```powershell
git commit -m "fix(H6): resolve lint issues for CI"
git push origin main
```

**Проверка в браузере:**

1. Откройте https://github.com/Rustem81/otus/actions  
2. Кликните последний запуск **H6 CI**  
3. Все jobs зелёные (галочки)

- [ ] Push выполнен  
- [ ] **H6 CI** — зелёный  

**Критерий шага 0:** на GitHub Actions workflow `h6-ci.yml` успешен.

---

# Шаг 1. 👤 Локальный запуск (Docker)

### Зачем

Перед облаком убедиться: проект стартует у вас на компьютере.

### Что понадобится

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) установлен и **запущен** (иконка в трее)
- Git уже есть (вы в репозитории OTUS)

### 1.1 Создать правильный `.env`

**Важно:** не редактируйте старый `.env` от H5 — скопируйте шаблон H6.

```powershell
cd C:\Project\OTUS\H6
copy .env.example .env
notepad .env
```

Заполните **минимум** (остальное можно оставить как в example):

| Переменная | Что писать |
|------------|------------|
| `SECRET_KEY` | Любая длинная случайная строка (**не** `change-me-in-production`) |
| `APP_VERSION` | `1.0.0` |
| `METRICS_ENABLED` | `true` |
| `LOG_FORMAT` | `console` |
| `DATABASE_URL` | Оставить как в example (для Docker) |
| `REDIS_URL` | `redis://redis:6379` |

**Сгенерировать SECRET_KEY (PowerShell):**

```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }) -as [byte[]])
```

Скопируйте результат в строку `SECRET_KEY=...` в `.env`.

- [ ] Файл `H6/.env` создан из `.env.example`  
- [ ] `SECRET_KEY` заменён  

### 1.2 Запустить контейнеры

```powershell
cd C:\Project\OTUS\H6
docker compose up -d
```

Первый раз может качать образы 5–15 минут.

```powershell
docker compose ps
```

В колонке **STATUS** у `backend`, `frontend`, `mock-server`, `postgres`, `redis` должно быть `running` (или `Up`).

**Если сервис `Exited` / `Restarting`:**

```powershell
docker compose logs backend
docker compose logs postgres
```

Частые причины: Docker не запущен; порт 8000 или 5173 занят другой программой.

- [ ] Все 5 основных сервисов running  

### 1.3 Проверить backend

```powershell
curl http://localhost:8000/health
```

**Успех:** JSON, например `"status":"ok"` или `"degraded"`, есть поля `version`, `dependencies`.

**Swagger (документация API):** http://localhost:8000/docs  

- [ ] `/health` отвечает 200  

### 1.4 Проверить frontend

Браузер: http://localhost:5173  

- [ ] Страница открывается (логин или главная)  

**Тестовый вход (если есть в README):** email `test@test.com`, пароль из README H6.

**Критерий шага 1:** локально backend + frontend работают.

---

# Шаг 2. 👤 Git и GitHub

### Зачем

Код должен быть на https://github.com/Rustem81/otus — оттуда Railway тянет проект.

### Текущая ситуация

Коммит с H6 уже есть локально на `main`, но **не запушен** (`ahead 2`).

### Вариант A — как в задании OTUS (отдельная ветка)

```powershell
cd C:\Project\OTUS
git checkout -b feature/h6-integrations
git push -u origin feature/h6-integrations
```

Потом на GitHub: **Pull requests** → New PR → `feature/h6-integrations` → `main` → Merge.

- [ ] Ветка на GitHub  
- [ ] PR смержен (или преподаватель принял ветку)  

### Вариант B — проще (всё в main)

```powershell
cd C:\Project\OTUS
git push origin main
```

- [ ] На GitHub в папке `H6/` виден ваш код  

### Проверка секретов

```powershell
git status
```

- [ ] **Нет** `H6/.env` в staged/untracked для коммита  

**Критерий шага 2:** репозиторий на GitHub актуален, секреты не закоммичены.

---

# Шаг 3. 👤 Railway (деплой в облако) + GitHub Variable

### Зачем

Приложение должно открываться по HTTPS в интернете, не только на `localhost`.

### 3.1 Регистрация и проект

1. Откройте https://railway.app/  
2. **Login** → **GitHub** → разрешите доступ к репозиторию  
3. **New Project** → **Deploy from GitHub repo**  
4. Выберите репозиторий **`Rustem81/otus`** (или ваш fork)  
5. Railway создаст первый сервис — его можно переименовать позже  

- [ ] Проект Railway создан  

### 3.2 Три сервиса из одного репо

В проекте Railway нужно **три отдельных сервиса** (не один):

| Имя в Railway | Root Directory | Watch Paths (если есть поле) |
|---------------|----------------|----------------------------|
| backend | `H6/backend` | `H6/backend/**` |
| frontend | `H6/frontend` | `H6/frontend/**` |
| mock-server | `H6/mock-server` | `H6/mock-server/**` |

**Как добавить второй/третий сервис:** в проекте → **+ New** → **GitHub Repo** → тот же репозиторий → в Settings указать Root Directory.

- [ ] Три сервиса созданы с правильными путями  

### 3.3 База PostgreSQL и Redis

1. В проекте Railway: **+ New** → **Database** → **PostgreSQL**  
2. Ещё раз **+ New** → **Database** → **Redis**  

- [ ] PostgreSQL plugin есть  
- [ ] Redis plugin есть  

### 3.4 Переменные backend

Откройте сервис **backend** → вкладка **Variables** → **Raw Editor** или добавляйте по одной:

| Имя | Значение | Пояснение |
|-----|----------|-----------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Railway подставит ссылку на БД |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Ссылка на Redis |
| `SECRET_KEY` | своя случайная строка | Как в шаге 1, **новая** для prod |
| `P2P_MOCK_BASE_URL` | `http://mock-server.railway.internal:8001` | Внутренний адрес mock |
| `P2P_DATA_SOURCE` | `mock` | Источник данных |
| `APP_VERSION` | `1.0.0` | Версия в `/health` |
| `RAILWAY_ENVIRONMENT` | `production` | Включит JSON-логи на сервере |

**`BACKEND_CORS_ORIGINS`** — добавите **после** шага 3.5, когда будет URL frontend.

- [ ] Переменные backend заданы (кроме CORS — после домена frontend)  

### 3.5 Публичные домены

**Backend:** Settings → **Networking** → **Generate Domain** → скопируйте URL, например `https://backend-production-xxxx.up.railway.app`

**Frontend:** то же для сервиса frontend.

**Mock-server:** домен **НЕ** генерировать — только internal.

В backend Variables добавьте:

```
BACKEND_CORS_ORIGINS=https://<ваш-frontend-домен>.up.railway.app
```

В frontend Variables:

```
VITE_API_URL=https://<ваш-backend-домен>.up.railway.app
```

**Важно для Vite:** после смены `VITE_*` Railway **пересоберёт** frontend (Redeploy).

- [ ] Домены backend и frontend есть  
- [ ] `VITE_API_URL` и `BACKEND_CORS_ORIGINS` заполнены  
- [ ] У mock-server нет публичного URL  

### 3.6 GitHub Variable для smoke-test

1. https://github.com/Rustem81/otus/settings/variables/actions  
2. **New repository variable**  
3. Name: `BACKEND_URL`  
4. Value: `https://<backend-домен>.up.railway.app` (**без** `/health` в конце)

- [ ] `BACKEND_URL` в GitHub Variables  

### 3.7 Деплой и проверка

```powershell
cd C:\Project\OTUS
git push origin main
```

1. Railway → каждый сервис → вкладка **Deployments** → статус **Success**  
2. В браузере: `https://<backend>/health` — JSON со `"status":"ok"`  
3. В браузере: `https://<frontend>/` — открывается приложение  
4. GitHub Actions → **H6 Post-Deploy Verification** — подождать ~3 мин (там sleep 180 с) → зелёный  

**Если smoke-test красный:**

- `BACKEND_URL` неверный или с лишним `/health`  
- backend ещё деплоится  
- в health `status` не `ok` (падет postgres/redis/mock)  

- [ ] Prod `/health` → ok  
- [ ] `h6-deploy` green  

**Критерий шага 3:** приложение в интернете, smoke-test зелёный.

**Запишите URL (понадобятся дальше):**

```
BACKEND_PROD=https://...
FRONTEND_PROD=https://...
```

---

# Шаг 4. 👤 README и честная документация

### 4.1 README.md

Откройте `H6/README.md`, найдите `<!-- TODO: вставить Railway URL -->` и вставьте **ваши** URL из шага 3.

- [ ] Frontend (prod)  
- [ ] Backend API (prod)  
- [ ] Swagger (`.../docs`)  
- [ ] Health Check (`.../health`)  
- [ ] UptimeRobot — после шага 7  

```powershell
git add H6/README.md
git commit -m "docs(H6): add production URLs to README"
git push
```

### 4.2 integration_documentation.md

1. Откройте `H6/integration_documentation.md`  
2. Таблица **«Использование AI»** — замените примеры на **ваши** реальные промпты из Cursor  
3. Чеклист в конце — уберите ✅ там, где вы **не проверяли**; поставьте только то, что сделали  
4. В разделах CI/CD, OAuth, Метрика — вставьте prod URL  

- [ ] Документация соответствует факту  

**Критерий шага 4:** ссылки из README открываются в браузере.

---

# Шаг 5. 👤 Аудит безопасности

### Зачем

Домашка требует не только отчёт AI, но и **ваш** запуск сканеров зависимостей.

### 5.1 pip-audit (Python)

```powershell
cd C:\Project\OTUS\H6\backend
..\venv\Scripts\python.exe -m pip install pip-audit
..\venv\Scripts\pip-audit.exe | Tee-Object ..\report-pip-audit.txt
```

Файл `H6/report-pip-audit.txt` — для отчёта, **не коммитьте**, если там ничего лишнего.

- [ ] pip-audit выполнен, вывод сохранён  

### 5.2 npm audit (JavaScript)

```powershell
cd C:\Project\OTUS\H6\frontend
npm audit | Tee-Object ..\report-npm-audit.txt
```

- [ ] npm audit выполнен, вывод сохранён  

### 5.3 Обновить security_audit.md

1. Откройте `H6/security_audit.md`  
2. Если pip-audit/npm audit нашли **High/Critical** — либо обновите пакеты, либо в таблице напишите **Accepted** + причину  
3. Заполните колонки **Статус** и **Коммит** там, где вы что-то меняли  

### 5.4 Секреты в git и workflows

```powershell
cd C:\Project\OTUS
git status
```

- [ ] Нет `.env` в коммите  

Откройте `.github/workflows/h6-ci.yml` — не должно быть паролей в открытом виде, только `${{ secrets.* }}` / `${{ vars.* }}`.

```powershell
git add H6/security_audit.md
git commit -m "docs(H6): security audit outputs and status"
git push
```

**Критерий шага 5:** отчёты запущены, `security_audit.md` актуален.

---

# Шаг 6. 👤 Проверка логирования (structlog + request_id)

### Зачем

Убедиться, что в логах есть идентификатор запроса — это требование H6.

### Локально (Docker уже запущен)

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/ads
```

Смотрите логи:

```powershell
cd C:\Project\OTUS\H6
docker compose logs backend --tail 30
```

- [ ] В логах есть поле `request_id`  

Проверка своего ID:

```powershell
curl -H "X-Request-ID: test-123" http://localhost:8000/health -v
```

В выводе `-v` найдите строку `< X-Request-ID: test-123`.

- [ ] В логах `request_id=test-123`  
- [ ] В ответе заголовок `X-Request-ID`  

Сохраните 10–20 строк в `H6/screenshots/logs-local.txt` (не в git).

### На Railway

1. Сервис backend → **Deployments** → последний деплой → **View Logs**  
2. Обновите страницу prod в браузере  
3. В логах JSON и поле `request_id`  

- [ ] Логи на Railway в JSON с `request_id`  

**Критерий шага 6:** request_id виден локально и на prod.

---

# Шаг 7. 👤 UptimeRobot

> Делать **после шага 3** — нужен URL `https://<backend>/health`.

### Пошагово

1. https://uptimerobot.com/ → **Register** (Free plan)  
2. Подтвердите email  
3. **Add New Monitor**  
   - Monitor Type: **HTTP(s)**  
   - Friendly Name: `MEXC P2P Backend`  
   - URL: `https://<ваш-backend>.up.railway.app/health`  
   - Monitoring Interval: **5 minutes**  
4. **Create Monitor**  
5. **My Settings** → **Alert Contacts** → добавьте email → подтвердите письмо  
6. Привяжите контакт к монитору  
7. Подождите 5–10 минут — статус **Up** (зелёный)  

- [ ] Монитор Up  
- [ ] Скриншот дашборда в `H6/screenshots/uptimerobot.png`  
- [ ] Ссылка добавлена в `README.md`  

**Опционально для обучения:** в Railway остановите backend → через 5–10 мин придёт email об падении → снова запустите.

**Критерий шага 7:** внешний мониторинг показывает Up.

---

# Шаг 8. 👤 Google OAuth (вход через Google)

### Зачем

Код OAuth уже в проекте — нужны **ключи** от Google.

### 8.1 Google Cloud Console

1. https://console.cloud.google.com/  
2. Вверху: **Select a project** → **New Project** → имя `MEXC P2P Insight` → **Create**  
3. Убедитесь, что выбран этот проект  

#### OAuth consent screen (экран согласия)

4. Меню ☰ → **APIs & Services** → **OAuth consent screen**  
5. User Type: **External** → **Create**  
6. Заполните:
   - App name: `MEXC P2P Insight`
   - User support email: ваш email
   - Developer contact: ваш email  
7. **Save and Continue**  
8. Scopes → **Add or Remove Scopes** → добавьте `email`, `profile`, `openid` → **Save** → **Continue**  
9. **Test users** → **Add users** → ваш Gmail → **Save**  
10. **Back to Dashboard** (приложение в режиме Testing — этого достаточно для учёбы)  

#### Credentials (ключи)

11. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**  
12. Application type: **Web application**  
13. Name: `MEXC P2P Web Client`  
14. **Authorized JavaScript origins** — Add URI:
    - `http://localhost:5173`
    - `https://<ваш-frontend>.up.railway.app`  
15. **Authorized redirect URIs** — Add URI:
    - `http://localhost:8000/api/v1/auth/google/callback`
    - `https://<ваш-backend>.up.railway.app/api/v1/auth/google/callback`  
16. **Create** → скопируйте **Client ID** и **Client Secret** (Secret показывается один раз!)  

- [ ] OAuth client создан  
- [ ] Origins и Redirect URI точно совпадают (без лишнего `/` в конце)  

### 8.2 Переменные окружения

**Локально** — допишите в `H6/.env`:

```env
GOOGLE_CLIENT_ID=xxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

Перезапустите backend:

```powershell
cd C:\Project\OTUS\H6
docker compose restart backend
```

**Railway backend** — Variables:

| Переменная | Значение |
|------------|----------|
| `GOOGLE_CLIENT_ID` | тот же Client ID |
| `GOOGLE_CLIENT_SECRET` | тот же Secret |
| `GOOGLE_REDIRECT_URI` | `https://<backend>/api/v1/auth/google/callback` |

**GitHub Secrets** (если преподаватель требует): Settings → Secrets → `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`.

- [ ] Переменные в `.env` и Railway  

### 8.3 Тест локально

1. http://localhost:5173 → страница входа  
2. **Войти через Google**  
3. Выберите тестовый Google-аккаунт (из Test users)  
4. Разрешите доступ  
5. Должен вернуть в приложение  

Проверка API (в браузере после входа или через DevTools → Application → Cookies):

- http://localhost:8000/api/v1/auth/me — должен быть JSON с пользователем  

- [ ] OAuth локально работает  

### 8.4 Тест на prod

1. Откройте prod frontend  
2. Повторите вход через Google  
3. Если ошибка `redirect_uri_mismatch` — проверьте URI в Google Console и `GOOGLE_REDIRECT_URI` на Railway  

- [ ] OAuth на prod работает  
- [ ] Скриншот: экран Google + главная приложения  

**Критерий шага 8:** вход через Google локально и на prod.

---

# Шаг 9. 👤 Яндекс.Метрика

### 8.1 Создать счётчик

1. https://metrika.yandex.ru/ → войти под Яндекс ID  
2. **Добавить счётчик**  
   - Имя: `MEXC P2P Insight`  
   - Адрес сайта: URL **prod frontend**  
   - Часовой пояс: ваш  
3. Скопируйте **номер счётчика** (только цифры)  

### 8.2 Цели (JavaScript-событие)

Счётчик → **Настройки** → **Цели** → **Добавить цель** → тип **JavaScript-событие**:

| Идентификатор | Название |
|---------------|----------|
| `login` | Успешный вход |
| `register` | Регистрация |
| `oauth_login` | Вход через Google |
| `view_ad` | Просмотр объявления |
| `blacklist_add` | Блокировка мерчанта |

Идентификатор должен **точно** совпадать с кодом (латиница, без пробелов).

### 8.3 Подключить к frontend

Файл `H6/frontend/.env` (создайте, если нет):

```env
VITE_YM_COUNTER_ID=12345678
```

Railway → сервис **frontend** → Variable `VITE_YM_COUNTER_ID` → **Redeploy**.

- [ ] Переменная локально и на Railway  

### 8.4 Проверка

1. Prod frontend **без** AdBlock  
2. Метрика → **Отчёты** → **В реальном времени** — через 1–3 мин появится визит  
3. Войдите в приложение (логин/пароль) — цель `login`  
4. Откройте объявление — цель `view_ad`  

**Localhost:** в dev Метрика обычно **не** грузится — это нормально, в консоли не должно быть красных ошибок.

- [ ] Визит на prod виден  
- [ ] Цели срабатывают  
- [ ] 2 скриншота в `H6/screenshots/`  

**Критерий шага 9:** Метрика показывает визиты и цели.

---

# Шаг 10. 🔶 Sentry (опционально)

1. https://sentry.io/ → регистрация  
2. **Create Project** → платформа **Python** → скопируйте **DSN**  
3. Второй проект → **React** → DSN для frontend  

| Где | Переменная |
|-----|------------|
| `H6/.env` | `SENTRY_DSN_BACKEND=...`, `SENTRY_ENVIRONMENT=development` |
| `H6/frontend/.env` | `VITE_SENTRY_DSN=...` |
| Railway backend | `SENTRY_DSN_BACKEND`, `SENTRY_ENVIRONMENT=production` |
| Railway frontend | `VITE_SENTRY_DSN` |

Проверка: спровоцируйте ошибку на prod → в Sentry → **Issues** появится запись → скриншот.

- [ ] 🔶 Issue в Sentry (если делали шаг)  

---

# Шаг 11. 🔶 Prometheus + Grafana (опционально, локально)

```powershell
cd C:\Project\OTUS\H6
docker compose up -d
curl http://localhost:8000/metrics
```

| URL | Что проверить |
|-----|----------------|
| http://localhost:9090/targets | target `fastapi` = **UP** |
| http://localhost:3001 | Grafana, логин `admin` / `admin` → сменить пароль |
| Dashboards | **MEXC P2P** — графики после нескольких запросов к API |

- [ ] 🔶 Скриншот Grafana (если делали шаг)  

---

# Шаг 12. 👤 Финальная сдача на OTUS

### 12.1 Документы

- [ ] `integration_documentation.md` — правда, ваши URL и промпты  
- [ ] `security_audit.md` — актуален  
- [ ] `README.md` — без TODO  

### 12.2 Скриншоты (минимум для сдачи)

Папка `H6/screenshots/`:

- [ ] GitHub Actions — H6 CI green  
- [ ] GitHub Actions — h6-deploy green  
- [ ] Railway — три сервиса running  
- [ ] OAuth — Google → приложение  
- [ ] Яндекс.Метрика — реальное время  
- [ ] UptimeRobot — Up  
- [ ] 🔶 Sentry, Grafana — если делали  

### 12.3 Финальный чеклист

- [ ] Push в `main` → Railway обновился  
- [ ] `h6-ci` и `h6-deploy` зелёные  
- [ ] `/health` на prod → `"status":"ok"`  
- [ ] OAuth на prod  
- [ ] Метрика: визиты и цели  
- [ ] UptimeRobot Up  
- [ ] Логи Railway: JSON + `request_id`  

### 12.4 Git (если работали в ветке)

```powershell
git checkout main
git merge feature/h6-integrations
git push origin main
```

### 12.5 Отправка на OTUS

- [ ] Ссылка на репозиторий: https://github.com/Rustem81/otus/tree/main/H6  
- [ ] Ссылка на prod **frontend**  
- [ ] Ссылка на prod **backend** (и `/docs` при необходимости)  

---

## Сводная таблица (tasks.md → статус)

| tasks.md | Тема | Статус |
|----------|------|--------|
| — | Шаг 0: lint / CI | ⬜ |
| §2 | Локально + git | ⬜ |
| §5 | Railway + GitHub | ⬜ |
| §7 | Security audit | ⬜ |
| §9 | Логирование | ⬜ |
| §11 | UptimeRobot | ⬜ |
| §17 | Google OAuth | ⬜ |
| §19 | Яндекс.Метрика | ⬜ |
| §21* | Sentry | 🔶 |
| §23* | Prometheus/Grafana | 🔶 |
| §26 | Сдача | ⬜ |

Меняйте ⬜ на ✅ по мере выполнения.

---

## Полезные команды (Windows)

```powershell
# Корень H6
cd C:\Project\OTUS\H6

# Docker
docker compose up -d
docker compose ps
docker compose logs -f backend
docker compose restart backend

# Backend lint (venv)
cd backend
..\venv\Scripts\ruff.exe check .

# Frontend
cd ..\frontend
npm run lint
npm run test -- --run

# Git
cd C:\Project\OTUS
git status
git push origin main
```

---

## Частые ошибки

| Симптом | Что проверить |
|---------|----------------|
| CI красный на lint | Шаг 0 |
| `redirect_uri_mismatch` (Google) | URI в Console = `GOOGLE_REDIRECT_URI` на Railway |
| Frontend не видит API | `VITE_API_URL` на Railway + redeploy frontend |
| CORS error в браузере | `BACKEND_CORS_ORIGINS` = точный URL frontend |
| smoke-test failed | `BACKEND_URL` в GitHub без `/health`; health возвращает `ok` |
| Метрика пустая | AdBlock выключен; `VITE_YM_COUNTER_ID`; prod, не localhost |
| Docker не стартует | Docker Desktop запущен; порты 8000/5173 свободны |

---

## Работа с AI в Cursor

Пишите коротко:

- `Делаем шаг 0` — lint  
- `Делаем шаг 3` — Railway, застрял на Variables  
- `Ошибка redirect_uri_mismatch` — разбор OAuth  

Не переходите к следующему шагу, пока не выполнен **критерий готовности** текущего.
