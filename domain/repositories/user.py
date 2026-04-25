from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from redis.asyncio import Redis
from sqlalchemy.orm import joinedload

from .relations import get_user_reputation_relations
from objects import models, entities, dtos
from objects.types import UserRole
from .base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession, redis: Redis, cache_ttl: int) -> None:
        super().__init__(session)
        self.redis = redis
        self.cache_ttl = cache_ttl

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
    ) -> None:
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

    async def get_user_reputation(
        self, user_id: int
    ) -> entities.ReputationUserWithUserEntity:
        user_reputation = await self.get_one_by_data(
            models.ReputationUserModel,
            user_id=user_id,
            options=get_user_reputation_relations(),
        )
        return entities.ReputationUserWithUserEntity.model_validate(user_reputation)

    async def get_or_create_cached(
        self, telegram_id: int, username: Optional[str]
    ) -> entities.UserEntity:
        user = await self.redis.get(f"user:{telegram_id}")

        if user:
            return entities.UserEntity.model_validate_json(user)

        user = await self.get_or_create(telegram_id, username)
        await self.redis.set(
            f"user:{telegram_id}", user.model_dump_json(), ex=self.cache_ttl
        )
        return user

    async def get_or_create_marketplace_user(
        self, user_id: int
    ) -> entities.MarketplaceUserWithUserEntity:
        marketplace_user = await self.get_one_by_data_or_none(
            models.MarketplaceUserModel,
            user_id=user_id,
            options=[joinedload(models.MarketplaceUserModel.user)],
        )

        if marketplace_user:
            return entities.MarketplaceUserWithUserEntity.model_validate(
                marketplace_user
            )

        marketplace_user = models.MarketplaceUserModel()
        await self.create_relation(marketplace_user, models.UserModel, user_id)
        self.session.add(marketplace_user)
        await self.session.flush()
        marketplace_user = await self.get_one_by_data(
            models.MarketplaceUserModel,
            user_id=user_id,
            options=[joinedload(models.MarketplaceUserModel.user)],
        )
        return entities.MarketplaceUserWithUserEntity.model_validate(marketplace_user)

    async def get_or_create_marketplace_user_cached(
        self, user_id: int
    ) -> entities.MarketplaceUserWithUserEntity:
        marketplace_user = await self.redis.get(f"marketplace_user:{user_id}")

        if marketplace_user:
            return entities.MarketplaceUserWithUserEntity.model_validate_json(
                marketplace_user
            )

        marketplace_user = await self.get_or_create_marketplace_user(user_id)
        await self.redis.set(
            f"marketplace_user:{user_id}",
            marketplace_user.model_dump_json(),
            ex=self.cache_ttl,
        )
        return marketplace_user
