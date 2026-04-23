from typing import Optional, List
from datetime import datetime

from domain.objects import UserRole, UserReputationRole, ViolationType
from .base import BaseResponse


class MarketplaceUserResponse(BaseResponse):
    name: Optional[str]
    description: Optional[str]
    rating: float


class ReputationUserResponse(BaseResponse):
    description: str
    role: UserReputationRole


class ViolationResponse(BaseResponse):
    id: int
    reason: str
    type: ViolationType


class ProfileResponse(BaseResponse):
    telegram_id: int
    username: Optional[str]
    role: UserRole
    review_count: int
    deal_count: int
    advertisement_count: int
    violations: List[ViolationResponse]
    reputation_user: Optional[ReputationUserResponse]
    marketplace_user: Optional[MarketplaceUserResponse]


class UserResponse(BaseResponse):
    telegram_id: int
    username: Optional[str]
    role: UserRole
    marketplace_user: Optional[MarketplaceUserResponse]


class ReviewResponse(BaseResponse):
    id: int
    message: str
    rating: int
    created_at: datetime
    author: UserResponse