from __future__ import annotations

from typing import Optional, List
from datetime import datetime

from objects.types import ViolationType, ReportStatus, ReportType
from .base import BaseEntity
from .user import UserEntity


class ViolationEntity(BaseEntity):
    reason: str
    type: ViolationType
    telegram_chat_id: int
    is_active: bool
    expires_at: Optional[datetime] = None
    user_id: int
    applied_by_user_id: int


class ViolationWithUserEntity(ViolationEntity):
    user: UserEntity
    applied_by_user: UserEntity


class ReportEntity(BaseEntity):
    reason: str
    status: ReportStatus
    attachments: List[str]
    report_type: ReportType
    admin_comment: Optional[str] = None
    user_id: int
    accused_user_id: Optional[int] = None
    applied_by_user_id: Optional[int] = None


class ReportWithUserEntity(ReportEntity):
    user: UserEntity
    accused_user: Optional[UserEntity] = None
    applied_by_user: Optional[UserEntity] = None