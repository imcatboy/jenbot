from __future__ import annotations

from datetime import datetime

from objects.types import UserReputationRole, UserRole
from .base import BaseEntity


class UserEntity(BaseEntity):
    telegram_id: int
    username: str
    balance: int
    experience: int
    message_count: int
    joined_at: datetime
    role: UserRole
    is_active: bool
    last_activity_at: datetime


class UserReputationEntity(BaseEntity):
    description: str
    role: UserReputationRole
    user_id: int
    added_by_user_id: int


class UserReputationWithUserEntity(UserReputationEntity):
    user: UserEntity
    added_by_user: UserEntity


class FeedbackEntity(BaseEntity):
    message: str
    is_read: bool
    user_id: int
