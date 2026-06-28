import asyncio
import logging

from sqlalchemy.ext.asyncio import async_sessionmaker
from aiogram.exceptions import TelegramNetworkError
from redis.asyncio import Redis
from aiogram import Bot
from typing import List

from domain.repositories import *
from domain.services import *
from domain.cache import ModerationCache, UserCache
from bot.actions import TradingActions
from .violations import actualize_violations_loop
from .external_deals import expire_external_deals_loop
from domain.uow import SQLAlchemyUnitOfWork

logger = logging.getLogger(__name__)


class SchedulerService:

    def __init__(self, session_factory: async_sessionmaker, bot: Bot, redis: Redis):
        self.session_factory = session_factory
        self.bot = bot
        self.redis = redis
        self._tasks: List[asyncio.Task] = []

    async def start(self):
        self._tasks.append(
            asyncio.create_task(self._run_violations_loop(), name="violations_loop")
        )
        self._tasks.append(
            asyncio.create_task(
                self._run_external_deals_loop(), name="external_deals_loop"
            )
        )
        logger.info("Scheduler started")

    async def stop(self):
        for task in self._tasks:
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")

    async def _run_violations_loop(self):
        while True:
            try:
                async with SQLAlchemyUnitOfWork(self.session_factory) as uow:
                    moderation_repository = ModerationRepository(uow.session)
                    user_repository = UserRepository(uow.session)
                    config_repository = ConfigRepository(uow.session, self.redis)
                    config_service = ConfigService(config_repository=config_repository)
                    moderation_cache = ModerationCache(
                        redis=self.redis, tracker_ttl=60 * 60 * 24
                    )
                    moderation_service = ModerationService(
                        moderation_repository=moderation_repository,
                        user_repository=user_repository,
                        config_service=config_service,
                        moderation_cache=moderation_cache,
                    )
                    await actualize_violations_loop(
                        self.bot, moderation_service, config_service
                    )
            except asyncio.CancelledError:
                break
            except TelegramNetworkError as e:
                logger.warning("Scheduler network error, will retry: %s", e)
            except Exception as e:
                logger.error("Scheduler error: %s", e, exc_info=True)
            finally:
                await asyncio.sleep(60)

    async def _run_external_deals_loop(self):
        while True:
            try:
                async with SQLAlchemyUnitOfWork(self.session_factory) as uow:
                    user_repository = UserRepository(uow.session)
                    user_cache = UserCache(redis=self.redis)
                    media_repository = MediaRepository(uow.session)
                    user_service = UserService(
                        user_repository=user_repository,
                        user_cache=user_cache,
                        media_repository=media_repository,
                    )
                    trading_repository = TradingRepository(uow.session)
                    marketplace_repository = MarketplaceRepository(uow.session)
                    messaging_repository = MessagingRepository(uow.session)
                    trading_service = TradingService(
                        trading_repository=trading_repository,
                        marketplace_repository=marketplace_repository,
                        messaging_repository=messaging_repository,
                        user_repository=user_repository,
                        user_service=user_service,
                    )
                    config_repository = ConfigRepository(uow.session, self.redis)
                    config_service = ConfigService(config_repository=config_repository)
                    trading_actions = TradingActions(
                        bot=self.bot,
                        trading_service=trading_service,
                        config_service=config_service,
                    )
                    await expire_external_deals_loop(trading_service, trading_actions)
            except asyncio.CancelledError:
                break
            except TelegramNetworkError as e:
                logger.warning("External deals loop network error, will retry: %s", e)
            except Exception as e:
                logger.error("External deals loop error: %s", e, exc_info=True)
            finally:
                await asyncio.sleep(60)
