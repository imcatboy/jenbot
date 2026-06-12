from typing import Optional, List
from datetime import datetime

from domain.objects.types import (
    ID,
    Name,
    Rating,
    Reason,
    IDSet,
    NoZeroFloat,
    TelegramID,
    Username,
    NoZeroInt,
)
from domain.objects import UserRole, UserReputationRole, ViolationType
from .base import BaseRequest, BaseResponse


class MarketplaceUserResponse(BaseResponse):
    name: Optional[str]
    description: Optional[str]
    rating: float
    avatar_id: Optional[ID] = None
    review_count: int
    deal_count: int
    advertisement_count: int


class ReputationUserResponse(BaseResponse):
    id: int
    description: Optional[str] = None
    about: Optional[str] = None
    amount: float
    version: int
    search_count: int
    applied_report_count: int
    review_count: int
    role: UserReputationRole


class ViolationResponse(BaseResponse):
    id: int
    reason: str
    type: ViolationType


class ProfileResponse(BaseResponse):
    telegram_id: int
    username: Optional[str]
    role: UserRole
    violations: List[ViolationResponse]
    reputation_user: Optional[ReputationUserResponse]
    marketplace_user: Optional[MarketplaceUserResponse]


class UsernameResponse(BaseResponse):
    username: str
    user_id: int


class UserResponse(BaseResponse):
    telegram_id: int
    usernames: List[UsernameResponse]
    role: UserRole
    reputation_user_id: Optional[int] = None


class UserWithMarketplaceUserResponse(BaseResponse):
    telegram_id: int
    username: Optional[str]
    role: UserRole
    marketplace_user: Optional[MarketplaceUserResponse]


class ReviewResponse(BaseResponse):
    id: int
    message: str
    rating: int
    created_at: datetime
    author: UserWithMarketplaceUserResponse


class ReviewsResponse(BaseResponse):
    items: List[ReviewResponse]
    has_more: bool


class CreateReviewRequest(BaseRequest):
    message: Reason
    rating: Rating
    deal_id: ID


class UpdateMarketplaceUserRequest(BaseRequest):
    name: Optional[Name] = None
    description: Optional[Reason] = None


class CreateUserDetailRequest(BaseRequest):
    name: Name
    value: Reason
    is_public: bool


class CreateReputationUserRequest(BaseRequest):
    user_ids: IDSet
    amount: Optional[NoZeroFloat] = None
    description: Optional[Reason] = None
    role: UserReputationRole
    details: List[CreateUserDetailRequest]
    scam_report_ids: IDSet


class UpdateUserDetailRequest(BaseRequest):
    id: Optional[ID] = None
    name: Name
    value: Reason
    is_public: bool


class UpdateReputationUserRequest(BaseRequest):
    version: NoZeroInt
    user_ids: Optional[IDSet] = None
    amount: Optional[NoZeroFloat] = None
    description: Optional[Reason] = None
    role: Optional[UserReputationRole] = None
    details: Optional[List[UpdateUserDetailRequest]] = None
    scam_report_ids: Optional[IDSet] = None


class CreateUserRequest(BaseRequest):
    telegram_id: TelegramID
    usernames: List[Username]


class UpdateUserRequest(BaseRequest):
    telegram_id: Optional[TelegramID] = None
    usernames: Optional[List[Username]] = None
