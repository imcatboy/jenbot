import asyncio
import logging

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from redis.asyncio import Redis
from contextlib import suppress
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from bot.handlers import handler_routers
from bot.core.settings import Settings
from bot.loops import SchedulerService
from bot.middlewares import *


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8", mode="a"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20
)
session_factory = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
    socket_connect_timeout=5,
)

fsm_storage = RedisStorage(redis)
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    # session=AiohttpSession(proxy=settings.PROXY_URL),
)
dp = Dispatcher(storage=fsm_storage)

scheduler_service = SchedulerService(
    session_factory=session_factory, bot=bot, redis=redis
)

dp.message.outer_middleware(ThrottlingMiddleware(rate_limit=1.0))
dp.callback_query.outer_middleware(ThrottlingMiddleware(rate_limit=1.0))
dp.update.outer_middleware(UOWMiddleware(session_factory=session_factory))
dp.update.outer_middleware(DIMiddleware(redis=redis, settings=settings))
dp.message.outer_middleware(AlbumMiddleware(latency=0.5))
dp.message.outer_middleware(UserMiddleware())
dp.callback_query.outer_middleware(UserMiddleware())
dp.message.outer_middleware(WordsMiddleware())
dp.message.outer_middleware(TrackerMiddleware())
dp.message.middleware(SubscriptionsMiddleware())
dp.callback_query.middleware(SubscriptionsMiddleware())
dp.message.middleware(RoleMiddleware())
dp.callback_query.middleware(RoleMiddleware())
dp.message.middleware(CommandValidationMiddleware())
dp.message.middleware(StateMiddleware())
dp.message.middleware(MediaCheckMiddleware())
dp.include_routers(*handler_routers)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="check", description="Проверить репутацию пользователя"),
        BotCommand(command="report", description="Создать жалобу"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Commands set")


async def check_connections():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        await redis.ping()
        logger.info("Connections to DB and Redis checked")
        return True
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False


async def on_shutdown(
    bot: Bot, engine: AsyncEngine, redis: Redis, scheduler_service: SchedulerService
):
    logger.info("Shutdown...")
    await scheduler_service.stop()
    await bot.session.close()
    await redis.aclose()
    await engine.dispose()
    logger.info("Resources released")


@dp.startup()
async def on_startup(bot: Bot, scheduler_service: SchedulerService):
    if not await check_connections():
        logger.critical("Failed to connect to DB/Redis. Shutdown.")
        raise SystemExit(1)

    await set_bot_commands(bot)
    await scheduler_service.start()
    logger.info(f"Bot @{(await bot.get_me()).username} started with scheduler")


async def main():
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        engine=engine,
        redis=redis,
        scheduler_service=scheduler_service,
    )


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
