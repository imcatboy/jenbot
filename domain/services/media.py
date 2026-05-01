from domain.repositories import MediaRepository
from domain.objects import dtos, entities


class MediaService:

    def __init__(self, media_repository: MediaRepository) -> None:
        self.media_repository = media_repository

    async def create_file(self, dto: dtos.CreateFileDTO) -> entities.FileEntity:
        return await self.media_repository.create_file(dto)

    async def get_file(self, file_id: int) -> entities.FileEntity:
        return await self.media_repository.get_file(file_id)
    
    async def link_file_to_marketplace_user(self, file_id: int, user_id: int) -> None:
        await self.media_repository.link_file_to_marketplace_user(file_id, user_id)