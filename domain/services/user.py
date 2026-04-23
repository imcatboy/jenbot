from typing import List

from objects import entities, exceptions, dtos
from domain.repositories import UserRepository
from domain.objects.types import UserRole


class UserService:

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def get_or_create(
        self, telegram_id: int, username: str
    ) -> entities.UserEntity:
        return await self.user_repository.get_or_create(telegram_id, username)
    
    async def get_by_id(self, id: int) -> entities.UserEntity:
        return await self.user_repository.get(id)

    async def get_by_telegram_id(self, telegram_id: int) -> entities.UserEntity:
        return await self.user_repository.get_by_telegram_id(telegram_id)

    async def get_by_username(self, username: str) -> entities.UserEntity:
        return await self.user_repository.get_by_username(username)

    async def update_role(self, id: int, role: UserRole) -> None:
        return await self.user_repository.update_role(id, role)
    
    async def get_by_role(self, role: UserRole) -> List[entities.UserEntity]:
        return await self.user_repository.get_by_role(role)
    
    async def create_user_reputation(self, dto: dtos.CreateUserReputationDTO) -> entities.UserReputationEntity:
        return await self.user_repository.create_user_reputation(dto)
    
    async def update_user_reputation(self, user_id: int, dto: dtos.UpdateUserReputationDTO) -> None:
        return await self.user_repository.update_user_reputation(user_id, dto)
    
    async def get_user_reputation(self, user_id: int) -> entities.UserReputationWithUserEntity:
        return await self.user_repository.get_user_reputation(user_id)
    
    async def create_or_update_user_reputation(self, dto: dtos.CreateUserReputationDTO) -> entities.UserReputationEntity:
        try:
            await self.get_user_reputation(dto.user_id)
        except exceptions.ObjectNotFoundException:
            return await self.create_user_reputation(dto)
        
        return await self.update_user_reputation(dto.user_id, dto)