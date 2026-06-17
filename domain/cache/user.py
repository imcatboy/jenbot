import re

from pydantic import TypeAdapter
from redis.asyncio import Redis
from typing import List

from .base import BaseCache
from domain.cache import keys
from domain.objects import entities


ReputationUsersAdapter = TypeAdapter(List[entities.ReputationUserWithRelationsEntity])


class UserCache(BaseCache):

    def __init__(
        self,
        redis: Redis,
        user_ttl: int = 60 * 60,
        auth_ttl: int = 900,
        reputation_user_ttl: int = 60 * 60,
        reputation_user_details_ttl: int = 60 * 5,
    ):
        super().__init__(redis)
        self.user_ttl = user_ttl
        self.auth_ttl = auth_ttl
        self.reputation_user_ttl = reputation_user_ttl
        self.reputation_user_details_ttl = reputation_user_details_ttl

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
            keys.get_user_by_id_key(user.id),
            user.model_dump_json(),
            expire=self.user_ttl,
        )
        await self.set(
            keys.get_user_by_telegram_id_key(user.telegram_id),
            user.model_dump_json(),
            expire=self.user_ttl,
        )

    async def get_profile(self, user_id: int) -> entities.ProfileEntity | None:
        profile = await self.get(keys.get_profile_key(user_id))

        if profile:
            return entities.ProfileEntity.model_validate_json(profile)

        return None

    async def set_profile(self, user_id: int, profile: entities.ProfileEntity) -> None:
        await self.set(
            keys.get_profile_key(user_id),
            profile.model_dump_json(),
            expire=self.user_ttl,
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
            expire=self.user_ttl,
        )

    async def set_reputation_user(
        self, reputation_user: entities.ReputationUserWithRelationsEntity
    ) -> None:
        await self.set(
            keys.get_reputation_user_key(reputation_user.id),
            reputation_user.model_dump_json(),
            expire=self.reputation_user_ttl,
        )

    async def get_reputation_user(
        self, reputation_user_id: int
    ) -> entities.ReputationUserWithRelationsEntity | None:
        reputation_user = await self.get(
            keys.get_reputation_user_key(reputation_user_id)
        )

        if reputation_user:
            return entities.ReputationUserWithRelationsEntity.model_validate_json(
                reputation_user
            )

        return None

    async def set_reputation_user_by_user_id(
        self, user_id: int, reputation_user: entities.ReputationUserWithRelationsEntity
    ) -> None:
        await self.set_reputation_user(reputation_user)
        await self.set(
            keys.get_reputation_user_by_user_id_key(user_id),
            reputation_user.id,
            expire=self.reputation_user_ttl,
        )

    async def get_reputation_user_by_user_id(
        self, user_id: int
    ) -> entities.ReputationUserWithRelationsEntity | None:
        reputation_user_id = await self.get(
            keys.get_reputation_user_by_user_id_key(user_id)
        )

        if reputation_user_id:
            return await self.get_reputation_user(reputation_user_id)

        return None

    async def set_reputation_user_by_telegram_id(
        self,
        telegram_id: int,
        reputation_user: entities.ReputationUserWithRelationsEntity,
    ) -> None:
        await self.set_reputation_user(reputation_user)
        await self.set(
            keys.get_reputation_user_by_telegram_id_key(telegram_id),
            reputation_user.id,
            expire=self.reputation_user_ttl,
        )

    async def get_reputation_user_by_telegram_id(
        self, telegram_id: int
    ) -> entities.ReputationUserWithRelationsEntity | None:
        reputation_user_id = await self.get(
            keys.get_reputation_user_by_telegram_id_key(telegram_id)
        )

        if reputation_user_id:
            return await self.get_reputation_user(reputation_user_id)

        return None

    async def set_reputation_users_by_username(
        self,
        username: str,
        reputation_users: List[entities.ReputationUserWithRelationsEntity],
    ) -> None:
        await self.set(
            keys.get_reputation_users_by_username_key(username),
            ReputationUsersAdapter.dump_json(reputation_users),
            expire=self.reputation_user_ttl,
        )

    async def get_reputation_users_by_username(
        self, username: str
    ) -> List[entities.ReputationUserWithRelationsEntity] | None:
        reputation_users = await self.get(
            keys.get_reputation_users_by_username_key(username)
        )

        if reputation_users:
            return ReputationUsersAdapter.validate_json(reputation_users)

        return None

    async def get_reputation_users_by_detail(
        self, detail: str
    ) -> List[entities.ReputationUserWithRelationsEntity] | None:
        reputation_users = await self.get(
            keys.get_reputation_user_by_detail_key(detail)
        )

        if reputation_users:
            return ReputationUsersAdapter.validate_json(reputation_users)

        return None

    async def set_reputation_users_by_detail(
        self,
        detail: str,
        reputation_users: List[entities.ReputationUserWithRelationsEntity],
    ) -> None:
        await self.set(
            keys.get_reputation_user_by_detail_key(detail),
            ReputationUsersAdapter.dump_json(reputation_users),
            expire=self.reputation_user_details_ttl,
        )

    async def get_reputation_users_by_search(
        self, search: str
    ) -> List[entities.ReputationUserWithRelationsEntity] | None:
        if search.isdigit() and len(search) >= 9:
            reputation_user = await self.get_reputation_user_by_telegram_id(int(search))

            if reputation_user:
                return [reputation_user]
        elif re.match(r"^@[a-zA-Z0-9_]+$", search):
            reputation_users = await self.get_reputation_users_by_username(
                search.replace("@", "").lower()
            )

            if reputation_users:
                return reputation_users
        else:
            return await self.get_reputation_users_by_detail(search)

    async def set_reputation_users_by_search(
        self,
        search: str,
        reputation_users: List[entities.ReputationUserWithRelationsEntity],
    ) -> None:
        if search.isdigit():
            if reputation_users:
                return await self.set_reputation_user_by_telegram_id(
                    int(search), reputation_users[0]
                )
        elif re.match(r"^@[a-zA-Z0-9_]+$", search):
            if reputation_users:
                return await self.set_reputation_users_by_username(
                    search.replace("@", "").lower(), reputation_users
                )
        else:
            await self.set_reputation_users_by_detail(search, reputation_users)

    async def invalidate_user(self, user: entities.UserEntity) -> None:
        await self.delete(*keys.get_user_keys(user))

    async def invalidate_reputation_user(self, reputation_user_id: int) -> None:
        await self.delete(keys.get_reputation_user_key(reputation_user_id))

    async def set_auth(self, hash: str, user: entities.UserEntity) -> None:
        await self.set(
            keys.get_auth_key(hash),
            user.model_dump_json(),
            expire=self.auth_ttl,
        )

    async def get_auth(self, hash: str) -> entities.UserEntity | None:
        user = await self.get(keys.get_auth_key(hash))

        if user:
            return entities.UserEntity.model_validate_json(user)
