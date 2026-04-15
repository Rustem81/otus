# H4: Разработка Frontend-приложения с AI-агентом

## Контекст

Лабораторная работа H4 — создание нового фронтенд-клиента для бэкенда MEXC P2P Агрегатора (H2).
Используем ТЗ из H3 (technical_specification.md, user_stories.md, ui_concepts/).
Реализуем Концепцию 2 из H3: карточный интерфейс, dark theme, крипто-эстетика.

## Стек

| Технология | Назначение |
|---|---|
| React 18 + TypeScript | UI-фреймворк |
| Tailwind CSS 4 | Стилизация, dark theme |
| shadcn/ui | Готовые компоненты (Card, Dialog, Table, Badge, Tabs и др.) |
| React Router v6 | Маршрутизация |
| TanStack Query v5 | Кэширование API-запросов |
| Orval | Генерация API-клиента из OpenAPI бэкенда H2 |
| Vitest + React Testing Library | Тесты |
| Vite | Сборка |

## Архитектура

```
H4/
├── src/
│   ├── api/              # Orval-сгенерированный клиент (из H2 бэкенда)
│   ├── components/       # shadcn/ui + кастомные компоненты
│   │   ├── ui/           # shadcn/ui базовые (Card, Button, Dialog...)
│   │   ├── AdCard.tsx            # Карточка объявления
│   │   ├── AdDetailDialog.tsx    # Модальное окно деталей
│   │   ├── FilterChips.tsx       # Фильтры-чипсы
│   │   ├── RiskIndicator.tsx     # Круговой индикатор риска
│   │   └── ProfitBadge.tsx       # Бейдж доходности
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── OnboardingPage.tsx
│   │   ├── MainPage.tsx          # Сетка карточек объявлений
│   │   ├── ProfilePage.tsx
│   │   ├── HistoryPage.tsx
│   │   ├── BlacklistPage.tsx
│   │   └── AdminPage.tsx
│   ├── layouts/
│   │   ├── MainLayout.tsx        # Sidebar + header + content
│   │   └── AuthLayout.tsx        # Центрированная карточка
│   ├── hooks/                    # Кастомные хуки
│   ├── stores/                   # Zustand (auth state)
│   ├── lib/                      # Утилиты
│   └── App.tsx
├── tests/
│   ├── AdCard.test.tsx
│   ├── FilterChips.test.tsx
│   └── LoginPage.test.tsx
├── public/
├── orval.config.ts
├── tailwind.config.ts
├── vite.config.ts
├── package.json
├── Dockerfile
├── README.md
└── development_report.md         # Отчёт о разработке (для сдачи)
```

## Подключение к бэкенду H2

Фронтенд H4 подключается к тому же бэкенду H2:
- Бэкенд: http://localhost:8000 (Docker из H2)
- Mock-server: http://localhost:8001 (эмуляция P2P API)
- Orval генерирует клиент из http://localhost:8000/openapi.json
- Никаких изменений в бэкенде не требуется

## Страницы и маппинг на User Stories (H3)

| Страница | User Stories | Ключевые компоненты |
|---|---|---|
| LoginPage | US-1 | Card, Input, Button |
| OnboardingPage | US-2 | Steps (кастомный), ToggleGroup, Select |
| MainPage | US-3, US-4, US-5, US-6, US-7, US-9 | AdCard (сетка), FilterChips, RiskIndicator, ProfitBadge, Dialog |
| ProfilePage | US-10 | Tabs, Input, Select, Button |
| HistoryPage | US-12 | Table или Timeline |
| BlacklistPage | US-11 | Card (сетка), Button |
| AdminPage | US-13, US-14 | Card (статусы), Table (ошибки), Switch |

## Визуальный стиль (Концепция 2 из H3)

- Dark theme: фон #1a1a2e, карточки #16213e, акцент cyan #0ff
- Карточки вместо таблицы на главном экране
- Круговой индикатор риска (зелёный/жёлтый/красный)
- Фильтры как чипсы в верхней панели
- Кнопка «Открыть в MEXC» на каждой карточке
- BUY/SELL toggle с цветовой индикацией

## Что нужно сдать

1. Репозиторий с кодом (GitHub)
2. Работающее приложение (локально или деплой)
3. `development_report.md` — процесс, промпты, проблемы, выводы
4. Минимум 3 теста (Vitest)

---

## Исходные материалы от v0.dev

В `H4/Text-to-UI/` лежит сгенерированное v0.dev приложение (Next.js + shadcn/ui + Tailwind).

Что переиспользуем:
- `components/merchant-card.tsx` — карточка объявления (адаптируем под типы бэкенда)
- `components/risk-indicator.tsx` — круговой SVG-индикатор (поменяем шкалу 0-100 → 1-10)
- `components/filter-bar.tsx` — фильтры-чипсы (заменим банки на РФ)
- `components/star-rating.tsx` — звёзды рейтинга (без изменений)
- `components/payment-icons.tsx` — иконки оплаты (добавим СБП, Сбербанк и др.)
- `components/ui/*` — все shadcn/ui компоненты (копируем как есть)
- Визуальный стиль: dark theme, цвета, типографика

Что НЕ переиспользуем (переделываем):
- Next.js → Vite + React Router (SPA, не нужен SSR)
- Захардкоженные mock-данные → Orval + бэкенд H2
- `app/page.tsx` → разбиваем на отдельные страницы

Что добавляем (отсутствует в v0.dev):
- LoginPage, OnboardingPage, ProfilePage, HistoryPage, BlacklistPage, AdminPage
- Модальное окно деталей объявления (AdDetailDialog)
- Маркер read-only в шапке
- Автообновление данных (таймер 15 сек)
- Чистая доходность с tooltip-детализацией
- Обработка ошибок (баннеры, retry, пустые состояния)
- Подключение к бэкенду H2 через Orval

## Задачи

### 🔴 Задачи для ТЕБЯ (ручные, не автоматизируемые)

1. **Сгенерировать UI в v0.dev** (опционально, но рекомендуется)
   - Открыть https://v0.dev
   - Вставить промпт Концепции 2 из `H3/ui_concepts/README.md`
   - Сохранить результат (скриншот + код если даст)
   - Это покажет преподавателю использование Text-to-UI инструментов

2. **Запустить бэкенд H2** перед разработкой фронтенда
   ```bash
   cd H2
   docker compose -f docker-compose.dev.yml up -d
   ```
   Убедиться что http://localhost:8000/docs работает

3. **Проверить приложение в браузере** после каждого этапа
   - Десктоп (1920px, 1366px)
   - Мобильный (375px) — через DevTools
   - Скриншоты багов → скинуть мне для исправления

4. **Написать development_report.md** — описать процесс:
   - Какие промпты давал Kiro
   - Какие проблемы возникали
   - Как использовал v0.dev (если использовал)
   - Выводы

5. **Сделать скриншоты** для отчёта:
   - Главный экран (карточки)
   - Мобильная версия
   - Карточка объявления (модальное окно)
   - Профиль

### 🟢 Задачи для KIRO (автоматизируемые)

1. Инициализация проекта (Vite + React + TS + Tailwind + shadcn/ui)
2. Настройка Orval (генерация API-клиента из бэкенда H2)
3. Реализация всех страниц и компонентов
4. Dark theme + адаптивная вёрстка
5. Написание 3+ тестов (Vitest + RTL)
6. Dockerfile + README.md
7. Рефакторинг и оптимизация

---

## Порядок выполнения

```
Шаг 1: [KIRO] Инициализация проекта
Шаг 2: [KIRO] Настройка Orval + подключение к бэкенду H2
Шаг 3: [ТЫ] Запуск бэкенда H2
Шаг 4: [KIRO] Реализация Layout + роутинг + auth
Шаг 5: [KIRO] MainPage (карточки объявлений + фильтры)
Шаг 6: [ТЫ] Проверка в браузере, скриншоты багов
Шаг 7: [KIRO] Остальные страницы (Profile, History, Blacklist, Admin, Onboarding)
Шаг 8: [KIRO] Адаптивная вёрстка (мобильная версия)
Шаг 9: [ТЫ] Проверка мобильной версии в DevTools
Шаг 10: [KIRO] Тесты (3+ штуки)
Шаг 11: [KIRO] Dockerfile + README
Шаг 12: [ТЫ] development_report.md + скриншоты
Шаг 13: [ТЫ] Пуш в GitHub
```

## Ссылки на контекст

- ТЗ: `H3/technical_specification.md`
- User Stories: `H3/user_stories.md`
- UI-концепции: `H3/ui_concepts/README.md`
- Бэкенд: `H2/backend/`
- OpenAPI: http://localhost:8000/openapi.json
- Steering-правила H2: `H2/.kiro/steering/`
- Промпт-шаблоны H2: `H2/prompt_templates.md`
