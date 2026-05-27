from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    String,
    BigInteger,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from domain.objects.types import UserReputationRole, UserRole
from .base import EntityModel, BaseModel, MetadataModel

if TYPE_CHECKING:
    from .messaging import ChatModel, ChatParticipantModel, MessageModel, FileModel
    from .moderation import (
        ChatViolationModel,
        ViolationModel,
        ReportModel,
        TrackerModel,
    )
    from .economy import TransactionModel, ChatPurchaseModel, ReviewModel
    from .marketplace import AdvertisementModel, ProductModel, CategoryModel
    from .trading import DealModel


class UserModel(EntityModel):
    __tablename__ = "users"
    fk_name = "user_id"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(32), unique=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="USER_ROLE"), default=UserRole.USER, index=True
    )
    reputation_user: Mapped[Optional[ReputationUserModel]] = relationship(
        back_populates="user",
        foreign_keys="ReputationUserModel.user_id",
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
    added_reputations: Mapped[List[ReputationUserModel]] = relationship(
        back_populates="added_by_user",
        foreign_keys="ReputationUserModel.added_by_user_id",
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
        foreign_keys="ReviewModel.author_id",
        back_populates="author",
    )
    reviews_received: Mapped[List[ReviewModel]] = relationship(
        foreign_keys="ReviewModel.subject_id",
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
    files: Mapped[List[FileModel]] = relationship(
        back_populates="uploaded_by_user",
        foreign_keys="FileModel.uploaded_by_user_id",
        cascade="all, delete-orphan",
    )
    products: Mapped[List[ProductModel]] = relationship(
        back_populates="author",
        foreign_keys="ProductModel.author_id",
        cascade="all, delete-orphan",
    )
    categories: Mapped[List[CategoryModel]] = relationship(
        back_populates="author",
        foreign_keys="CategoryModel.author_id",
        cascade="all, delete-orphan",
    )
    controlled_trackers: Mapped[List[TrackerModel]] = relationship(
        back_populates="tracking_user",
        foreign_keys="TrackerModel.tracking_user_id",
        cascade="all, delete-orphan",
    )
    tracked_users: Mapped[List[TrackerModel]] = relationship(
        back_populates="tracked_user",
        foreign_keys="TrackerModel.tracked_user_id",
        cascade="all, delete-orphan",
    )


class ReputationUserModel(BaseModel, MetadataModel):
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
        back_populates="reputation_user",
        foreign_keys=[user_id],
    )


class ChatUserModel(BaseModel, MetadataModel):
    __tablename__ = "chat_users"
    fk_name = "chat_user_id"
    __table_args__ = (
        CheckConstraint(
            "experience >= 0",
            name="ck_chat_user_experience_positive",
        ),
        CheckConstraint(
            "message_count >= 0",
            name="ck_chat_user_message_count_positive",
        ),
        CheckConstraint(
            "balance >= 0",
            name="ck_chat_user_balance_positive",
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    balance: Mapped[int] = mapped_column(default=0)
    experience: Mapped[int] = mapped_column(default=0)
    message_count: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_activity_at: Mapped[datetime] = mapped_column(default=datetime.now, index=True)
    user: Mapped[UserModel] = relationship(
        back_populates="chat_user",
        foreign_keys=[user_id],
    )


class MarketplaceUserModel(BaseModel, MetadataModel):
    __tablename__ = "marketplace_users"
    fk_name = "marketplace_user_id"
    __table_args__ = (
        CheckConstraint(
            "rating >= 0.0 and rating <= 5.0",
            name="ck_marketplace_user_rating_range",
        ),
        CheckConstraint(
            "advertisement_count >= 0",
            name="ck_marketplace_user_advertisement_count_positive",
        ),
        CheckConstraint(
            "deal_count >= 0",
            name="ck_marketplace_user_deal_count_positive",
        ),
        CheckConstraint(
            "review_count >= 0",
            name="ck_marketplace_user_review_count_positive",
        ),
        Index("ix_marketplace_users_rating", "rating", "deal_count"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(32))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_id: Mapped[Optional[int]] = mapped_column(ForeignKey("files.id"))
    avatar: Mapped[Optional[FileModel]] = relationship(
        back_populates="marketplace_user",
    )
    rating: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=2), default=0.0, index=True
    )
    advertisement_count: Mapped[int] = mapped_column(default=0)
    deal_count: Mapped[int] = mapped_column(default=0)
    review_count: Mapped[int] = mapped_column(default=0)
    user: Mapped[UserModel] = relationship(
        back_populates="marketplace_user",
        foreign_keys=[user_id],
    )
