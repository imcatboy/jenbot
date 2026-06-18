# domain — бизнес-логика

Общий **domain layer** для бота и API. Не зависит от aiogram, FastAPI и React — только Python, SQLAlchemy, Redis, Pydantic.

## Назначение

- Единый источник бизнес-правил для всех клиентов
- Модели БД, entities, DTO, schemas
- Repositories (доступ к данным)
- Services (бизнес-операции)
- Cache (Redis)
- Domain exceptions

## Структура

```
domain/
├── uow.py                    # SQLAlchemyUnitOfWork
├── objects/
│   ├── types.py              # Enums, validators (UsernameOrTelegramID…)
│   ├── exceptions.py         # 26 domain exceptions
│   ├── entities/             # Dataclass-like domain objects
│   ├── models/               # SQLAlchemy ORM models
│   ├── dtos/                 # Data Transfer Objects (service input)
│   └── schemas/              # Pydantic API request/response schemas
├── repositories/             # Data access layer
├── services/                 # Business logic
├── cache/                    # Redis caching
└── mappers/                  # Entity ↔ schema mappers
```

## Слои данных

```
Handler / Endpoint
       ↓  DTO
   Service  ← business rules, orchestration
       ↓
  Repository
       ↓
  ORM Model  →  PostgreSQL
       ↓
   Entity  →  returned to caller
```

### Entities vs Models


|             | Entity                              | Model                        |
| ----------- | ----------------------------------- | ---------------------------- |
| Назначение  | Объект домена для services/handlers | SQLAlchemy ORM, таблицы БД   |
| Зависимости | Чистый Python                       | SQLAlchemy                   |
| Пример      | `entities.ReputationUserEntity`     | `models.ReputationUserModel` |


Repositories загружают models и возвращают entities.

### DTO vs Schema


|               | DTO                       | Schema                            |
| ------------- | ------------------------- | --------------------------------- |
| Использование | Внутри domain/services    | На границе API (request/response) |
| Пример        | `CreateReputationUserDTO` | `CreateReputationUserRequest`     |


## Services


| Service              | Ответственность                                       |
| -------------------- | ----------------------------------------------------- |
| `UserService`        | Пользователи, reputation users, usernames, auth cache |
| `ModerationService`  | Violations, chat violations, reports, trackers        |
| `TradingService`     | Deals, external deals, reviews, scam reports          |
| `MarketplaceService` | Advertisements, options, filters, suggestions         |
| `ProductService`     | Products, categories                                  |
| `MessagingService`   | Chats, messages                                       |
| `MediaService`       | File storage, media cache                             |
| `ConfigService`      | Key-value config (subscriptions, settings)            |


## Repositories

Наследуют `BaseRepository` (~450 строк общих CRUD-паттернов):

- `get`, `get_many`, `create`, `update`, `delete`
- фильтрация через DTO
- eager loading relationships

Специализированные: `UserRepository`, `ModerationRepository`, `TradingRepository`, `MarketplaceRepository`, и др.

## ORM Models — ключевые таблицы

### User & Reputation (`models/user.py`)

- `users` — telegram_id, role, связь с reputation_user
- `reputation_users` — role (guarantor, scammer…), name, version
- `usernames` — история @username
- `user_details` — произвольные поля карточки
- `reputation_user_users` — связь many-to-many аккаунтов

### Moderation (`models/moderation.py`)

- `violations`, `chat_violations` — warn/mute/ban
- `reports` — жалобы с attachments (ARRAY)
- `trackers` — partial unique index на active trackers
- `reputation_requests`, `telegram_files`

### Trading (`models/trading.py`)

- `deals` — money/trade с check constraints на тип сделки
- `external_deals` — сделки с гарантом (seller, buyer, agent)
- `scam_reports`, `reviews`

### Marketplace (`models/marketplace.py`)

- `products`, `categories`, `advertisements`, `advertisement_options`
- `advertisement_option_trades`, drafts

## Domain Exceptions (примеры)

```python
DealSelfPurchaseException      # нельзя купить своё объявление
NotEnoughInventoryException    # недостаточно товара
TooManyObjectsFoundException   # max 3 pending deals
UserIsNotGuarantorException    # пользователь не является гарантом
UserIsScammerException         # scammer не может участвовать в сделке
ModerationException            # бот не может применить violation
```

Исключения содержат structured data (`object_ids`, `**data`) для логирования и API responses.

## Cache (`domain/cache/`)


| Cache             | Назначение                  |
| ----------------- | --------------------------- |
| `UserCache`       | Auth sessions, user lookups |
| `ModerationCache` | Trackers TTL 24h            |
| `MediaCache`      | File metadata               |


Ключи централизованы в `cache/keys.py`.

## Unit of Work

```python
async with SQLAlchemyUnitOfWork(session_factory) as uow:
    service = UserService(user_repository=UserRepository(uow.session), ...)
    await service.do_something()
    # commit on success, rollback on exception
```

Используется в:

- `bot/middlewares/uow.py` — на каждый Telegram update
- `api/dependencies/uow.py` — на каждый HTTP request
- `bot/loops/` — в фоновых задачах

## Types & Validation (`objects/types.py`)

- `ViolationType`, `UserRole`, `UserReputationRole`
- `DealStatus`, `DealType`, `DealCondition`
- `ReportType`, `ReportStatus`
- Custom Pydantic validators: `UsernameOrTelegramID`, `SettingName`, `SettingValue`

## Примеры бизнес-правил

**Лимит pending-сделок** (`TradingService.buy_advertisement_option`):

```python
if len(deals) >= 3:
    raise TooManyObjectsFoundException("Deal", user_id=..., status=PENDING)
```

**Выбор гаранта** (`TradingService.start_external_deal`):

- Явный `agent_id` → проверка роли guarantor
- Иначе → guarantor из seller/buyer по роли (SMALL_GUARANTOR, GUARANTOR, BIG_GUARANTOR, DEPOSITOR)
- Scammer блокирует старт сделки

**Partial unique index** (`TrackerModel`):

```sql
UNIQUE (tracked_user_id, tracking_user_id) WHERE is_active = TRUE
```

## Использование из других модулей

```python
# bot/middlewares/dependencies.py
user_service = UserService(
    user_repository=UserRepository(session=uow.session),
    user_cache=UserCache(redis=redis),
    media_repository=MediaRepository(session=uow.session),
)

# api/dependencies/uow.py — аналогично через Depends
```

Domain **не импортирует** bot или api — зависимость однонаправленная.