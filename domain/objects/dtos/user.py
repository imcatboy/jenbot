from domain.objects.types import UserReputationRole
from typing import Optional, List
from .base import BaseDTO


class CreateUserDetailDTO(BaseDTO):
    name: str
    value: str
    is_public: bool


class CreateReputationUserDTO(BaseDTO):
    user_ids: List[int]
    description: Optional[str] = None
    about: Optional[str] = None
    added_by_user_id: int
    role: UserReputationRole
    details: List[CreateUserDetailDTO]


class UpdateUserDetailDTO(BaseDTO):
    id: Optional[int] = None
    name: str
    value: str
    is_public: bool


class UpdateReputationUserDTO(BaseDTO):
    user_ids: List[int]
    description: Optional[str] = None
    about: Optional[str] = None
    role: Optional[UserReputationRole] = None
    added_by_user_id: Optional[int] = None
    details: List[UpdateUserDetailDTO]


class UpdateMarketplaceUserDTO(BaseDTO):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_id: Optional[int] = None
