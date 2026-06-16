from domain.objects.types import UserReputationRole
from typing import Optional, List
from .base import BaseDTO


class CreateUserDetailDTO(BaseDTO):
    name: str
    value: str
    is_public: bool


class CreateReputationUserDTO(BaseDTO):
    user_ids: List[int]
    amount: Optional[float] = None
    description: Optional[str] = None
    added_by_user_id: int
    role: UserReputationRole
    details: List[CreateUserDetailDTO]
    scam_report_ids: List[int]


class UpdateUserDetailDTO(BaseDTO):
    id: Optional[int] = None
    name: str
    value: str
    is_public: bool


class UpdateReputationUserDTO(BaseDTO):
    version: int
    added_by_user_id: int
    user_ids: Optional[List[int]] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    about: Optional[str] = None
    role: Optional[UserReputationRole] = None
    details: Optional[List[UpdateUserDetailDTO]] = None
    scam_report_ids: Optional[List[int]] = None


class UpdateMarketplaceUserDTO(BaseDTO):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_id: Optional[int] = None
