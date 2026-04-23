import asyncio

from typing import Any, Awaitable, Callable, Dict, List
from aiogram.types.message import Message
from aiogram import BaseMiddleware
from cachetools import TTLCache


class AlbumMiddleware(BaseMiddleware):

    def __init__(self, latency: float) -> None:
        self.latency = latency
        self.cache = TTLCache[str, List[Message]](maxsize=1000, ttl=latency)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        if event.media_group_id in self.cache.keys():
            self.cache[event.media_group_id].append(event)
            return 
        
        self.cache[event.media_group_id] = [event]
        await asyncio.sleep(self.latency)
        data["album"] = self.cache.pop(event.media_group_id)
        return await handler(event, data)