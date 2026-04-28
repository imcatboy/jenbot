from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from redis.asyncio import Redis

from api.core.settings import Settings


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["api.dependencies", "api.endpoints"])

    settings = providers.Singleton(Settings)
    engine = providers.Singleton(create_async_engine, settings.provided.DATABASE_URL)
    session_factory = providers.Singleton(async_sessionmaker, bind=engine)
    redis = providers.Singleton(
        Redis,
        host=settings.provided.REDIS_HOST,
        port=settings.provided.REDIS_PORT,
        db=settings.provided.REDIS_DB,
    )