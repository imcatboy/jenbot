from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from objects import models, entities, dtos
from .base import BaseRepository
from objects.types import UserRole
from .relations import get_user_reputation_relations


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_or_create(
        self, telegram_id: int, username: str
    ) -> entities.UserEntity:
        user = await self.get_one_by_data_or_none(
            models.UserModel, telegram_id=telegram_id
        )

        if user:
            user.username = username
            return entities.UserEntity.model_validate(user)

        user = models.UserModel(telegram_id=telegram_id, username=username)
        self.session.add(user)
        await self.session.flush()
        return entities.UserEntity.model_validate(user)

    async def get(self, id: int) -> entities.UserEntity:
        user = await self.get_by_id(models.UserModel, id)
        return entities.UserEntity.model_validate(user)

    async def get_by_telegram_id(self, telegram_id: int) -> entities.UserEntity:
        user = await self.get_one_by_data(models.UserModel, telegram_id=telegram_id)
        return entities.UserEntity.model_validate(user)

    async def get_by_username(self, username: str) -> entities.UserEntity:
        user = await self.get_one_by_data(models.UserModel, username=username)
        return entities.UserEntity.model_validate(user)

    async def update_role(self, id: int, role: UserRole) -> None:
        user = await self.get_by_id(models.UserModel, id)
        user.role = role

    async def get_by_role(self, role: UserRole) -> List[entities.UserEntity]:
        users = await self.get_all_by_data(models.UserModel, role=role)
        return [entities.UserEntity.model_validate(user) for user in users]

    async def create_user_reputation(self, dto: dtos.CreateUserReputationDTO) -> entities.ReputationUserEntity:
        user_reputation = models.ReputationUserModel(
            description=dto.description,
            role=dto.role,
        )
        await self.create_relation(user_reputation, models.UserModel, dto.user_id)
        await self.create_relation(user_reputation, models.UserModel, dto.added_by_user_id, "added_by_user_id")
        self.session.add(user_reputation)
        await self.session.flush()
        return entities.ReputationUserEntity.model_validate(user_reputation)
    
    async def update_user_reputation(self, user_id: int, dto: dtos.UpdateUserReputationDTO) -> None:
        user_reputation = await self.get_one_by_data(models.ReputationUserModel, user_id=user_id)

        if dto.description is not None:
            user_reputation.description = dto.description
        if dto.role is not None:
            user_reputation.role = dto.role

        await self.update_relation(user_reputation, models.UserModel, dto.added_by_user_id, "added_by_user_id")
        await self.session.flush()
    
    async def get_user_reputation(self, user_id: int) -> entities.ReputationUserWithUserEntity:
        user_reputation = await self.get_one_by_data(models.ReputationUserModel, user_id=user_id, options=get_user_reputation_relations())
        return entities.ReputationUserWithUserEntity.model_validate(user_reputation)