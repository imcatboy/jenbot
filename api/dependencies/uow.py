from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from dependency_injector.wiring import inject, Provide
from typing import AsyncGenerator
from redis.asyncio import Redis
from fastapi import Depends

from api.core.container import AppContainer
from domain import SQLAlchemyUnitOfWork
from domain.cache import *
from domain.repositories import *
from domain.services import *
from domain.mappers import *


@inject
async def get_uow(
    session_factory: async_sessionmaker[AsyncSession] = Depends(
        Provide[AppContainer.session_factory]
    ),
) -> AsyncGenerator[SQLAlchemyUnitOfWork, None]:
    uow = SQLAlchemyUnitOfWork(session_factory=session_factory)

    async with uow:
        yield uow


@inject
async def get_user_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    redis: Redis = Depends(Provide[AppContainer.redis]),
) -> UserService:
    user_repository = UserRepository(session=uow.session)
    user_cache = UserCache(redis=redis)
    media_repository = MediaRepository(session=uow.session)
    return UserService(
        user_repository=user_repository,
        user_cache=user_cache,
        media_repository=media_repository,
    )


async def get_product_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> ProductService:
    product_repository = ProductRepository(session=uow.session)
    media_repository = MediaRepository(session=uow.session)
    return ProductService(
        product_repository=product_repository, media_repository=media_repository
    )


async def get_media_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> MediaService:
    media_repository = MediaRepository(session=uow.session)
    return MediaService(media_repository=media_repository)


async def get_marketplace_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> MarketplaceService:
    marketplace_repository = MarketplaceRepository(session=uow.session)
    mapper = MarketplaceMapper()
    product_repository = ProductRepository(session=uow.session)
    return MarketplaceService(
        marketplace_repository=marketplace_repository,
        mapper=mapper,
        product_repository=product_repository,
    )


async def get_trading_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    redis: Redis = Depends(Provide[AppContainer.redis]),
) -> TradingService:
    trading_repository = TradingRepository(session=uow.session)
    marketplace_repository = MarketplaceRepository(session=uow.session)
    messaging_repository = MessagingRepository(session=uow.session)
    user_repository = UserRepository(session=uow.session)
    user_cache = UserCache(redis=redis)
    media_repository = MediaRepository(session=uow.session)
    user_service = UserService(
        user_repository=user_repository,
        user_cache=user_cache,
        media_repository=media_repository,
    )
    return TradingService(
        trading_repository=trading_repository,
        marketplace_repository=marketplace_repository,
        messaging_repository=messaging_repository,
        user_repository=user_repository,
        user_service=user_service,
    )


async def get_messaging_service(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> MessagingService:
    messaging_repository = MessagingRepository(session=uow.session)
    return MessagingService(messaging_repository=messaging_repository)
