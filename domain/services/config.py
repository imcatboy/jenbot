from typing import Any

from domain.repositories import ConfigRepository


class ConfigService:

    def __init__(self, config_repository: ConfigRepository) -> None:
        self.config_repository = config_repository

    async def get(self, key: str, default: Any = None) -> Any:
        return await self.config_repository.get_cached(key, default)

    async def set(self, key: str, value: Any) -> None:
        await self.config_repository.set_cached(key, value)
