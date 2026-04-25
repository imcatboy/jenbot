from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from domain.services import UserService, ModerationService, ConfigService
from domain.repositories import UserRepository, ModerationRepository, ConfigRepository
from core.settings import Settings
from redis.asyncio import Redis


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".dependencies"])

    settings = providers.Singleton(Settings)
    engine = providers.Singleton(create_async_engine, settings.DATABASE_URL)
    session_factory = providers.Singleton(async_sessionmaker, bind=engine)
    redis = providers.Singleton(Redis, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    user_repository = providers.Factory(UserRepository, session=session_factory, redis=redis)
    user_service = providers.Factory(UserService, user_repository=user_repository)
    moderation_repository = providers.Factory(
        ModerationRepository, session=session_factory
    )
    moderation_service = providers.Factory(
        ModerationService, moderation_repository=moderation_repository
    )
    config_repository = providers.Factory(ConfigRepository, session=session_factory)
    config_service = providers.Factory(
        ConfigService, config_repository=config_repository
    )
