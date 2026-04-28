import hmac
import hashlib
import json

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Header, HTTPException
from urllib.parse import parse_qsl, unquote
from datetime import datetime, timezone
from pydantic import BaseModel
from redis.asyncio import Redis

from api.core.container import AppContainer
from api.core.settings import Settings
from domain.objects import entities
from domain.services import UserService
from .uow import get_user_service


settings = Settings()


class TelegramUserRaw(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    is_premium: bool = False
    language_code: str | None = None


TEST_TELEGRAM_USER: TelegramUserRaw = TelegramUserRaw(
    id=1356311909,
    first_name="Brain",
    username="imcatboy",
    is_premium=True,
    language_code="ru",
)


def validate_init_data(init_data: str, max_age: int = 3600) -> TelegramUserRaw:
    params = dict(parse_qsl(unquote(init_data)))
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(params.items()) if k != "hash"
    )
    secret_key = hmac.new(
        b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if calculated_hash != params.get("hash"):
        raise ValueError("Invalid signature")

    auth_date = datetime.fromtimestamp(int(params.get("auth_date", 0)), tz=timezone.utc)
    if (datetime.now(tz=timezone.utc) - auth_date).total_seconds() > max_age:
        raise ValueError("Expired initData")

    return TelegramUserRaw.model_validate(json.loads(params.get("user", "{}")))


async def resolve_current_user(
    init_data: str, user_service: UserService
) -> entities.UserEntity:
    try:
        telegram_user = TEST_TELEGRAM_USER
        # telegram_user = validate_init_data(init_data, settings.BOT_TOKEN)
    except Exception:
        raise HTTPException(401, "Telegram auth failed")

    return await user_service.get_or_create(telegram_user.id, telegram_user.username)


async def get_current_user(
    init_data: str = Header(
        ..., alias="X-Telegram-Init-Data", description="Telegram init data"
    ),
    user_service: UserService = Depends(get_user_service),
) -> entities.UserEntity:
    return await resolve_current_user(init_data, user_service)


@inject
async def get_current_user_cached(
    init_data: str = Header(
        ..., alias="X-Telegram-Init-Data", description="Telegram init data"
    ),
    user_service: UserService = Depends(get_user_service),
    redis: Redis = Depends(Provide[AppContainer.redis]),
) -> entities.UserEntity:
    cache_key = "auth:" + hashlib.sha256(init_data.encode()).hexdigest()
    cached = await redis.get(cache_key)

    if cached:
        return entities.UserEntity.model_validate_json(cached)

    user = await resolve_current_user(init_data, user_service)
    await redis.setex(cache_key, 900, user.model_dump_json())
    return user
