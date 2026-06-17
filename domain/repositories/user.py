import re

from sqlalchemy import cast, select, or_, update, String
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from .relations import (
    get_reputation_user_relations,
    get_profile_relations,
)
from domain.objects import models, entities, dtos, exceptions
from domain.objects.types import UserRole
from .base import BaseRepository


class UserRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, telegram_id: int, usernames: List[str]) -> int:
        await self.validator.validate_data_not_exists(
            models.UserModel, telegram_id=telegram_id
        )
        user = models.UserModel(telegram_id=telegram_id)
        self.session.add(user)
        await self.session.flush()
        await self.set_many_to_one_relation(
            user, models.UsernameModel, "username", usernames
        )
        return user.id

    async def get_or_create(
        self, telegram_id: int, usernames: List[str]
    ) -> entities.UserEntity:
        user = await self.get_one_by_data_or_none(
            models.UserModel,
            [selectinload(models.UserModel.usernames)],
            telegram_id=telegram_id,
        )

        if user:
            existing_usernames = {username.username for username in user.usernames}
            new_usernames = [
                username for username in usernames if username not in existing_usernames
            ]

            if new_usernames:
                await self.set_many_to_one_relation(
                    user,
                    models.UsernameModel,
                    "username",
                    new_usernames + list(existing_usernames),
                )
                await self.session.flush()
                await self.session.refresh(user, ["usernames"])

            return entities.UserEntity.model_validate(user)

        try:
            await self.create(telegram_id, usernames)
        except IntegrityError:
            await self.session.rollback()

        user = await self.get_one_by_data(
            models.UserModel,
            [selectinload(models.UserModel.usernames)],
            telegram_id=telegram_id,
        )
        return entities.UserEntity.model_validate(user)

    async def update(
        self,
        id: int,
        telegram_id: Optional[int] = None,
        usernames: Optional[List[str]] = None,
    ) -> None:
        user = await self.get_by_id(models.UserModel, id)

        if telegram_id is not None:
            user.telegram_id = telegram_id

        await self.set_many_to_one_relation(
            user, models.UsernameModel, "username", usernames
        )
        await self.session.flush()

    async def get_many(self, dto: dtos.GetDTO) -> List[entities.UserEntity]:
        result = await self.session.execute(
            select(models.UserModel)
            .join(models.UsernameModel, isouter=True)
            .limit(dto.limit)
            .offset(dto.offset)
            .where(
                models.UserModel.role == UserRole.USER,
                or_(
                    cast(models.UserModel.telegram_id, String).ilike(f"{dto.search}"),
                    models.UsernameModel.username.ilike(f"%{dto.search}%"),
                ),
            )
            .options(selectinload(models.UserModel.usernames))
        )
        return [
            entities.UserEntity.model_validate(user) for user in result.scalars().all()
        ]

    async def get(self, id: int) -> entities.UserEntity:
        user = await self.get_by_id(
            models.UserModel, id, [selectinload(models.UserModel.usernames)]
        )
        return entities.UserEntity.model_validate(user)

    async def get_by_telegram_id(self, telegram_id: int) -> entities.UserEntity:
        user = await self.get_one_by_data(
            models.UserModel,
            [selectinload(models.UserModel.usernames)],
            telegram_id=telegram_id,
        )
        return entities.UserEntity.model_validate(user)

    async def get_by_username(self, username: str) -> entities.UserEntity:
        result = await self.session.execute(
            select(models.UserModel)
            .join(models.UsernameModel)
            .where(models.UsernameModel.username == username)
            .options(selectinload(models.UserModel.usernames))
        )
        user = result.scalar_one_or_none()

        if not user:
            raise exceptions.ObjectNotFoundException(
                models.UserModel.__name__, [username]
            )

        return entities.UserEntity.model_validate(user)

    async def update_role(self, id: int, role: UserRole) -> None:
        user = await self.get_by_id(models.UserModel, id)
        user.role = role
        await self.session.flush()

    async def get_by_role(self, role: UserRole) -> List[entities.UserEntity]:
        users = await self.get_all_by_data(
            models.UserModel, [selectinload(models.UserModel.usernames)], role=role
        )
        return [entities.UserEntity.model_validate(user) for user in users]

    async def create_reputation_user(
        self, dto: dtos.CreateReputationUserDTO
    ) -> entities.ReputationUserEntity:
        await self.validator.validate_values_not_exists(
            models.UserDetailModel, "value", [detail.value for detail in dto.details]
        )
        reputation_user = models.ReputationUserModel(
            description=dto.description,
            role=dto.role,
            amount=dto.amount,
        )
        await self.create_relation(
            reputation_user, models.UserModel, dto.added_by_user_id, "added_by_user_id"
        )
        self.sync_children(
            reputation_user.user_details,
            dto.details,
            create=lambda detail: models.UserDetailModel(
                name=detail.name,
                value=detail.value,
                is_public=detail.is_public,
            ),
            update=lambda detail, dto: None,
        )
        self.session.add(reputation_user)
        await self.session.flush()
        await self.create_many_to_one_relation(
            reputation_user, models.UserModel, dto.user_ids
        )
        return entities.ReputationUserEntity.model_validate(reputation_user)

    async def update_reputation_user(
        self, reputation_user_id: int, dto: dtos.UpdateReputationUserDTO
    ) -> entities.ReputationUserEntity:
        reputation_user = await self.get_by_id(
            models.ReputationUserModel, reputation_user_id
        )

        if reputation_user.version != dto.version:
            raise exceptions.VersionMismatchException(
                models.ReputationUserModel.__name__,
                reputation_user_id,
                reputation_user.version,
                dto.version,
            )

        await self.validator.validate_values_not_exists(
            models.UserDetailModel,
            "value",
            [detail.value for detail in dto.details if detail.id is None],
        )

        if dto.description is not None:
            reputation_user.description = dto.description
        if dto.role is not None:
            reputation_user.role = dto.role
        if dto.about is not None:
            reputation_user.about = dto.about
        if dto.amount is not None:
            reputation_user.amount = dto.amount

        await self.update_relation(
            reputation_user, models.UserModel, dto.added_by_user_id, "added_by_user_id"
        )
        await self.update_many_to_one_relation(
            reputation_user, models.UserModel, dto.user_ids
        )
        await self.sync_many_to_one_relation(
            reputation_user, models.UserDetailModel, dto.details
        )
        reputation_user.version += 1
        await self.session.flush()
        return entities.ReputationUserEntity.model_validate(reputation_user)

    async def get_reputation_user_by_user_id(
        self, user_id: int
    ) -> entities.ReputationUserWithRelationsEntity:
        result = await self.session.execute(
            select(models.ReputationUserModel)
            .join(
                models.UserModel,
                models.UserModel.reputation_user_id == models.ReputationUserModel.id,
            )
            .where(models.UserModel.id == user_id)
            .options(*get_reputation_user_relations())
        )
        reputation_user = result.scalar_one_or_none()

        if not reputation_user:
            raise exceptions.ObjectNotFoundException(
                models.ReputationUserModel.__name__, user_id=user_id
            )

        return entities.ReputationUserWithRelationsEntity.model_validate(
            reputation_user
        )

    async def get_reputation_users(
        self, search: str
    ) -> List[entities.ReputationUserWithRelationsEntity]:
        query = (
            select(models.ReputationUserModel)
            .join(
                models.UserModel,
                models.UserModel.reputation_user_id == models.ReputationUserModel.id,
            )
            .join(models.UsernameModel, isouter=True)
            .join(models.UserDetailModel, isouter=True)
            .options(*get_reputation_user_relations())
        )
        conditions = []

        if search.isdigit():
            conditions.append(
                cast(models.UserModel.telegram_id, String).like(f"%{search}%")
            )

        if re.match(r"^@[a-zA-Z0-9_]+$", search):
            conditions.append(
                models.UsernameModel.username.ilike(
                    f"%{search.replace("@", "").lower()}%"
                )
            )
        else:
            conditions.append(models.UserDetailModel.value.ilike(f"%{search.lower()}%"))

        query = query.where(or_(*conditions))
        reputation_users = await self.session.execute(query)
        return [
            entities.ReputationUserWithRelationsEntity.model_validate(reputation_user)
            for reputation_user in reputation_users.scalars().unique().all()
        ]

    async def get_reputation_user(
        self, id: int
    ) -> entities.ReputationUserWithRelationsEntity:
        reputation_user = await self.get_by_id(
            models.ReputationUserModel, id, options=get_reputation_user_relations()
        )
        return entities.ReputationUserWithRelationsEntity.model_validate(
            reputation_user
        )

    async def add_search_count(self, reputation_user_ids: List[int]) -> None:
        await self.session.execute(
            update(models.ReputationUserModel)
            .where(models.ReputationUserModel.id.in_(reputation_user_ids))
            .values(search_count=models.ReputationUserModel.search_count + 1)
        )

    async def get_or_create_marketplace_user(
        self, user_id: int
    ) -> entities.UserWithMarketplaceUserEntity:
        user = await self.get_one_by_data_or_none(
            models.UserModel,
            id=user_id,
            options=[
                joinedload(models.UserModel.marketplace_user),
                selectinload(models.UserModel.usernames),
            ],
        )

        if user and user.marketplace_user:
            return entities.UserWithMarketplaceUserEntity.model_validate(user)

        marketplace_user = models.MarketplaceUserModel(user_id=user_id)
        self.session.add(marketplace_user)
        await self.session.flush()
        user = await self.get_by_id(
            models.UserModel,
            id=user_id,
            options=[
                joinedload(models.UserModel.marketplace_user),
                selectinload(models.UserModel.usernames),
            ],
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

        await self.set_optional_relation(
            marketplace_user, models.FileModel, dto.avatar_id, "avatar_id"
        )
        await self.session.flush()
        return entities.MarketplaceUserEntity.model_validate(marketplace_user)
