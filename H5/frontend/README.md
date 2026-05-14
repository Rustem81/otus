# MEXC P2P Aggregator — Frontend

React-клиент для бэкенда MEXC P2P Агрегатора. Приложение отображает P2P-объявления с биржи MEXC, позволяет анализировать риски мерчантов, управлять чёрным списком и просматривать историю.

## Стек технологий

| Технология | Версия | Назначение |
|---|---|---|
| React | 19 | UI-фреймворк |
| TypeScript | 6 | Типизация |
| Vite | 8 | Сборка и dev-сервер |
| Tailwind CSS | 4 | Стилизация |
| shadcn/ui (Radix) | — | UI-компоненты |
| React Router | 7 | Маршрутизация |
| TanStack Query | 5 | Кэширование API |
| Zustand | 5 | Глобальное состояние (auth) |
| Lucide React | — | Иконки |
| Vitest + RTL | — | Тестирование |

## Функциональность

- Авторизация (логин / регистрация) с JWT-токенами
- Онбординг нового пользователя (выбор банков, лимитов, риск-профиля)
- Главная страница — карточки P2P-объявлений с автообновлением (15 сек)
- Детальный просмотр объявления (диалог с метриками мерчанта)
- Индикатор риска (цветовая шкала 1–10) и рейтинг мерчанта (звёзды)
- Фильтрация по направлению (BUY / SELL)
- Профиль трейдера (настройки, фильтры, KYC)
- История просмотров (timeline по датам)
- Чёрный список мерчантов (блокировка / разблокировка)
- Панель администратора (health-статусы сервисов, ошибки за 24ч)
- Dark theme (крипто-эстетика, cyan accent)
- Адаптивная вёрстка (desktop + mobile с hamburger-меню)

## Структура проекта

```
src/
├── assets/               # Статические ресурсы
├── components/           # Кастомные компоненты
│   ├── ui/               # shadcn/ui (не редактировать)
│   ├── __tests__/        # Тесты компонентов
│   │   ├── ad-card.test.tsx
│   │   ├── risk-indicator.test.tsx
│   │   ├── star-rating.test.tsx
│   │   └── payment-icons.test.tsx
│   ├── ad-card.tsx        # Карточка объявления
│   ├── ad-detail-dialog.tsx
│   ├── risk-indicator.tsx # Индикатор риска (SVG)
│   ├── star-rating.tsx    # Рейтинг звёздами
│   └── payment-icons.tsx  # Иконки способов оплаты
├── pages/                # Страницы (по одной на роут)
│   ├── login.tsx          # Авторизация
│   ├── onboarding.tsx     # Онбординг
│   ├── main.tsx           # Объявления (главная)
│   ├── profile.tsx        # Профиль (3 таба)
│   ├── history.tsx        # История просмотров
│   ├── blacklist.tsx      # Чёрный список
│   └── admin.tsx          # Панель администратора
├── layouts/              # Лейауты
│   ├── main-layout.tsx    # Sidebar + mobile hamburger
│   └── auth-layout.tsx    # Центрированная форма
├── stores/               # Zustand stores
│   └── auth.ts            # Авторизация, JWT, user
├── lib/                  # Утилиты
│   ├── api.ts             # fetch-обёртки (apiGet/Post/Put/Delete)
│   └── utils.ts           # cn() для Tailwind
├── test/                 # Настройка тестового окружения
│   └── setup.ts
├── App.tsx               # Роутинг + providers
├── main.tsx              # Точка входа (ReactDOM.createRoot)
└── index.css             # Tailwind CSS 4 + dark theme
```

## Быстрый старт

### Требования

- Node.js 18+
- npm 9+
- Бэкенд H2 (FastAPI + PostgreSQL + Redis + mock-server)

### Установка и запуск (dev)

```bash
cd H4/app
npm install
npm run dev
```

Приложение будет доступно на http://localhost:5173

### Переменные окружения

Создайте `.env` в корне `H4/app/`:

```env
VITE_API_URL=http://localhost:8000
```

### Запуск тестов

```bash
npm test          # однократный запуск
npm run test:watch # watch-режим
```

### Сборка

```bash
npm run build
npm run preview   # предпросмотр production-билда
```

## Docker

### Только фронтенд

```bash
cd H4/app
docker build -t mexc-p2p-frontend .
docker run -p 3000:80 mexc-p2p-frontend
```

### Полный стек (фронтенд + бэкенд + БД)

```bash
cd H4
docker compose up
```

Сервисы:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## Тестовый аккаунт

```
Email: test@test.com
Password: testpassword123
```

## API

Фронтенд подключается к бэкенду H2 (FastAPI). Основные эндпоинты:

| Метод | Путь | Описание |
|---|---|---|
| POST | /api/v1/auth/login | Авторизация |
| POST | /api/v1/auth/register | Регистрация |
| GET | /api/v1/auth/me | Текущий пользователь |
| GET | /api/v1/advertisements | Список объявлений |
| GET | /api/v1/profile/ | Профиль трейдера |
| PUT | /api/v1/profile/ | Обновление профиля |
| POST | /api/v1/profile/onboarding | Онбординг |
| GET | /api/v1/history | История просмотров |
| POST | /api/v1/history | Добавить в историю |
| GET | /api/v1/blacklist | Чёрный список |
| POST | /api/v1/blacklist | Заблокировать мерчанта |
| DELETE | /api/v1/blacklist/:id | Разблокировать |
| GET | /health | Health check |
| GET | /api/v1/admin/errors | Ошибки (admin) |
