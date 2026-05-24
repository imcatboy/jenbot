from typing import Callable, Dict, Any, Awaitable, Union
from aiogram.types import Message, CallbackQuery
from aiogram import BaseMiddleware
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float) -> None:
        self.cache = TTLCache[str, bool](maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)

        if isinstance(event, Message) and event.media_group_id:
            return await handler(event, data)

        user_id = event.from_user.id
        
        event_type = "msg" if isinstance(event, Message) else "cb"
        cache_key = f"{event_type}:{user_id}"

        if cache_key in self.cache:
            if isinstance(event, CallbackQuery):
                await event.answer("Too many requests! Please wait a second.", show_alert=False)
            
            return

        self.cache[cache_key] = True
        return await handler(event, data)
