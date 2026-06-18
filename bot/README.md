# bot — Telegram-бот

Telegram-бот на **aiogram 3** — основной пользовательский интерфейс платформы JenBot. Работает через long polling, использует общий `domain/`-слой и развёрнут в production.

## Назначение

- Проверка репутации пользователей (`/check`, `/me`)
- Модерация в групповых чатах (warn, mute, ban)
- Подача жалоб (`/report`, `/scam`)
- Отзывы и scam reports
- Административные команды
- Проверка подписки на каналы экосистемы
- Фоновая актуализация истёкших нарушений

## Структура

```
bot/
├── main.py              # Точка входа, wiring middleware и routers
├── core/
│   ├── settings.py      # Pydantic Settings (BOT_TOKEN, DATABASE_URL, PROXY…)
│   └── protocol.py      # Протоколы для actions
├── handlers/            # Роутеры по доменам
│   ├── moderation.py    # Модерация в чатах (~550 строк)
│   ├── reputation.py    # Репутация, отзывы, scam reports
│   ├── report.py        # Жалобы пользователей
│   ├── admin.py         # Админ-команды
│   ├── user.py          # Базовые user handlers
│   ├── event.py         # join/leave/ban_word события
│   ├── exceptions.py    # Обработка domain exceptions
│   └── trading.py       # External deals (написан, не подключён к dispatcher)
├── middlewares/         # Цепочка middleware (см. ниже)
├── actions/             # Высокоуровневые действия (user, moderation, media, audit)
├── loops/               # Scheduler: actualize_violations_loop
├── filters/             # groups, users
└── data/                # keyboards, text, callbacks, states
```

## Middleware (порядок выполнения)

| Middleware | Уровень | Назначение |
|------------|---------|------------|
| `ThrottlingMiddleware` | outer | Rate limit 1 req/s на message и callback |
| `UOWMiddleware` | outer | Unit of Work — сессия SQLAlchemy на update |
| `DIMiddleware` | outer | Сборка repositories + services в `data` |
| `AlbumMiddleware` | outer | Группировка media album (latency 0.5s) |
| `UserMiddleware` | outer | Резолв `UserEntity` из Telegram |
| `WordsMiddleware` | outer | Фильтр запрещённых слов |
| `TrackerMiddleware` | outer | Трекинг пользователей модераторами |
| `SubscriptionsMiddleware` | inner | Проверка подписки (flag `subscriptions: True`) |
| `RoleMiddleware` | inner | Проверка роли пользователя |
| `CommandValidationMiddleware` | inner | Валидация команд |
| `StateMiddleware` | inner | FSM state handling |
| `MediaCheckMiddleware` | inner | Проверка медиа-вложений |

Флаг `subscriptions: True` на handler включает проверку каналов из `ConfigService.get("subscriptions")`. Список каналов настраивается в БД без изменения кода.

## Handlers в production

Подключены в `handler_routers`:

```python
handler_routers = [
    moderation_router,
    reputation_router,
    exception_router,
    report_router,
    event_router,
    admin_router,
    user_router,
]
```

`trading_router` реализован в `handlers/trading.py`, но **намеренно не подключён** — external deals в стадии доработки перед релизом.

## Dependency Injection

`DIMiddleware` создаёт на каждый update:

- `ConfigService`, `UserService`, `MediaService`
- `ModerationService`, `TradingService`, `MarketplaceService`
- `MessagingService`, `ProductService`
- `UserActions`, `ModerationActions`, `MediaActions`, `AuditActions`

Handlers получают сервисы через `data[...]` — без глобального состояния.

## FSM и Redis

- FSM storage: `RedisStorage` — состояния переживают рестарт бота
- Redis также используется domain cache (auth, users, moderation)

## Scheduler

`SchedulerService` запускает фоновую задачу `actualize_violations_loop`:

- каждые 60 секунд проверяет истёкшие chat violations
- снимает mute/ban в Telegram через Bot API
- обновляет статус в БД

## Команды бота

| Команда | Описание |
|---------|----------|
| `/help` | Справка |
| `/check` | Репутация пользователя |
| `/me` | Своя репутация |
| `/report` | Жалоба в чате |
| `/review` | Отзыв о пользователе |
| `/scam` | Жалоба на скамера |

## Запуск

```bash
# Из корня репозитория
export PYTHONPATH=.
python -m bot.main
```

Docker:

```bash
docker compose up -d bot
```

## Обработка ошибок

`handlers/exceptions.py` перехватывает `domain.objects.exceptions.*` и переводит их в понятные сообщения пользователю. Domain layer не знает про Telegram — маппинг только на уровне bot.

## Связь с другими модулями

```
bot/handlers  →  domain/services  →  domain/repositories  →  PostgreSQL
                      ↓
                 domain/cache  →  Redis
```

Mini App модерации (`web/base`) использует тот же domain через `api/`, а не через бота.
