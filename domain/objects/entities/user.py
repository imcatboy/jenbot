from __future__ import annotations

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from domain.objects.types import UserReputationRole, UserRole
from .base import EntityWithMetadata, MetadataEntity

if TYPE_CHECKING:
    from .moderation import ViolationEntity


class UsernameEntity(EntityWithMetadata):
    username: str
    user_id: int


class UserEntity(EntityWithMetadata):
    telegram_id: int
    usernames: List[UsernameEntity]
    reputation_user_id: Optional[int] = None
    role: UserRole


class ReputationUserEntity(EntityWithMetadata):
    description: Optional[str] = None
    about: Optional[str] = None
    amount: float
    search_count: int
    applied_report_count: int
    review_count: int
    role: UserReputationRole
    added_by_user_id: int


class UserDetailEntity(EntityWithMetadata):
    name: str
    value: str
    is_public: bool
    reputation_user_id: int


class ReputationUserWithRelationsEntity(ReputationUserEntity):
    users: List[UserEntity]
    user_details: List[UserDetailEntity]
    added_by_user: UserEntity


class ChatUserEntity(MetadataEntity):
    user_id: int
    balance: int
    experience: int
    message_count: int
    is_active: bool
    last_activity_at: datetime


class ChatUserWithUserEntity(ChatUserEntity):
    user: UserEntity


class MarketplaceUserEntity(MetadataEntity):
    user_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_id: Optional[int] = None
    rating: float
    advertisement_count: int
    deal_count: int
    review_count: int


class MarketplaceUserWithUserEntity(MarketplaceUserEntity):
    user: UserEntity


class UserWithMarketplaceUserEntity(UserEntity):
    marketplace_user: Optional[MarketplaceUserEntity] = None


class ProfileEntity(UserEntity):
    violations: List[ViolationEntity]
    reputation_user: Optional[ReputationUserEntity]
    marketplace_user: Optional[MarketplaceUserEntity]
