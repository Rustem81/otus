---
inclusion: fileMatch
fileMatchPattern: "src/components/**,src/pages/**"
---

# Правила shadcn/ui + Tailwind CSS

## S1: Использование shadcn/ui компонентов

Всегда предпочитай shadcn/ui компоненты вместо кастомных:

| Задача | Компонент |
|---|---|
| Карточка | `Card`, `CardHeader`, `CardContent`, `CardFooter` |
| Кнопка | `Button` с variants: `default`, `outline`, `ghost`, `destructive` |
| Модальное окно | `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle` |
| Выпадающий список | `Select`, `SelectTrigger`, `SelectContent`, `SelectItem` |
| Табы | `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent` |
| Бейдж | `Badge` с variants: `default`, `secondary`, `outline`, `destructive` |
| Ввод текста | `Input` с `Label` |
| Чекбокс | `Checkbox` |
| Переключатель | `Switch` |
| Тултип | `Tooltip`, `TooltipTrigger`, `TooltipContent` |
| Разделитель | `Separator` |
| Боковая панель | `Sheet` (мобильное меню) |

## S2: Импорт shadcn/ui

```tsx
// Правильно — из @/components/ui/
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
```

## S3: Tailwind dark theme

Проект использует class-based dark mode (класс `.dark` на корневом элементе).

```tsx
// Цвета через CSS-переменные:
className="bg-background text-foreground"     // основной фон/текст
className="bg-card text-card-foreground"       // карточки
className="bg-muted text-muted-foreground"     // приглушённый
className="text-primary"                        // акцентный цвет
className="text-destructive"                    // ошибки/удаление
```

## S4: Адаптивная сетка

```tsx
// Карточки: 1 колонка mobile, 2 tablet, 3 desktop
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">

// Два столбца на desktop
<div className="grid grid-cols-1 gap-4 md:grid-cols-2">

// Статистика: 2 mobile, 4 desktop
<div className="grid grid-cols-2 gap-3 md:grid-cols-4">
```

## S5: Цветовая индикация

| Значение | Цвет Tailwind |
|---|---|
| Покупка (BUY) / Позитив / Низкий риск | `text-green-400`, `bg-green-500/20` |
| Продажа (SELL) / Негатив / Высокий риск | `text-red-400`, `bg-red-500/20` |
| Средний риск / Предупреждение | `text-yellow-400`, `bg-yellow-500/20` |
| Акцент / Primary | `text-primary` (cyan в dark theme) |
| Приглушённый текст | `text-muted-foreground` |

## S6: Иконки — Lucide React

```tsx
import { RefreshCw, ExternalLink, Ban, Star, Clock } from "lucide-react";

// Размеры: h-3 w-3 (мелкие), h-4 w-4 (стандарт), h-5 w-5 (средние), h-12 w-12 (большие/empty state)
<RefreshCw className="h-4 w-4" />
```
