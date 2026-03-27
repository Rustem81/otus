---
inclusion: fileMatch
fileMatchPattern: "frontend/**"
---

# Правила фронтенда (Vue.js + Quasar + TypeScript)

## Структура проекта

```
frontend/
├── src/
│   ├── api/                    # Сгенерированный Orval-клиент (НЕ редактировать вручную)
│   │   ├── model/              # TypeScript-типы из OpenAPI
│   │   └── endpoints/          # Хуки и функции запросов
│   ├── components/
│   │   ├── advertisement/      # AdvertisementTable, RiskScoreBadge, ProfitabilityTooltip
│   │   ├── profile/            # ProfileForm, BankSelector, RiskProfileSelector
│   │   ├── admin/              # SourceStatus, ErrorStats
│   │   └── common/             # ReadOnlyBadge, LoadingState, ErrorState
│   ├── composables/            # useAuth, useFilters, usePolling, useProfile
│   ├── layouts/                # MainLayout.vue (с ReadOnlyBadge в шапке)
│   ├── pages/                  # DashboardPage, ProfilePage, AdminPage, LoginPage
│   ├── router/                 # Vue Router конфигурация
│   ├── stores/                 # Pinia stores (auth, filters, advertisements)
│   ├── types/                  # Дополнительные типы (не из Orval)
│   └── boot/                   # Quasar boot files (axios, auth, orval)
├── orval.config.ts             # Конфигурация Orval
├── quasar.config.js
├── tsconfig.json
├── Dockerfile
└── .env.example
```

## Стиль кода TypeScript/Vue

### Правило F1: TypeScript strict mode

`strict: true` в tsconfig. Никогда `any` — используй `unknown` с type guard.

### Правило F2: Именование

- Переменные и функции: `camelCase`
- Компоненты Vue: `PascalCase` — `AdvertisementTable.vue`
- Типы и интерфейсы: `PascalCase` — `AdvertisementDTO`, `MerchantMetrics`
- Константы: `UPPER_SNAKE_CASE`
- Файлы компонентов: `PascalCase.vue`
- Файлы composables: `use*.ts` — `useAuth.ts`, `useFilters.ts`
- Файлы stores: `*.store.ts` — `auth.store.ts`

### Правило F3: Только Composition API + script setup

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';
import type { AdvertisementResponse } from '@/api/model';

const props = defineProps<{
  advertisement: AdvertisementResponse;
}>();

const riskColor = computed(() => {
  if (props.advertisement.riskScore <= 3) return 'positive';
  if (props.advertisement.riskScore <= 7) return 'warning';
  return 'negative';
});
</script>
```

### Правило F4: Orval для API-клиента

Фронтенд НЕ пишет HTTP-запросы вручную. Всё взаимодействие с бэкендом — через сгенерированный Orval-клиент:

1. Бэкенд генерирует OpenAPI-схему автоматически (FastAPI делает это из коробки)
2. Orval генерирует TypeScript-типы и vue-query хуки
3. Фронтенд использует сгенерированные хуки в компонентах

```ts
// orval.config.ts
import { defineConfig } from 'orval';

export default defineConfig({
  mexcApi: {
    input: {
      target: 'http://localhost:8000/openapi.json',
    },
    output: {
      target: './src/api/endpoints',
      schemas: './src/api/model',
      client: 'vue-query',
      httpClient: 'fetch',
      mode: 'tags-split',
      clean: true,
      prettier: true,
    },
  },
});
```

```vue
<!-- Использование в компоненте -->
<script setup lang="ts">
import { useGetAdvertisements } from '@/api/endpoints/advertisements';

const { data, isLoading, error } = useGetAdvertisements({
  pair: 'RUB_USDT',
  minRating: 4.0,
});
</script>
```

### Правило F5: Запрещённые библиотеки и подходы

- НЕ используй Options API — только Composition API с `<script setup>`
- НЕ используй `var` — только `const` и `let`
- НЕ используй Vuetify, Bootstrap, Tailwind — только Quasar UI-компоненты
- НЕ используй axios напрямую — используй Orval-сгенерированный клиент (fetch-based)
- НЕ используй moment.js — используй `date-fns` или нативный `Intl.DateTimeFormat`
- НЕ редактируй файлы в `src/api/` вручную — они генерируются Orval

### Правило F6: Quasar-компоненты

При работе с Quasar используй скилл `#quasar-skilld`. Ключевые моменты:
- `QTable` — prop `rows` (не `data`), используй `table-row-class-fn` для стилизации строк по риск-скору
- `useQuasar()` composable для доступа к `$q` (Notify, Dialog, Loading)
- Валидация форм через Regle (рекомендация Quasar)
- `model-value` + `@update:model-value` вместо `v-model` для кастомных компонентов

### Правило F7: Форматирование — Prettier

- Ширина строки: 100 символов
- Отступы: 2 пробела
- Точка с запятой: да
- Одинарные кавычки
- Trailing comma: all

## GoF-паттерны на фронтенде

- **Observer** — реактивность Vue (watchers, computed) уже реализует этот паттерн; Pinia stores для глобального состояния
- **Strategy** — composables как стратегии сортировки/фильтрации (`useSortByProfitability`, `useSortByRisk`)
- **Facade** — composable `useAdvertisements()` объединяет загрузку данных, фильтрацию, сортировку и пагинацию в единый интерфейс для страницы
- **Decorator** — HOC или composables для добавления поведения (например, `withAuth` guard)

## Тесты фронтенда

- Фреймворк: Vitest + Vue Test Utils
- Структура: `__tests__/` рядом с компонентами или `*.test.ts` рядом с файлом
- Моки API: MSW (Mock Service Worker) — Orval может генерировать MSW-хендлеры
- Один компонент — один тест-файл
