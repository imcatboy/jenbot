from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, String, BigInteger, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from objects.types import ViolationType, ReportType, ReportStatus
from .base import EntityModel

if TYPE_CHECKING:
    from .user import UserModel


class ChatViolationModel(EntityModel):
    __tablename__ = "chat_violations"
    fk_name = "chat_violation_id"

    reason: Mapped[str] = mapped_column(String(255))
    type: Mapped[ViolationType] = mapped_column(Enum(ViolationType))
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(default=True)
    expires_at: Mapped[Optional[datetime]]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(
        back_populates="violations",
        foreign_keys=[user_id],
    )
    applied_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    applied_by_user: Mapped[UserModel] = relationship(
        back_populates="applied_violations",
        foreign_keys=[applied_by_user_id],
    )


class ReportModel(EntityModel):
    __tablename__ = "reports"
    fk_name = "report_id"

    reason: Mapped[str] = mapped_column(String(1024))
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.PENDING)
    attachments: Mapped[List[str]] = mapped_column(ARRAY(String(255)))
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType))
    admin_comment: Mapped[Optional[str]] = mapped_column(String(1024))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(
        back_populates="reports",
        foreign_keys=[user_id],
    )
    accused_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    accused_user: Mapped[Optional[UserModel]] = relationship(
        back_populates="accused_reports",
        foreign_keys=[accused_user_id],
    )
    applied_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    applied_by_user: Mapped[Optional[UserModel]] = relationship(
        back_populates="applied_reports",
        foreign_keys=[applied_by_user_id],
    )