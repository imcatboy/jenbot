# web/base — Mini App модерации

Telegram **Mini App** для заполнения репутационных карточек модераторами. Заменяет длинные цепочки inline-кнопок в боте на полноценный UI с формами.

**Статус: Production** — используется командой модерации.

## Назначение

- Поиск и просмотр карточек репутации
- Создание / редактирование карточек (роли, детали, связанные аккаунты)
- Привязка scam reports к карточкам
- Draft-режим: изменения накапливаются локально, сохраняются одной кнопкой

## Стек

| | |
|---|---|
| Framework | React 19 + TypeScript |
| Build | Vite 8 |
| State | Zustand (UI + draft) |
| Data fetching | TanStack React Query |
| HTTP | Axios |
| Styling | SCSS Modules |
| Telegram | `@twa-dev/sdk`, `@types/telegram-web-app` |

## Структура

```
web/base/src/
├── main.tsx                 # Telegram WebApp init, QueryClient
├── App.tsx                  # View router
├── features/
│   ├── MainSearch/          # Главный экран — поиск карточек
│   ├── ReputationCard/      # Редактор карточки (основной экран)
│   ├── UserSearch/          # Поиск пользователей для привязки
│   ├── UserCreate/          # Создание связанного пользователя
│   └── DetailCreate/        # Добавление detail-поля
├── shared/
│   ├── components/
│   │   ├── AccessGate/      # Telegram-only + staff-only guard
│   │   ├── MainButtonController/  # Telegram MainButton API
│   │   ├── BackButtonController/  # Telegram BackButton API
│   │   └── ErrorAlert/
│   └── ui/                  # TextField, Select, AreaField, LinkedUser…
├── stores/ui.ts             # View state, draft, MainButton config
├── hooks/                   # useMyUser, useReputationUser, mutations
├── api/                     # client, services, schemas
└── utils/                   # draft transforms, telegram helpers
```

## Views (навигация)

Zustand `view` переключает экраны без react-router:

| View | Компонент | Описание |
|------|-----------|----------|
| `home` | MainSearch | Поиск по базе |
| `card` | ReputationCard | Редактор карточки |
| `userSearch` | UserSearch | Привязка Telegram-пользователя |
| `createUser` | UserCreate | Создание user в карточке |
| `createDetail` | DetailCreate | Новое detail-поле |

`MainButtonController` и `BackButtonController` синхронизируют нативные кнопки Telegram с Zustand config.

## AccessGate

Двухуровневая защита:

1. **Telegram WebApp only** — приложение не работает в обычном браузере
2. **Staff only** — `user.role` must be `admin` or `moderator`

```tsx
if (isError || !user || !isStaffRole(user.role)) {
  return <AccessDenied title="Пока сюда нельзя" ... />;
}
```

## Draft-паттерн

`ReputationCard` не сохраняет каждое поле на сервер. Вместо этого:

1. `initDraft(reputationUser)` — загрузка в локальный draft
2. `updateDraft({ ... })` — изменения в Zustand
3. `isDirty` — флаг несохранённых изменений
4. MainButton «Сохранить» → `draftToCreateRequest` / `draftToUpdateRequest` → API

Преимущества:
- Меньше запросов к API
- UX как в desktop-редакторе
- Откат через `clearDraft`

## API интеграция

`api/client.ts` — axios instance с:

```typescript
headers: { "X-Telegram-Init-Data": WebApp.initData }
```

Сервисы:
- `user.ts` — get_me, create/update user
- `reputation.ts` — CRUD reputation cards
- `trading.ts` — scam reports для карточек

Schemas типизированы в `api/schemas/` — зеркало Pydantic schemas backend.

## Hooks

| Hook | Назначение |
|------|------------|
| `useMyUser` | Текущий пользователь (auth) |
| `useReputationUser` | Загрузка карточки по ID |
| `useCreateReputationUser` | Mutation create |
| `useUpdateReputationUser` | Mutation update |
| `useAlertError` | Global error → Zustand error state |
| `useDebounce` | Debounce для поиска |

## UI Kit

Переиспользуемые компоненты в `shared/ui/`:

- `TextField`, `AreaField`, `TextFieldList`
- `Select`, `Dropdown`, `Checkbox`
- `ReadableField` — read-only с edit action
- `LinkedUser` — карточка привязанного аккаунта
- `ReportCard` / `ReportCardAdd` — scam reports
- `Detail` — detail-поле карточки
- `Search`, `UserCard`, `Sceleton`

SCSS Modules + CSS variables (`styles/_vars.scss`).

## Запуск

```bash
cd web/base
npm install
npm run dev
```

Сборка:

```bash
npm run build
# dist/ → nginx (см. docker-compose.yml)
```

Для локальной разработки Mini App нужен HTTPS tunnel (ngrok / Cloudflare Tunnel) или Telegram test environment.

## Production

Статика `web/base/dist` монтируется в nginx контейнер. API проксируется на `api` service. SSL через certbot.

## Связь с backend

```
ReputationCard (React)
    → POST/PUT /v1/reputation
    → api/dependencies/auth.py (initData)
    → UserService.create_reputation_user / update_reputation_user
    → domain/repositories/user.py
    → PostgreSQL
```

Бот не участвует в этом flow — Mini App работает только через REST API.
