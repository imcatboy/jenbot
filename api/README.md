# api — REST API

**FastAPI**-приложение — backend для Telegram Mini Apps и потенциальных внешних клиентов. Разделяет domain-слой с ботом; авторизация через **Telegram Web App initData**.

## Назначение

- CRUD репутационных карточек (для Mini App модерации)
- Управление пользователями, отзывами, scam reports
- Маркетплейс: объявления, продукты, категории, фильтры
- Сделки
- Messaging и загрузка медиа

## Структура

```
api/
├── main.py                 # FastAPI app, CORS, exception handlers, Sentry
├── core/
│   ├── settings.py         # PROJECT_HOST, PROJECT_PORT, media paths, CORS
│   ├── container.py        # dependency-injector: engine, session_factory, redis
│   └── openapi.py          # Метаданные OpenAPI (tags, summaries, responses)
├── dependencies/
│   ├── auth.py             # Telegram initData validation, Authorize(role)
│   ├── uow.py              # UoW + service factories для endpoints
│   └── media.py            # Upload validation (avatar, product, message files)
└── endpoints/
    ├── exceptions.py       # Domain exception → HTTP response mappers
    └── v1/
        ├── user.py
        ├── reputation.py
        ├── product.py
        ├── marketplace.py
        ├── trading.py
        └── messaging.py
```

## API v1 — роутеры


| Prefix            | Tag         | Основные операции                       |
| ----------------- | ----------- | --------------------------------------- |
| `/v1/users`       | User        | get_me, create/update user, reviews     |
| `/v1/reputation`  | Reputation  | CRUD reputation cards (moderator/admin) |
| `/v1/products`    | Product     | products, categories                    |
| `/v1/marketplace` | Marketplace | advertisements, filters, suggestions    |
| `/v1/trading`     | Trading     | deals, external deals, scam reports     |
| `/v1/messaging`   | Messaging   | chats, messages, files                  |


Документация: `/docs` (Swagger), `/redoc`.

## Авторизация

### Telegram initData

Mini Apps передают `X-Telegram-Init-Data` header (или `?init_data=` query).

`validate_init_data()`:

1. Парсит query string из initData
2. Проверяет HMAC-SHA256 подпись через bot token
3. Проверяет `auth_date` (max age 3600s по умолчанию)
4. Извлекает `TelegramUserRaw`

`get_current_user` → `user_service.get_or_create(telegram_id, usernames)`.

`get_current_user_cached` — кэширует результат auth в Redis по hash initData.

### Role-based access

```python
user: entities.UserEntity = Depends(Authorize([UserRole.ADMIN, UserRole.MODERATOR]))
```

Роли: `admin`, `moderator`, `user` (`domain.objects.types.UserRole`).

## Exception handling

26 доменных исключений из `domain.objects.exceptions` маппятся в HTTP:


| Exception                      | HTTP |
| ------------------------------ | ---- |
| `ObjectNotFoundException`      | 404  |
| `ObjectAlreadyExistsException` | 409  |
| `TooManyObjectsFoundException` | 409  |
| `NotEnoughInventoryException`  | 400  |
| `DealSelfPurchaseException`    | 400  |
| `UserIsNotGuarantorException`  | 403  |
| `InvalidDataException`         | 422  |
| …                              | …    |


Единый формат ответа через Pydantic schemas (`domain.objects.schemas`).

## Dependency Injection

`dependency-injector` (`AppContainer`):

- `Settings` — singleton
- `engine` — async SQLAlchemy engine (pool_size=3)
- `session_factory` — async_sessionmaker
- `redis` — Redis client

Endpoints получают сервисы через `Depends(get_*_service)` из `dependencies/uow.py` — каждый request создаёт UoW и сервисы в scope запроса.

## Медиа

Upload endpoints валидируют:

- расширения файлов (`ALLOWED_*_EXTENSIONS`)
- максимальный размер (`*_MAX_SIZE`)
- resize через Pillow (`AVATAR_SIZE`, `PRODUCT_IMAGE_SIZE`)

Файлы сохраняются в `media/avatars`, `media/products`, `media/messages`.

## Мониторинг

Sentry SDK инициализируется в `main.py` через `SENTRY_DSN`.

## Запуск

```bash
export PYTHONPATH=.
python -m api.main
# uvicorn на PROJECT_HOST:PROJECT_PORT (по умолчанию 127.0.0.1:4000)
```

Docker:

```bash
docker compose up -d api
```

За nginx API проксируется на внутренний порт.

## Связь с frontend

```
web/base, web/marketplace
    → axios + X-Telegram-Init-Data
    → api/endpoints/v1/*
    → domain/services
```

Frontend не обращается к боту напрямую — только через REST API.