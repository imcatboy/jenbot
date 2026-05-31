from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from domain.objects.types import ViolationType, ReportStatus, ReportType
from .base import EntityWithMetadata
from .user import UserEntity


class ChatViolationEntity(EntityWithMetadata):
    reason: str
    type: ViolationType
    telegram_chat_id: Optional[int] = None
    is_active: bool
    expires_at: Optional[datetime] = None
    user_id: int
    applied_by_user_id: int


class ChatViolationWithUserEntity(ChatViolationEntity):
    user: UserEntity
    applied_by_user: UserEntity


class ViolationEntity(EntityWithMetadata):
    name: str
    expires_at: Optional[datetime] = None
    user_id: int


class ViolationWithUserEntity(ViolationEntity):
    user: UserEntity


class ReportEntity(EntityWithMetadata):
    reason: str
    status: ReportStatus
    attachments: List[str]
    type: ReportType
    admin_comment: Optional[str] = None
    user_id: int
    accused_user_id: Optional[int] = None
    applied_by_user_id: Optional[int] = None


class ReportWithUserEntity(ReportEntity):
    user: UserEntity
    accused_user: Optional[UserEntity] = None
    applied_by_user: Optional[UserEntity] = None


class TrackerEntity(EntityWithMetadata):
    expires_at: Optional[datetime] = None
    is_active: bool
    tracked_user_id: int
    tracking_user_id: int


class TrackerWithUserEntity(TrackerEntity):
    tracked_user: UserEntity
    tracking_user: UserEntity


class TelegramFileEntity(EntityWithMetadata):
    name: str
    file_id: str