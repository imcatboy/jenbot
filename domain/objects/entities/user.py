from __future__ import annotations

from datetime import datetime
from typing import Optional

from domain.objects.types import UserReputationRole, UserRole
from .base import EntityWithMetadata, MetadataEntity


class UserEntity(EntityWithMetadata):
    telegram_id: int
    username: Optional[str]
    role: UserRole


class ReputationUserEntity(MetadataEntity):
    user_id: int
    description: str
    role: UserReputationRole
    added_by_user_id: int


class ReputationUserWithUserEntity(ReputationUserEntity):
    user: UserEntity
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
    name: Optional[str]
    description: Optional[str]
    rating: float


class MarketplaceUserWithUserEntity(MarketplaceUserEntity):
    user: UserEntity


class UserWithMarketplaceUserEntity(UserEntity):
    marketplace_user: Optional[MarketplaceUserEntity] = None