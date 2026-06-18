# web — Telegram Mini Apps

Frontend-приложения платформы JenBot. Каждое — **отдельный Vite + React** проект с собственным `package.json`, деплоится как статика через nginx.

## Проекты

| Проект | Путь | Статус | README |
|--------|------|--------|--------|
| Reputation (модерация) | [base/](base/) | Production | [base/README.md](base/README.md) |
| Marketplace (каталог) | [marketplace/](marketplace/) | MVP | [marketplace/README.md](marketplace/README.md) |

## Общие принципы

- **React 19 + TypeScript + Vite 8**
- **Zustand** для UI state, **TanStack Query** для server state
- **SCSS Modules** + shared design tokens (`_vars.scss`, `_animations.scss`)
- Авторизация через **Telegram Web App initData** → header `X-Telegram-Init-Data` → `api/`
- Нативные **MainButton** и **BackButton** Telegram синхронизируются через controller-компоненты

## API

Оба приложения обращаются к одному backend:

```
https://<domain>/v1/...
```

Локально API: `http://127.0.0.1:4000/v1/...` (см. `api/core/settings.py`).

## Разработка Mini App

Telegram Mini Apps требуют HTTPS. Варианты для local dev:

1. **ngrok / Cloudflare Tunnel** → proxy на `vite dev` port
2. Telegram **Web App test environment** (BotFather)
3. Сборка + deploy на staging server

`web/marketplace` использует `vite --host` для доступа по LAN/tunnel.

## Сборка и деплой

```bash
cd web/base && npm run build        # → web/base/dist/
cd web/marketplace && npm run build # → web/marketplace/dist/
```

В production `docker-compose.yml` монтирует `web/base/dist` в nginx. Marketplace dist подключается аналогично при необходимости.

## Структура типичного feature

```
features/SomeFeature/
├── SomeFeature.tsx
├── SomeFeature.module.scss
├── SomeFeature.config.tsx   # optional constants
└── index.ts
```

Shared UI — в `shared/ui/`, переиспользуется между features внутри одного app (не между base и marketplace).
