from typing import Optional, List
from datetime import datetime

from domain.objects.types import (
    ID,
    Name,
    Rating,
    Reason,
    IDSet,
    NoNegativeFloat,
    ReportStatus,
    TelegramID,
    Username,
    NoNegativeInt,
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
    added_by_user_id: int


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
    id: int
    telegram_id: int
    usernames: List[UsernameResponse]
    role: UserRole
    reputation_user_id: Optional[int] = None


class UserWithMarketplaceUserResponse(BaseResponse):
    id: int
    telegram_id: int
    usernames: List[UsernameResponse]
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


class ReputationUserWithUsersResponse(ReputationUserResponse):
    id: int
    description: Optional[str] = None
    about: Optional[str] = None
    amount: float
    version: int
    search_count: int
    applied_report_count: int
    review_count: int
    users: List[UserResponse]
    role: UserReputationRole


class UserDetailResponse(BaseResponse):
    id: int
    name: str
    value: str
    is_public: bool


class ScamReportResponse(BaseResponse):
    id: int
    description: Optional[str] = None
    contact_info: Optional[str] = None
    attachments: List[str]
    comment: Optional[str] = None
    status: ReportStatus
    user_id: int
    accused_reputation_user_id: Optional[int] = None
    applied_by_user_id: Optional[int] = None


class ReputationUserWithRelationsResponse(ReputationUserResponse):
    users: List[UserResponse]
    user_details: List[UserDetailResponse]
    added_by_user: UserResponse
    accused_reports: List[ScamReportResponse]


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
    amount: Optional[NoNegativeFloat] = None
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
    version: NoNegativeInt
    user_ids: Optional[IDSet] = None
    amount: Optional[NoNegativeFloat] = None
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
