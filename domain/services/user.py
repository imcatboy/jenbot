from typing import List, Optional

from domain.repositories import UserRepository, MediaRepository
from domain.objects import entities, exceptions, dtos
from domain.objects.types import UserReputationRole, UserRole
from domain.cache import UserCache


class UserService:

    def __init__(
        self,
        user_repository: UserRepository,
        user_cache: UserCache,
        media_repository: MediaRepository,
    ) -> None:
        self.user_repository = user_repository
        self.user_cache = user_cache
        self.media_repository = media_repository

    async def create(
        self, telegram_id: int, usernames: List[str]
    ) -> entities.UserEntity:
        user_id = await self.user_repository.create(telegram_id, usernames)
        user = await self.get_by_id(user_id)
        await self.user_cache.set_user(user)
        return user

    async def update(
        self,
        id: int,
        telegram_id: Optional[int] = None,
        usernames: Optional[List[str]] = None,
    ) -> entities.UserEntity:
        user = await self.get_by_id(id)

        if user.role != UserRole.USER:
            raise exceptions.UserNotAllowedToUpdateException(user.id)

        await self.user_repository.update(id, telegram_id, usernames)
        user = await self.get_by_id(id)
        await self.user_cache.set_user(user)
        return user

    async def get_or_create(
        self, telegram_id: int, usernames: List[str]
    ) -> entities.UserEntity:
        user = await self.user_cache.get_user_by_telegram_id(telegram_id)

        if user:
            return user

        user = await self.user_repository.get_or_create(telegram_id, usernames)
        await self.user_cache.set_user(user)
        return user

    async def get_by_id(self, id: int) -> entities.UserEntity:
        user = await self.user_cache.get_user_by_id(id)

        if user:
            return user

        user = await self.user_repository.get(id)
        await self.user_cache.set_user(user)
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> entities.UserEntity:
        user = await self.user_cache.get_user_by_telegram_id(telegram_id)

        if user:
            return user

        user = await self.user_repository.get_by_telegram_id(telegram_id)
        await self.user_cache.set_user(user)
        return user

    async def get_by_username(self, username: str) -> entities.UserEntity:
        return await self.user_repository.get_by_username(username)

    async def update_role(self, id: int, role: UserRole) -> None:
        await self.user_repository.update_role(id, role)
        user = await self.get_by_id(id)
        await self.user_cache.invalidate_user(user)

    async def get_by_role(self, role: UserRole) -> List[entities.UserEntity]:
        return await self.user_repository.get_by_role(role)

    async def get_many(self, dto: dtos.GetDTO) -> List[entities.UserEntity]:
        return await self.user_repository.get_many(dto)

    async def create_reputation_user(
        self, dto: dtos.CreateReputationUserDTO
    ) -> entities.ReputationUserEntity:
        added_by_user = await self.get_by_id(dto.added_by_user_id)

        if added_by_user.role != UserRole.ADMIN and (
            dto.amount is not None
            or dto.role
            not in [UserReputationRole.SCAMMER, UserReputationRole.CLEAN_USER]
        ):
            raise exceptions.UserNotAllowedToSetReputationUserException(
                added_by_user.id
            )

        user_reputation = await self.user_repository.create_reputation_user(dto)
        await self.user_cache.set_reputation_user(user_reputation)
        return user_reputation

    async def update_reputation_user(
        self, user_id: int, dto: dtos.UpdateReputationUserDTO
    ) -> entities.ReputationUserEntity:
        added_by_user = await self.get_by_id(dto.added_by_user_id)

        if added_by_user.role != UserRole.ADMIN and (
            dto.amount is not None
            or dto.role
            not in [UserReputationRole.SCAMMER, UserReputationRole.CLEAN_USER]
        ):
            raise exceptions.UserNotAllowedToSetReputationUserException(
                added_by_user.id
            )

        user_reputation = await self.user_repository.update_reputation_user(
            user_id, dto
        )
        await self.user_cache.set_reputation_user(user_reputation)
        return user_reputation

    async def get_reputation_user_by_user_id(
        self, user_id: int
    ) -> entities.ReputationUserWithRelationsEntity:
        user_reputation = await self.user_cache.get_reputation_user_by_user_id(user_id)

        if user_reputation:
            return user_reputation

        user_reputation = await self.user_repository.get_reputation_user_by_user_id(
            user_id
        )
        await self.user_cache.set_reputation_user_by_user_id(user_id, user_reputation)
        return user_reputation

    async def get_reputation_users(
        self, search: str
    ) -> List[entities.ReputationUserWithRelationsEntity]:
        user_reputations = await self.user_cache.get_reputation_users_by_search(search)

        if user_reputations:
            reputation_user_ids = [
                user_reputation.id for user_reputation in user_reputations
            ]
            await self.user_repository.add_search_count(reputation_user_ids)
            return user_reputations

        user_reputations = await self.user_repository.get_reputation_users(search)
        reputation_user_ids = [
            user_reputation.id for user_reputation in user_reputations
        ]
        await self.user_repository.add_search_count(reputation_user_ids)
        await self.user_cache.set_reputation_users_by_search(search, user_reputations)
        return user_reputations

    async def get_reputation_user(
        self, id: int
    ) -> entities.ReputationUserWithRelationsEntity:
        user_reputation = await self.user_cache.get_reputation_user(id)

        if user_reputation:
            return user_reputation

        user_reputation = await self.user_repository.get_reputation_user(id)
        await self.user_cache.set_reputation_user(user_reputation)
        return user_reputation

    async def create_or_update_reputation_user(
        self, dto: dtos.CreateReputationUserDTO
    ) -> entities.ReputationUserEntity:
        try:
            await self.get_reputation_user_by_user_id(dto.user_id)
        except exceptions.ObjectNotFoundException:
            return await self.create_reputation_user(dto)

        return await self.update_reputation_user(dto.user_id, dto)

    async def get_or_create_marketplace_user(
        self, user_id: int
    ) -> entities.UserWithMarketplaceUserEntity:
        user = await self.user_cache.get_marketplace_user(user_id)

        if user:
            return user

        user = await self.user_repository.get_or_create_marketplace_user(user_id)
        await self.user_cache.set_marketplace_user(user_id, user)
        return user

    async def get_profile(self, user_id: int) -> entities.ProfileEntity:
        profile = await self.user_cache.get_profile(user_id)

        if profile:
            return profile

        profile = await self.user_repository.get_profile(user_id)
        await self.user_cache.set_profile(user_id, profile)
        return profile

    async def get_auth(self, hash: str) -> entities.UserEntity | None:
        return await self.user_cache.get_auth(hash)

    async def set_auth(self, hash: str, user: entities.UserEntity) -> None:
        await self.user_cache.set_auth(hash, user)

    async def update_marketplace_user(
        self, user_id: int, dto: dtos.UpdateMarketplaceUserDTO
    ) -> entities.MarketplaceUserEntity:
        marketplace_user = await self.user_repository.update_marketplace_user(
            user_id, dto
        )
        user = await self.get_by_id(user_id)
        await self.user_cache.invalidate_user(user)
        return marketplace_user

    async def get_avatar(self, user_id: int) -> entities.FileEntity:
        user = await self.get_or_create_marketplace_user(user_id)

        if not user.marketplace_user or not user.marketplace_user.avatar_id:
            raise exceptions.ObjectNotFoundException("FileModel", user_id=user_id)

        return await self.media_repository.get_file(user.marketplace_user.avatar_id)
