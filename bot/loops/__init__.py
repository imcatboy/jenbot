import asyncio
import logging

from sqlalchemy.ext.asyncio import async_sessionmaker
from redis.asyncio import Redis
from aiogram import Bot
from typing import List

from domain.repositories import ModerationRepository, UserRepository, ConfigRepository
from domain.services import ModerationService, ConfigService
from .violations import actualize_violations_loop
from domain.uow import SQLAlchemyUnitOfWork
from domain.cache import ModerationCache

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
                    moderation_cache = ModerationCache(redis=self.redis, tracker_ttl=60 * 60 * 24)
                    moderation_service = ModerationService(
                        moderation_repository=moderation_repository,
                        user_repository=user_repository,
                        config_service=config_service,
                        moderation_cache=moderation_cache,
                    )
                    await actualize_violations_loop(self.bot, moderation_service, config_service)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Scheduler critical error: {e}", exc_info=True)
            finally:
                await asyncio.sleep(60)
