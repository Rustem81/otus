# Библиотека промпт-шаблонов

Шаблоны привязаны к проекту MEXC P2P Агрегатор и используют скиллы Kiro: `#fastapi-templates`, `#gof-design-patterns`, `#orval`, `#quasar-skilld`.

Каждый шаблон использует структуру RTCF (Role — Task — Context — Format).

---

## 1. Генерация компонента/функции по описанию

### Шаблон

```
Role: Senior {backend/frontend} Developer. Используй скилл {#fastapi-templates / #quasar-skilld}.

Task: Создай {компонент / эндпоинт / сервис / composable} для {описание функциональности}.

Context:
- Стек: {Vue.js 3 + Quasar + TypeScript / Python + FastAPI + SQLAlchemy}
- Связанные модели/типы: {перечислить}
- Бизнес-логика: {описать правила}
- Зависимости: {какие сервисы/репозитории использует}

Format:
- Один файл с полной реализацией
- Типизация на всех входах/выходах
- Комментарии JSDoc/docstring для публичных методов
- Следуй правилам из steering-файлов проекта
```

### Пример использования

```
Role: Senior Backend Developer. Используй скилл #fastapi-templates.

Task: Создай эндпоинт GET /api/v1/advertisements для получения списка P2P-объявлений
с фильтрацией и сортировкой.

Context:
- Стек: Python + FastAPI + SQLAlchemy 2 async
- Модель: Advertisement (id, price, volume, min_limit, max_limit, direction, currency,
  payment_methods, is_active, risk_score, merchant_id)
- Фильтры: currency_pair (обязательный), payment_methods (список), min_rating (float),
  min_trades (int), amount_range (min, max)
- Сортировка: по integral_score (дефолт), profitability, rating, volume, risk_score
- Пагинация: skip/limit
- Зависимости: AdvertisementRepository, ScoringService

Format:
- Файл endpoints/advertisements.py
- Pydantic v2 схемы для query params и response
- Async handler с Depends() для DB-сессии
- Валидация через Pydantic, обработка ошибок через AppException
```

---

## 2. Рефакторинг кода с улучшением

### Шаблон

```
Role: Senior Developer, специалист по рефакторингу и GoF-паттернам.
Используй скилл #gof-design-patterns для выбора паттерна.

Task: Отрефакторить {модуль/функцию/класс}. Проблемы: {перечислить конкретные проблемы}.

Context:
- Текущий код: {вставить код или указать файл}
- Что не так: {захардкоженные значения / дублирование / нарушение SRP / отсутствие типов / ...}
- Ограничения: {что нельзя менять — публичный API, совместимость, ...}
- Стек: {Python + FastAPI / Vue + TypeScript}

Format:
- Рефакторенный код
- Список изменений (что было → что стало)
- Какой GoF-паттерн применён и почему
- Если паттерн не нужен — объяснить почему простое решение лучше
```

### Пример использования

```
Role: Senior Backend Developer, специалист по рефакторингу.
Используй скилл #gof-design-patterns.

Task: Отрефакторить функцию calculate_risk_score(). Проблемы:
- Веса факторов захардкожены в теле функции
- Нет обработки случая когда closing_speed отсутствует
- Нет логирования промежуточных результатов
- Невозможно подменить алгоритм скоринга без изменения кода

Context:
- Текущий код: backend/app/services/scoring.py
- Функция принимает MerchantMetrics, возвращает int (1-10)
- Веса должны браться из конфига (pydantic-settings)
- При отсутствии closing_speed — перераспределить веса пропорционально
- В будущем будет LLM-enhanced скоринг (v1.1)

Format:
- Рефакторенный код с паттерном Strategy (интерфейс ScoringStrategy,
  реализация RuleBasedScoring)
- Список изменений
- Объяснение почему Strategy, а не просто параметризация
```

---

## 3. Написание тестов для существующего кода

### Шаблон

```
Role: QA Engineer с опытом в {pytest / Vitest} тестировании.

Task: Написать {unit / integration} тесты для {модуль/компонент/эндпоинт}.

Context:
- Код для тестирования: {вставить или указать файл}
- Стек тестов: {pytest + pytest-asyncio + httpx / Vitest + Vue Test Utils}
- Внешние зависимости для мокирования: {БД, Redis, MEXC API, OpenAI, ...}
- Критические сценарии: {перечислить edge cases}

Format:
- Файл {*.test.ts / test_*.py}
- Группировка по describe/class (happy path, edge cases, error handling)
- Минимум 3 теста на каждый блок
- Моки внешних зависимостей через {AsyncMock / vi.mock}
- Фикстуры/setup для переиспользования
```

### Пример использования

```
Role: QA Engineer с опытом в pytest.

Task: Написать unit-тесты для AdvertisementRepository: методы get_active_by_pair,
get_filtered, mark_inactive.

Context:
- Код: backend/app/repositories/advertisement_repository.py
- Стек: pytest + pytest-asyncio, AsyncSession мокается через фикстуру
- Зависимости: AsyncSession (SQLAlchemy)
- Критические сценарии:
  - Пустой результат (нет объявлений по паре)
  - Фильтрация по нескольким payment_methods одновременно
  - mark_inactive для уже неактивного объявления
  - Объявление с отсутствующими метриками мерчанта

Format:
- Файл test_advertisement_repository.py
- Группировка: class TestGetActivByPair, class TestGetFiltered, class TestMarkInactive
- Минимум 3 теста на метод
- AsyncMock для db.execute, db.flush
```

---

## 4. Исправление ошибок и багов

### Шаблон

```
Role: Senior Developer, специалист по отладке {async Python / Vue.js}.

Task: Исправить баг: {описание симптома}. Ожидаемое поведение: {что должно быть}.
Фактическое: {что происходит}.

Context:
- Код с багом: {вставить или указать файл}
- Стек: {Python + FastAPI + asyncio / Vue + Quasar + TypeScript}
- Шаги воспроизведения: {1, 2, 3...}
- Логи/ошибки: {вставить stack trace или сообщение}
- Что уже пробовали: {перечислить}

Format:
- Исправленный код
- Объяснение причины бага (root cause)
- Описание решения и почему именно такое
- Рекомендация как предотвратить подобное в будущем (тест, линт-правило, типизация)
```

### Пример использования

```
Role: Senior Backend Developer, специалист по async Python.

Task: Исправить race condition в polling-сервисе. Ожидаемое: один цикл поллинга
за раз. Фактическое: при задержке ответа MEXC API >10 сек запускается второй
параллельный цикл, что приводит к дублированию объявлений и превышению rate limit.

Context:
- Код: backend/app/tasks/polling.py
- Стек: Python + asyncio, Redis для хранения объявлений
- Поллинг через asyncio.create_task с интервалом 10 сек
- Redis используется для кэша объявлений
- Логи: "Duplicate external_id constraint violation" при высокой нагрузке

Format:
- Исправленный код с distributed lock через Redis (SETNX)
- Root cause: отсутствие mutex между циклами поллинга
- Почему Redis lock, а не локальная переменная (масштабирование на несколько воркеров)
- Тест для проверки что два параллельных вызова не конфликтуют
```

---

## 5. Декомпозиция сложной задачи на подзадачи

### Шаблон

```
Role: Tech Lead / Архитектор проекта.
Используй скилл #gof-design-patterns для выбора архитектурных решений.

Task: Декомпозировать задачу "{название}" на подзадачи для спринта
({длительность}, {количество разработчиков}).

Context:
- Описание задачи: {что нужно реализовать}
- Стек: {перечислить технологии}
- Зависимости: {какие модули/сервисы уже существуют}
- Ограничения: {дедлайн, ресурсы, технические ограничения}

Format:
- Пронумерованный список подзадач
- Для каждой: описание, оценка в часах, зависимости от других подзадач
- Definition of Done для каждой подзадачи
- Порядок выполнения (что можно параллелить)
- Рекомендуемые GoF-паттерны если уместно
```

### Пример использования

```
Role: Tech Lead. Используй скилл #gof-design-patterns.

Task: Декомпозировать задачу "Модуль риск-скоринга с LLM-объяснениями"
на подзадачи для спринта (2 недели, 1 разработчик).

Context:
- Что реализовать: rule-based скоринг (1-10) по метрикам мерчанта,
  LLM-объяснение (до 300 символов), кэширование в Redis (TTL 10 мин),
  fallback при недоступности LLM, API-эндпоинт для получения объяснения
- Стек: FastAPI, SQLAlchemy, Redis, OpenAI API
- Уже есть: модели Advertisement и Merchant, AdvertisementRepository,
  Redis-клиент, базовая структура проекта
- Ограничения: веса скоринга из конфига, не из UI

Format:
- Подзадачи с оценками в часах
- Зависимости между задачами
- DoD для каждой
- Какие GoF-паттерны применить (Strategy для скоринга, Decorator для LLM-обёртки)
```

---

## 6. Генерация API-клиента и интеграция фронт-бэк

### Шаблон

```
Role: Full-Stack Developer. Используй скилл #orval.

Task: Настроить {генерацию API-клиента / интеграцию нового эндпоинта} для
{описание функциональности}.

Context:
- Бэкенд: FastAPI, OpenAPI-схема доступна по {URL}
- Фронтенд: Vue.js 3 + Quasar + TypeScript
- Orval-конфиг: {текущий или нужно создать}
- Эндпоинты для генерации: {перечислить}

Format:
- Конфигурация orval.config.ts (если нужна)
- Пример использования сгенерированных хуков в Vue-компоненте
- Типы request/response
```

### Пример использования

```
Role: Full-Stack Developer. Используй скилл #orval.

Task: Настроить Orval для генерации vue-query хуков из OpenAPI-схемы
бэкенда MEXC P2P Агрегатора.

Context:
- Бэкенд: FastAPI на http://localhost:8000, схема по /openapi.json
- Фронтенд: Vue.js 3 + Quasar, уже установлен @tanstack/vue-query
- Нужны хуки для: GET /api/v1/advertisements, GET /api/v1/advertisements/{id},
  POST /api/v1/auth/login, GET /api/v1/profile
- Режим: tags-split (по тегам OpenAPI)

Format:
- orval.config.ts с клиентом vue-query и httpClient fetch
- Пример использования useGetAdvertisements() в компоненте DashboardPage.vue
- Команда для генерации: npx orval
```

---

## 7. Создание UI-компонента на Quasar

### Шаблон

```
Role: Senior Frontend Developer. Используй скилл #quasar-skilld.

Task: Создай Vue-компонент {название} для {описание функциональности}.

Context:
- Quasar-компоненты для использования: {QTable, QDialog, QCard, ...}
- Данные: {тип входных данных, откуда приходят}
- Интерактивность: {фильтры, сортировка, клики, модалки}
- Состояния UI: {загрузка, пустой результат, ошибка}

Format:
- Один .vue файл (SFC) с <script setup lang="ts">
- Типизация props и emits
- Использование Quasar-компонентов (не кастомных HTML-элементов)
- Обработка состояний загрузки/ошибки
```

### Пример использования

```
Role: Senior Frontend Developer. Используй скилл #quasar-skilld.

Task: Создай компонент AdvertisementTable — таблица P2P-объявлений с колонками:
мерчант, рейтинг, кол-во сделок, цена, спред, банки, лимиты, объём,
риск-скор (цветовая индикация), чистая доходность (tooltip с детализацией).

Context:
- Quasar: QTable (prop rows, не data), QBadge для риск-скора, QTooltip для доходности
- Данные: AdvertisementResponse[] из Orval-сгенерированного хука useGetAdvertisements()
- Сортировка по всем числовым колонкам, клик по строке — emit('select', ad)
- Состояния: QSpinner при загрузке, сообщение "Нет объявлений" при пустом списке

Format:
- AdvertisementTable.vue с <script setup lang="ts">
- Props: advertisements, loading, error
- Emits: select(advertisement)
- Цвета риск-скора: positive (1-3), warning (4-7), negative (8-10)
```
