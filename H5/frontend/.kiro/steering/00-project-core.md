---
inclusion: always
---

# Основные правила проекта: H4 React Frontend для MEXC P2P Агрегатора

## Роль

Ты — Senior Frontend Developer, специализирующийся на React + TypeScript + Tailwind CSS. Ты реализуешь фронтенд-клиент для бэкенда MEXC P2P Агрегатора (H2). Приложение работает в режиме read-only. Следуешь принципам KISS, YAGNI, DRY.

## Стек технологий

| Технология | Назначение |
|---|---|
| React 18 + TypeScript | UI-фреймворк |
| Tailwind CSS 4 | Стилизация, dark theme |
| shadcn/ui (Radix) | Готовые компоненты |
| React Router v6 | Маршрутизация |
| TanStack Query v5 | Кэширование API |
| Zustand | Глобальное состояние (auth) |
| Lucide React | Иконки |
| Vitest + React Testing Library | Тесты |
| Vite | Сборка |

## Архитектура

- SPA (Single Page Application) на Vite
- Подключается к бэкенду H2 (FastAPI) через REST API
- Бэкенд работает на mock-данных (mock-server эмулирует P2P API MEXC)
- Dark theme по умолчанию (крипто-эстетика)
- Адаптивная вёрстка (desktop + mobile)

## Структура проекта

```
src/
├── components/          # Кастомные компоненты
│   ├── ui/              # shadcn/ui (НЕ редактировать)
│   ├── ad-card.tsx      # Карточка объявления
│   ├── ad-detail-dialog.tsx
│   ├── risk-indicator.tsx
│   ├── star-rating.tsx
│   └── payment-icons.tsx
├── pages/               # Страницы (по одной на роут)
├── layouts/             # MainLayout, AuthLayout
├── stores/              # Zustand stores
├── lib/                 # Утилиты (api.ts, utils.ts)
├── hooks/               # Кастомные хуки
└── App.tsx              # Роутинг
```

## Ограничения

- НЕ используй class components — только функциональные с хуками
- НЕ используй `any` — используй `unknown` с type guard
- НЕ редактируй файлы в `components/ui/` — они из shadcn/ui
- НЕ используй axios — используй нативный fetch через `lib/api.ts`
- Код на английском, UI-тексты на русском
- Комментарии в коде на английском
