from redis.asyncio import Redis
from typing import Any


class BaseCache:

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str, default: Any = None) -> Any:
        return await self.redis.get(key) or default

    async def set(self, key: str, value: Any, expire: int = 60 * 60) -> None:
        await self.redis.set(key, value, ex=expire)

    async def delete(self, *keys: str) -> None:
        await self.redis.delete(*keys)

