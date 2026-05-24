from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from typing import List, Optional

from .relations import get_user_reputation_relations, get_profile_relations
from domain.objects import models, entities, dtos
from domain.objects.types import UserRole
from .base import BaseRepository


class UserRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_or_create(
        self, telegram_id: int, username: Optional[str]
    ) -> entities.UserEntity:
        user = await self.get_one_by_data_or_none(
            models.UserModel, telegram_id=telegram_id
        )

        if user:
            user.username = username
            await self.session.flush()
            return entities.UserEntity.model_validate(user)

        try:
            user = models.UserModel(telegram_id=telegram_id, username=username)
            self.session.add(user)
            await self.session.flush()
        except IntegrityError:
            user = await self.get_one_by_data(models.UserModel, telegram_id=telegram_id)

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
        await self.session.flush()

    async def get_by_role(self, role: UserRole) -> List[entities.UserEntity]:
        users = await self.get_all_by_data(models.UserModel, role=role)
        return [entities.UserEntity.model_validate(user) for user in users]

    async def create_user_reputation(
        self, dto: dtos.CreateUserReputationDTO
    ) -> entities.ReputationUserEntity:
        user_reputation = models.ReputationUserModel(
            description=dto.description,
            role=dto.role,
        )
        await self.create_relation(user_reputation, models.UserModel, dto.user_id)
        await self.create_relation(
            user_reputation, models.UserModel, dto.added_by_user_id, "added_by_user_id"
        )
        self.session.add(user_reputation)
        await self.session.flush()
        return entities.ReputationUserEntity.model_validate(user_reputation)

    async def update_user_reputation(
        self, user_id: int, dto: dtos.UpdateUserReputationDTO
    ) -> entities.ReputationUserEntity:
        user_reputation = await self.get_one_by_data(
            models.ReputationUserModel, user_id=user_id
        )

        if dto.description is not None:
            user_reputation.description = dto.description
        if dto.role is not None:
            user_reputation.role = dto.role

        await self.update_relation(
            user_reputation, models.UserModel, dto.added_by_user_id, "added_by_user_id"
        )
        await self.session.flush()
        return entities.ReputationUserEntity.model_validate(user_reputation)

    async def get_user_reputation(
        self, user_id: int
    ) -> entities.ReputationUserWithUserEntity:
        user_reputation = await self.get_one_by_data(
            models.ReputationUserModel,
            user_id=user_id,
            options=get_user_reputation_relations(),
        )
        return entities.ReputationUserWithUserEntity.model_validate(user_reputation)

    async def get_or_create_marketplace_user(
        self, user_id: int
    ) -> entities.UserWithMarketplaceUserEntity:
        user = await self.get_one_by_data_or_none(
            models.UserModel,
            id=user_id,
            options=[joinedload(models.UserModel.marketplace_user)],
        )

        if user and user.marketplace_user:
            return entities.UserWithMarketplaceUserEntity.model_validate(user)

        marketplace_user = models.MarketplaceUserModel(user_id=user_id)
        self.session.add(marketplace_user)
        await self.session.flush()
        marketplace_user = await self.get_by_id(
            models.UserModel,
            id=user_id,
            options=[joinedload(models.UserModel.marketplace_user)],
        )
        return entities.UserWithMarketplaceUserEntity.model_validate(user)

    async def get_profile(self, user_id: int) -> entities.ProfileEntity:
        user = await self.get_by_id(
            models.UserModel,
            user_id,
            options=get_profile_relations(),
        )
        return entities.ProfileEntity.model_validate(user)

    async def update_marketplace_user(
        self, user_id: int, dto: dtos.UpdateMarketplaceUserDTO
    ) -> entities.MarketplaceUserEntity:
        marketplace_user = await self.get_one_by_data(
            models.MarketplaceUserModel, user_id=user_id
        )

        if dto.name is not None:
            marketplace_user.name = dto.name
        if dto.description is not None:
            marketplace_user.description = dto.description

        await self.update_relation
        await self.session.flush()
        return entities.MarketplaceUserEntity.model_validate(marketplace_user)
