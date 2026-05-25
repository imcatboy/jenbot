from datetime import datetime
from typing import Optional, List

from domain.objects.types import ViolationType, ReportStatus, ReportType, ChatAction
from .base import BaseDTO


class AddViolationDTO(BaseDTO):
    user_id: int
    reason: str
    type: ViolationType
    applied_by_user_id: int
    telegram_chat_id: Optional[int] = None
    expires_at: Optional[datetime] = None


class BanUserDTO(BaseDTO):
    user_id: int
    reason: str
    applied_by_user_id: int
    telegram_chat_id: int
    expires_at: Optional[datetime] = None


class GlobalBanUserDTO(BaseDTO):
    user_id: int
    reason: str
    applied_by_user_id: int
    expires_at: Optional[datetime] = None


class MuteUserDTO(BaseDTO):
    user_id: int
    reason: str
    applied_by_user_id: int
    telegram_chat_id: int
    expires_at: Optional[datetime] = None


class WarnUserDTO(BaseDTO):
    user_id: int
    reason: str
    applied_by_user_id: int
    telegram_chat_id: int
    expires_at: Optional[datetime] = None


class AddReportDTO(BaseDTO):
    reason: str
    attachments: List[str]
    type: ReportType
    user_id: int
    accused_user_id: Optional[int] = None


class UpdateReportDTO(BaseDTO):
    status: Optional[ReportStatus] = None
    admin_comment: Optional[str] = None
    applied_by_user_id: Optional[int] = None


class GetReportsDTO(BaseDTO):
    user_id: Optional[int] = None
    status: Optional[ReportStatus] = None
    type: Optional[ReportType] = None
    accused_user_id: Optional[int] = None


class GetUserReportDTO(BaseDTO):
    report_id: int
    status: ReportStatus
    type: ReportType


class GetViolationsDTO(BaseDTO):
    user_id: Optional[int] = None
    applied_by_user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int
    offset: int