from redis.asyncio import Redis

from .base import BaseCache
from domain.cache import keys
from domain.objects import entities


class UserCache(BaseCache):

    def __init__(self, redis: Redis, ttl: int = 60 * 60):
        super().__init__(redis)
        self.ttl = ttl

    async def get_user_by_id(self, user_id: int) -> entities.UserEntity | None:
        user = await self.get(keys.get_user_by_id_key(user_id))

        if user:
            return entities.UserEntity.model_validate_json(user)

        return None

    async def get_user_by_telegram_id(
        self, telegram_id: int
    ) -> entities.UserEntity | None:
        user = await self.get(keys.get_user_by_telegram_id_key(telegram_id))

        if user:
            return entities.UserEntity.model_validate_json(user)

        return None

    async def set_user(self, user: entities.UserEntity) -> None:
        await self.set(
            keys.get_user_by_id_key(user.id), user.model_dump_json(), expire=self.ttl
        )
        await self.set(
            keys.get_user_by_telegram_id_key(user.telegram_id),
            user.model_dump_json(),
            expire=self.ttl,
        )

    async def get_profile(self, user_id: int) -> entities.ProfileEntity | None:
        profile = await self.get(keys.get_profile_key(user_id))

        if profile:
            return entities.ProfileEntity.model_validate_json(profile)

        return None

    async def set_profile(self, user_id: int, profile: entities.ProfileEntity) -> None:
        await self.set(
            keys.get_profile_key(user_id), profile.model_dump_json(), expire=self.ttl
        )

    async def get_marketplace_user(
        self, user_id: int
    ) -> entities.UserWithMarketplaceUserEntity | None:
        marketplace_user = await self.get(keys.get_marketplace_user_key(user_id))

        if marketplace_user:
            return entities.UserWithMarketplaceUserEntity.model_validate_json(
                marketplace_user
            )

        return None

    async def set_marketplace_user(
        self, user_id: int, marketplace_user: entities.UserWithMarketplaceUserEntity
    ) -> None:
        await self.set(
            keys.get_marketplace_user_key(user_id),
            marketplace_user.model_dump_json(),
            expire=self.ttl,
        )

    async def get_user_reputation(
        self, user_id: int
    ) -> entities.ReputationUserWithUserEntity | None:
        user_reputation = await self.get(keys.get_reputation_user_key(user_id))

        if user_reputation:
            return entities.ReputationUserWithUserEntity.model_validate_json(
                user_reputation
            )

        return None

    async def set_user_reputation(
        self, user_id: int, user_reputation: entities.ReputationUserWithUserEntity
    ) -> None:
        await self.set(
            keys.get_reputation_user_key(user_id),
            user_reputation.model_dump_json(),
            expire=self.ttl,
        )

    async def invalidate_user(self, user: entities.UserEntity) -> None:
        await self.delete(*keys.get_user_keys(user))
