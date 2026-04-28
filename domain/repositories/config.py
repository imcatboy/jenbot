import json

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from sqlalchemy import select
from typing import Any

from domain.objects.models import ConfigModel
from .base import BaseRepository

class ConfigRepository(BaseRepository):

    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        super().__init__(session)
        self.redis = redis
        self.ttl = 60 * 60

    async def get(self, key: str, default: Any = None) -> Any:
        result = await self.session.execute(
            select(ConfigModel).where(ConfigModel.key == key)
        )
        config = result.scalar_one_or_none()

        if config is None:
            return default

        return config.value

    async def set(self, key: str, value: Any) -> None:
        result = await self.session.execute(
            select(ConfigModel).where(ConfigModel.key == key)
        )
        config = result.scalar_one_or_none()

        if config is None:
            config = ConfigModel(key=key, value=value)
            self.session.add(config)
        else:
            config.value = value

    async def get_cached(self, key: str, default: Any = None) -> Any:
        config = await self.redis.get(f"config:{key}")

        if config is not None:
            return json.loads(config)

        value = await self.get(key, default)

        if value is not None:
            await self.redis.set(f"config:{key}", json.dumps(value), ex=self.ttl)

        return value

    async def set_cached(self, key: str, value: Any) -> None:
        await self.redis.delete(f"config:{key}")
        await self.set(key, value)
