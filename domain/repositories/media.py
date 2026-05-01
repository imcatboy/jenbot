from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from domain.objects import dtos, entities, models


class MediaRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_file(self, dto: dtos.CreateFileDTO) -> entities.FileEntity:
        file = models.FileModel(**dto.model_dump())
        await self.create_relation(file, models.UserModel, dto.uploaded_by_user_id)
        await self.set_optional_relation(file, models.MessageModel, dto.message_id)
        await self.set_optional_relation(file, models.ProductModel, dto.product_id)
        self.session.add(file)
        await self.session.flush()
        return entities.FileEntity.model_validate(file)

    async def link_file_to_marketplace_user(self, file_id: int, user_id: int) -> None:
        file = await self.get_one_by_data(models.MarketplaceUserModel, user_id=user_id)
        await self.create_relation(file, models.FileModel, file_id, "avatar_id")
        await self.session.flush()

    async def get_file(self, file_id: int) -> entities.FileEntity:
        file = await self.get_by_id(models.FileModel, file_id)
        return entities.FileEntity.model_validate(file)