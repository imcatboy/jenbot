from redis.exceptions import ReadOnlyError
from redis.asyncio import Redis
from typing import Any

import logging

logger = logging.getLogger(__name__)


class BaseCache:

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str, default: Any = None) -> Any:
        return await self.redis.get(key) or default

    async def set(self, key: str, value: Any, expire: int = 60 * 60) -> None:
        try:
            await self.redis.set(key, value, ex=expire)
        except ReadOnlyError:
            logger.error(f"Error setting cache: Redis is in read only mode")

    async def delete(self, *keys: str) -> None:
        await self.redis.delete(*keys)

