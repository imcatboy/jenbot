from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from cachetools import TTLCache

from bot.data import text


class ThrottlingMiddleware(BaseMiddleware):
    
    def __init__(self, rate_limit: float) -> None:
        self.cache = TTLCache[str, bool](maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        if not getattr(event, "from_user", None):
            return await handler(event, data)
        
        message: Message | None = None

        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            message = event.message

        if not message:
            return await handler(event, data)

        user_id = message.from_user.id

        if user_id in self.cache:
            return

        self.cache[user_id] = True
        return await handler(event, data)
