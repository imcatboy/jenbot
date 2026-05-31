from redis.asyncio import Redis

from domain.objects import entities
from domain.cache import keys
from .base import BaseCache


class MediaCache(BaseCache):

    def __init__(self, redis: Redis, telegram_file_ttl: int = 60 * 60):
        super().__init__(redis)
        self.telegram_file_ttl = telegram_file_ttl

    async def get_telegram_file(self, name: str) -> entities.TelegramFileEntity | None:
        file = await self.get(keys.get_telegram_file_key(name))

        if file:
            return entities.TelegramFileEntity.model_validate_json(file)

        return None

    async def set_telegram_file(
        self, name: str, file: entities.TelegramFileEntity
    ) -> None:
        await self.set(
            keys.get_telegram_file_key(name),
            file.model_dump_json(),
            expire=self.telegram_file_ttl,
        )

    async def invalidate_telegram_file(self, name: str) -> None:
        await self.delete(keys.get_telegram_file_key(name))
