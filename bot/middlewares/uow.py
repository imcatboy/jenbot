from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware

from domain import SQLAlchemyUnitOfWork


class UOWMiddleware(BaseMiddleware):

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        uow = SQLAlchemyUnitOfWork(self.session_factory)
        data["uow"] = uow

        async with uow:
            return await handler(event, data)