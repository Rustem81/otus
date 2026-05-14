---
inclusion: fileMatch
fileMatchPattern: "src/**"
---

# Правила React + TypeScript + Tailwind

## R1: Именование

- Компоненты: `PascalCase` — `AdCard.tsx`, `RiskIndicator.tsx`
- Хуки: `use*` — `useAuth.ts`, `useAds.ts`
- Утилиты: `camelCase` — `formatPrice.ts`
- Типы/интерфейсы: `PascalCase` — `Ad`, `MerchantInfo`
- Константы: `UPPER_SNAKE_CASE` — `API_URL`, `REFRESH_INTERVAL`
- Файлы страниц: `kebab-case` — `main.tsx`, `profile.tsx`

## R2: Компоненты

```tsx
// Правильно: функциональный компонент с типизированными props
interface AdCardProps {
  ad: Ad;
  isBest?: boolean;
  onBlock?: (merchantId: string) => void;
}

export function AdCard({ ad, isBest, onBlock }: AdCardProps) {
  // ...
}
```

- Один компонент — один файл
- Props через interface, не через inline type
- Деструктуризация props в параметрах
- Экспорт через `export function`, не `export default`

## R3: Состояние

- Локальное: `useState`, `useReducer`
- Глобальное (auth): Zustand store
- Серверное (API данные): TanStack Query или `useEffect` + `useState`
- НЕ дублируй серверное состояние в Zustand

## R4: API-вызовы

Все HTTP-запросы через `lib/api.ts`:

```tsx
import { apiGet, apiPost } from "@/lib/api";

// В компоненте
const [data, setData] = useState<AdsResponse | null>(null);
useEffect(() => {
  apiGet<AdsResponse>("/api/v1/advertisements").then(setData);
}, []);
```

- `apiGet/apiPost/apiPut/apiDelete` — единственные точки входа
- Автоматический Bearer token из localStorage
- Автоматический редирект на /login при 401

## R5: Стилизация

- Только Tailwind CSS utility classes
- shadcn/ui компоненты для UI-элементов (Card, Button, Dialog, Badge и т.д.)
- НЕ пиши кастомный CSS (кроме index.css с темой)
- Адаптивность через Tailwind breakpoints: `sm:`, `md:`, `lg:`
- Dark theme через CSS-переменные в `.dark` классе

## R6: Обработка состояний UI

Каждая страница должна обрабатывать 3 состояния:
1. **Loading** — спиннер или скелетон
2. **Error** — сообщение + кнопка retry
3. **Empty** — иконка + текст + действие (ссылка или кнопка)

```tsx
if (loading) return <Spinner />;
if (error) return <ErrorBanner message={error} onRetry={refetch} />;
if (!data.length) return <EmptyState icon={SearchX} text="Нет данных" />;
return <DataGrid data={data} />;
```

## R7: Тесты

- Фреймворк: Vitest + React Testing Library
- Файлы: `*.test.tsx` рядом с компонентом или в `__tests__/`
- Минимум: рендер без ошибок, проверка ключевых элементов, обработка событий
