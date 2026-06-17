from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware
from redis.asyncio import Redis
from aiogram import Bot

from domain import SQLAlchemyUnitOfWork
from bot.core.settings import Settings
from domain.repositories import *
from domain.services import *
from domain.cache import *
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
        user_cache = UserCache(redis=self.redis)
        media_repository = MediaRepository(session=uow.session)
        media_cache = MediaCache(redis=self.redis)
        media_service = MediaService(
            media_repository=media_repository, media_cache=media_cache
        )
        data["media_service"] = media_service
        user_service = UserService(
            user_repository=user_repository,
            user_cache=user_cache,
            media_repository=media_repository,
        )
        data["user_service"] = user_service
        moderation_repository = ModerationRepository(session=uow.session)
        moderation_cache = ModerationCache(redis=self.redis, tracker_ttl=60 * 60 * 24)
        moderation_service = ModerationService(
            moderation_repository=moderation_repository,
            user_repository=user_repository,
            config_service=config_service,
            moderation_cache=moderation_cache,
        )
        media_actions = MediaActions(
            media_service=media_service,
            bot=bot,
            config_service=config_service,
        )
        data["media_actions"] = media_actions
        data["moderation_service"] = moderation_service
        audit_actions = AuditActions(
            moderation_service=moderation_service,
            config_service=config_service,
            bot=bot,
        )
        marketplace_repository = MarketplaceRepository(session=uow.session)
        trading_repository = TradingRepository(session=uow.session)
        messaging_repository = MessagingRepository(session=uow.session)
        trading_service = TradingService(
            trading_repository=trading_repository,
            marketplace_repository=marketplace_repository,
            messaging_repository=messaging_repository,
            user_repository=user_repository,
        )
        moderation_actions = ModerationActions(
            moderation_service=moderation_service,
            user_service=user_service,
            config_service=config_service,
            bot=bot,
            media_actions=media_actions,
            trading_service=trading_service,
        )
        data["trading_service"] = trading_service
        data["audit_actions"] = audit_actions
        data["moderation_actions"] = moderation_actions
        user_actions = UserActions(user_service=user_service, bot=bot)
        data["user_actions"] = user_actions
        return await handler(event, data)
