from domain.repositories import MediaRepository
from domain.objects import dtos, entities
from domain.cache import MediaCache


class MediaService:

    def __init__(
        self, media_repository: MediaRepository, media_cache: MediaCache
    ) -> None:
        self.media_repository = media_repository
        self.media_cache = media_cache

    async def create_file(self, dto: dtos.CreateFileDTO) -> entities.FileEntity:
        return await self.media_repository.create_file(dto)

    async def get_file(self, file_id: int) -> entities.FileEntity:
        return await self.media_repository.get_file(file_id)

    async def link_file_to_marketplace_user(self, file_id: int, user_id: int) -> None:
        await self.media_repository.link_file_to_marketplace_user(file_id, user_id)

    async def get_telegram_file(self, name: str) -> entities.TelegramFileEntity:
        file = await self.media_cache.get_telegram_file(name)

        if file:
            return file

        file = await self.media_repository.get_telegram_file(name)
        await self.media_cache.set_telegram_file(name, file)
        return file

    async def create_telegram_file(
        self, name: str, file_id: str
    ) -> entities.TelegramFileEntity:
        file = await self.media_repository.create_telegram_file(name, file_id)
        await self.media_cache.set_telegram_file(name, file)
        return file
