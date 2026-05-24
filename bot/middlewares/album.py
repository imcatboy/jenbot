import asyncio

from typing import Any, Awaitable, Callable, Dict, List
from aiogram.types.message import Message
from aiogram import BaseMiddleware
from cachetools import TTLCache


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.5) -> None:
        self.latency = latency
        self.cache = TTLCache[str, List[Message]](maxsize=1000, ttl=latency * 3)
        self.lock_cache = TTLCache[str, bool](maxsize=1000, ttl=latency * 3)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        if event.media_group_id not in self.cache:
            self.cache[event.media_group_id] = []

        self.cache[event.media_group_id].append(event)

        if event.media_group_id in self.lock_cache:
            return

        self.lock_cache[event.media_group_id] = True
        await asyncio.sleep(self.latency)
        album = self.cache.pop(event.media_group_id, [])
        self.lock_cache.pop(event.media_group_id, None)
        album.sort(key=lambda x: x.message_id)
        data["album"] = album
        return await handler(event, data)
