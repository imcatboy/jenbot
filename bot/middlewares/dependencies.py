from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware
from redis.asyncio import Redis
from aiogram import Bot

from domain import SQLAlchemyUnitOfWork
from bot.core.settings import Settings
from domain.repositories import *
from domain.services import *
from bot.actions import *


class DIMiddleware(BaseMiddleware):

    def __init__(self, redis: Redis, settings: Settings) -> None:
        self.redis = redis
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        uow: SQLAlchemyUnitOfWork = data["uow"]
        bot: Bot = data["bot"]
        data["settings"] = self.settings
        config_repository = ConfigRepository(session=uow.session, redis=self.redis)
        config_service = ConfigService(config_repository=config_repository)
        data["config_service"] = config_service
        user_repository = UserRepository(session=uow.session)
        user_service = UserService(user_repository=user_repository)
        data["user_service"] = user_service
        moderation_repository = ModerationRepository(session=uow.session)
        moderation_service = ModerationService(
            moderation_repository=moderation_repository,
            user_repository=user_repository,
            config_service=config_service,
        )
        data["moderation_service"] = moderation_service
        moderation_actions = ModerationActions(
            moderation_service=moderation_service,
            user_service=user_service,
            config_service=config_service,
            bot=bot,
        )
        data["moderation_actions"] = moderation_actions
        user_actions = UserActions(user_service=user_service, bot=bot)
        data["user_actions"] = user_actions
        return await handler(event, data)
