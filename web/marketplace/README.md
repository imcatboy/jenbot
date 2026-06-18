# web/marketplace — Mini App маркетплейса

Telegram **Mini App** для просмотра каталога объявлений маркетплейса. Backend (domain + API) готов; frontend — **MVP в разработке**.

**Статус: В разработке** — каталог, поиск и фильтры работают; checkout и полный user flow — в планах.

## Назначение

- Каталог объявлений с карточками
- Поиск и фильтрация
- TabBar навигация (задел под профиль, сообщения, создание объявления)
- Интеграция с Telegram MainButton / BackButton

## Стек

| | |
|---|---|
| Framework | React 19 + TypeScript |
| Build | Vite 8 |
| State | Zustand (UI + catalog filters) |
| Data fetching | TanStack React Query |
| HTTP | Axios |
| Styling | SCSS Modules |
| Telegram | `@twa-dev/sdk` |

## Структура

```
web/marketplace/src/
├── App.tsx                  # Layout: Header + TabBar + view router
├── features/
│   ├── Catalog/             # Список объявлений
│   ├── CatalogSearch/       # Поиск
│   └── CatalogFilters/      # Фильтры
├── shared/
│   ├── components/
│   │   ├── Header/          # Dynamic header (search, buttons)
│   │   ├── TabBar/          # Bottom navigation
│   │   ├── MainButtonController/
│   │   ├── BackButtonController/
│   │   └── MainButtonMock/  # Dev mock для MainButton вне Telegram
│   └── ui/
│       ├── AdCard/          # Карточка объявления
│       ├── Option/          # Вариант товара
│       ├── Search/, Button/, Tab/, Image/, Sceleton/
├── stores/
│   ├── ui.ts                # view, subView, headerConfig
│   └── catalog.ts           # activeFilters
├── hooks/
│   └── useMarketplace.ts    # React Query wrapper
└── api/
    ├── client.ts
    ├── services/marketplace.ts
    └── schemas/marketplace.ts
```

## Навигация

```
view: "catalog"
  subView: undefined  →  Catalog
  subView: "search"   →  CatalogSearch
  subView: "filters"  →  CatalogFilters
```

`Header` конфигурируется динамически через `setHeaderConfig`:

```typescript
setHeaderConfig({
  search: { placeholder: "Найти объявление...", onFocus: () => setSubView("search") },
  rightButton: { icon: <FiltersIcon />, onClick: () => setSubView("filters") },
});
```

## Catalog Store

`catalog.ts` — Zustand store для фильтров:

- категории, продукты, продавцы
- сортировка (`SortType`: popularity, new, old)
- передаётся в `useMarketplace(activeFilters)` → `GET /v1/marketplace/advertisements`

## API интеграция

```typescript
// api/services/marketplace.ts
getAdvertisements(filters) → GET /v1/marketplace/advertisements
getAdvertisementFilters()  → GET /v1/marketplace/advertisements/filters
getSuggestions(query)      → GET /v1/marketplace/advertisements/suggestions
```

Auth — тот же `X-Telegram-Init-Data`, что и в `web/base`.

Backend endpoints реализованы в `api/endpoints/v1/marketplace.py`, business logic — `domain/services/marketplace.py` + `domain/repositories/marketplace.py` (~600 строк).

## Что готово / что в планах

| Функция | Статус |
|---------|--------|
| Каталог объявлений | ✅ |
| Поиск | ✅ |
| Фильтры | ✅ (базовые) |
| AdCard UI | ✅ |
| TabBar (навигация) | ✅ UI, частично wired |
| Создание объявления | 🔲 |
| Покупка / сделки | 🔲 (domain готов, UI нет) |
| Профиль / сообщения | 🔲 |

## Запуск

```bash
cd web/marketplace
npm install
npm run dev
# vite --host для доступа из Telegram WebApp preview
```

Сборка:

```bash
npm run build
```

## Dev notes

- `MainButtonMock` — заглушка MainButton для разработки вне Telegram
- `vite --host --dangerously-disable-host-check` в dev script — для tunnel-доступа

## Связь с domain

Marketplace domain включает:

- `ProductModel`, `CategoryModel`, `AdvertisementModel`, `AdvertisementOptionModel`
- Draft status для объявлений
- Option trades (barter)
- Authors на products/categories

Frontend использует subset API; полный trading flow (`domain/services/trading.py`) будет подключён на следующем этапе.

## Отличие от web/base

| | web/base | web/marketplace |
|---|----------|-----------------|
| Аудитория | Модераторы (staff) | Все пользователи |
| AccessGate | Staff-only | Нет (планируется auth) |
| Сложность UI | Draft-редактор форм | Каталог + filters |
| Production | ✅ | 🔲 MVP |

Оба приложения — независимые Vite-проекты с общим API backend.
