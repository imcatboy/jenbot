from aiogram.filters import BaseFilter
from aiogram.types import Message
from typing import List

from domain.objects.types import UserRole
from domain.objects import entities


class UsersFilter(BaseFilter):
    def __init__(self, user_roles: List[UserRole]) -> None:
        self.user_roles = user_roles

    async def __call__(
        self, message: Message, user: entities.UserEntity | None = None
    ) -> bool:
        if user is None:
            return False

        return user.role in self.user_roles
