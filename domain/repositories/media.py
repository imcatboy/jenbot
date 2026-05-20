from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from .base import BaseRepository
from domain.objects import dtos, entities, models


class MediaRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_file(self, dto: dtos.CreateFileDTO) -> entities.FileEntity:
        file = models.FileModel(**dto.model_dump())
        await self.create_relation(file, models.UserModel, dto.uploaded_by_user_id)
        self.session.add(file)
        await self.session.flush()
        return entities.FileEntity.model_validate(file)

    async def link_file_to_marketplace_user(self, file_id: int, user_id: int) -> None:
        file = await self.get_one_by_data(models.MarketplaceUserModel, user_id=user_id)
        await self.create_relation(file, models.FileModel, file_id, "avatar_id")
        await self.session.flush()

    async def is_user_unlinked_files(self, user_id: int, file_ids: List[int]) -> bool:
        if not file_ids:
            return True

        file_ids = list(set(file_ids))
        query = select(func.count(models.FileModel.id)).where(
            models.FileModel.uploaded_by_user_id == user_id,
            models.FileModel.id.in_(file_ids),
            models.FileModel.message_id.is_(None),
            models.FileModel.product_id.is_(None),
            models.FileModel.marketplace_user.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one() == len(file_ids)

    async def get_file(self, file_id: int) -> entities.FileEntity:
        file = await self.get_by_id(models.FileModel, file_id)
        return entities.FileEntity.model_validate(file)

    async def get_product_file(
        self, product_id: int, file_id: int
    ) -> entities.FileEntity:
        file = await self.get_one_by_data(
            models.FileModel, product_id=product_id, id=file_id
        )
        return entities.FileEntity.model_validate(file)

    async def get_message_file(
        self, message_id: int, file_id: int
    ) -> entities.FileEntity:
        file = await self.get_one_by_data(
            models.FileModel, message_id=message_id, id=file_id
        )
        return entities.FileEntity.model_validate(file)
