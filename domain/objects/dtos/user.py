from domain.objects.types import UserReputationRole
from typing import Optional
from .base import BaseDTO


class CreateUserReputationDTO(BaseDTO):
    user_id: int
    description: str
    added_by_user_id: int
    role: UserReputationRole


class UpdateUserReputationDTO(BaseDTO):
    description: Optional[str] = None
    role: Optional[UserReputationRole] = None
    added_by_user_id: Optional[int] = None


class UpdateMarketplaceUserDTO(BaseDTO):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_id: Optional[int] = None