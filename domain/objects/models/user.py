from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, String, BigInteger
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from objects.types import UserReputationRole, UserRole
from .base import EntityModel, BaseModel, MetadataModel

if TYPE_CHECKING:
    from .moderation import ChatViolationModel, ViolationModel, ReportModel
    from .economy import TransactionModel, ChatPurchaseModel, ReviewModel
    from .marketplace import AdvertisementModel
    from .trading import DealModel
    from .messaging import ChatModel, ChatParticipantModel, MessageModel, MessageFileModel


class UserModel(EntityModel):
    __tablename__ = "users"
    fk_name = "user_id"

    telegram_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="USER_ROLE"))
    user_reputation: Mapped[Optional[UserReputationModel]] = relationship(
        back_populates="user",
        foreign_keys="UserReputationModel.user_id",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    chat_user: Mapped[Optional[ChatUserModel]] = relationship(
        back_populates="user",
        foreign_keys="ChatUserModel.user_id",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    marketplace_user: Mapped[Optional[MarketplaceUserModel]] = relationship(
        back_populates="user",
        foreign_keys="MarketplaceUserModel.user_id",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    violations: Mapped[List[ViolationModel]] = relationship(
        back_populates="user",
        foreign_keys="ViolationModel.user_id",
        cascade="all, delete-orphan",
    )
    chat_violations: Mapped[List[ChatViolationModel]] = relationship(
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
        back_populates="user",
        foreign_keys="ChatPurchaseModel.user_id",
        cascade="all, delete-orphan",
    )
    received_transactions: Mapped[List[TransactionModel]] = relationship(
        back_populates="receiver",
        foreign_keys="TransactionModel.receiver_id",
        cascade="all, delete-orphan",
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
    advertisements: Mapped[List[AdvertisementModel]] = relationship(
        back_populates="user",
        foreign_keys="AdvertisementModel.user_id",
        cascade="all, delete-orphan",
    )
    buyer_deals: Mapped[List[DealModel]] = relationship(
        foreign_keys="DealModel.user_id",
        back_populates="buyer",
    )
    seller_deals: Mapped[List[DealModel]] = relationship(
        foreign_keys="DealModel.seller_id",
        back_populates="seller",
    )
    agent_deals: Mapped[List[DealModel]] = relationship(
        foreign_keys="DealModel.agent_id",
        back_populates="agent",
    )
    reviews_written: Mapped[List[ReviewModel]] = relationship(
        foreign_keys="ReviewModel.user_id",
        back_populates="author",
    )
    reviews_received: Mapped[List[ReviewModel]] = relationship(
        foreign_keys="ReviewModel.for_user_id",
        back_populates="subject",
    )
    chat_participants: Mapped[List[ChatParticipantModel]] = relationship(
        back_populates="user",
        foreign_keys="ChatParticipantModel.user_id",
        cascade="all, delete-orphan",
    )
    authored_chats: Mapped[List[ChatModel]] = relationship(
        back_populates="author",
        foreign_keys="ChatModel.author_id",
    )
    messages: Mapped[List[MessageModel]] = relationship(
        back_populates="user",
        foreign_keys="MessageModel.user_id",
        cascade="all, delete-orphan",
    )
    files: Mapped[List[MessageFileModel]] = relationship(
        back_populates="user",
        foreign_keys="MessageFileModel.user_id",
        cascade="all, delete-orphan",
    )



class UserReputationModel(BaseModel, MetadataModel):
    __tablename__ = "reputation_users"
    fk_name = "user_reputation_id"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserReputationRole] = mapped_column(
        Enum(UserReputationRole, name="REPUTATION_ROLE"),
    )
    added_by_user_id: Mapped[int] = mapped_column(
        "added_by_user",
        ForeignKey("users.id"),
    )
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
    balance: Mapped[int]
    experience: Mapped[int]
    message_count: Mapped[int]
    is_active: Mapped[bool]
    last_activity_at: Mapped[datetime]
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
    rating: Mapped[float]
    user: Mapped[UserModel] = relationship(
        back_populates="marketplace_user",
        foreign_keys=[user_id],
    )
