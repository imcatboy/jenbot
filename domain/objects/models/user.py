from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, String, BigInteger
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from objects.types import UserReputationRole, UserRole
from .base import EntityModel, BaseModel, MetadataModel

if TYPE_CHECKING:
    from .moderation import ChatViolationModel, ReportModel
    from .economy import TransactionModel, ChatPurchaseModel


class UserModel(EntityModel):
    __tablename__ = "users"
    fk_name = "user_id"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(32), unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    user_reputation: Mapped[UserReputationModel] = relationship(
        back_populates="user",
        foreign_keys="UserReputationModel.user_id",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    chat_user: Mapped[ChatUserModel] = relationship(
        back_populates="user",
        foreign_keys="ChatUserModel.user_id",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    marketplace_user: Mapped[MarketplaceUserModel] = relationship(
        back_populates="user",
        foreign_keys="MarketplaceUserModel.user_id",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    violations: Mapped[List[ChatViolationModel]] = relationship(
        back_populates="user",
        foreign_keys="ChatViolationModel.user_id",
        cascade="all, delete-orphan",
    )
    applied_violations: Mapped[List[ChatViolationModel]] = relationship(
        back_populates="applied_by_user",
        foreign_keys="ChatViolationModel.applied_by_user_id",
        cascade="all, delete-orphan",
    )
    added_reputations: Mapped[List[UserReputationModel]] = relationship(
        back_populates="added_by_user",
        foreign_keys="UserReputationModel.added_by_user_id",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[List[TransactionModel]] = relationship(
        back_populates="user",
        foreign_keys="TransactionModel.user_id",
        cascade="all, delete-orphan",
    )
    purchases: Mapped[List[ChatPurchaseModel]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    received_transactions: Mapped[List[TransactionModel]] = relationship(
        back_populates="receiver",
        foreign_keys="TransactionModel.receiver_id",
    )
    reports: Mapped[List[ReportModel]] = relationship(
        back_populates="user",
        foreign_keys="ReportModel.user_id",
        cascade="all, delete-orphan",
    )
    applied_reports: Mapped[List[ReportModel]] = relationship(
        back_populates="applied_by_user",
        foreign_keys="ReportModel.applied_by_user_id",
        cascade="all, delete-orphan",
    )
    accused_reports: Mapped[List[ReportModel]] = relationship(
        back_populates="accused_user",
        foreign_keys="ReportModel.accused_user_id",
        cascade="all, delete-orphan",
    )


class UserReputationModel(BaseModel, MetadataModel):
    __tablename__ = "user_reputations"
    fk_name = "user_reputation_id"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserReputationRole] = mapped_column(Enum(UserReputationRole))
    added_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    added_by_user: Mapped[UserModel] = relationship(
        back_populates="added_reputations",
        foreign_keys=[added_by_user_id],
    )
    user: Mapped[UserModel] = relationship(
        back_populates="user_reputation",
        foreign_keys=[user_id],
    )


class ChatUserModel(BaseModel, MetadataModel):
    __tablename__ = "chat_users"
    fk_name = "chat_user_id"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    balance: Mapped[int] = mapped_column(default=0)
    experience: Mapped[int] = mapped_column(default=0)
    message_count: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_activity_at: Mapped[datetime] = mapped_column(default=datetime.now)
    user: Mapped[UserModel] = relationship(
        back_populates="chat_user",
        foreign_keys=[user_id],
    )


class MarketplaceUserModel(BaseModel, MetadataModel):
    __tablename__ = "marketplace_users"
    fk_name = "marketplace_user_id"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(32))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    rating: Mapped[float] = mapped_column(default=0)
    user: Mapped[UserModel] = relationship(
        back_populates="marketplace_user",
        foreign_keys=[user_id],
    )