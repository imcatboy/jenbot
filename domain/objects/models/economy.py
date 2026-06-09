from __future__ import annotations

from sqlalchemy import (
    Enum,
    ForeignKey,
    String,
    CheckConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from domain.objects.types import TransactionType
from .base import EntityModel

if TYPE_CHECKING:
    from .user import UserModel, ReputationUserModel
    from .trading import DealModel, ExternalDealModel


class TransactionModel(EntityModel):
    __tablename__ = "transactions"
    fk_name = "transaction_id"
    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_transaction_amount_positive",
        ),
    )

    amount: Mapped[int]
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="TRANSACTION_TYPE"),
    )
    description: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped[UserModel] = relationship(
        back_populates="transactions",
        foreign_keys=[user_id],
    )
    receiver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    receiver: Mapped[Optional[UserModel]] = relationship(
        back_populates="received_transactions",
        foreign_keys=[receiver_id],
    )


class ChatProductModel(EntityModel):
    __tablename__ = "chat_products"
    fk_name = "chat_product_id"
    __table_args__ = (
        CheckConstraint(
            "price > 0",
            name="ck_chat_product_price_positive",
        ),
    )

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    price: Mapped[int]
    is_active: Mapped[bool]
    purchases: Mapped[List[ChatPurchaseModel]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )


class ChatPurchaseModel(EntityModel):
    __tablename__ = "chat_purchases"
    fk_name = "chat_purchase_id"
    __table_args__ = (
        CheckConstraint(
            "price > 0",
            name="ck_chat_purchase_price_positive",
        ),
    )
    is_used: Mapped[bool]
    expires_at: Mapped[Optional[datetime]] = mapped_column(index=True)
    price: Mapped[int]
    product_id: Mapped[int] = mapped_column(ForeignKey("chat_products.id"))
    product: Mapped[ChatProductModel] = relationship(back_populates="purchases")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped[UserModel] = relationship(
        back_populates="purchases", foreign_keys=[user_id]
    )


class ReviewModel(EntityModel):
    __tablename__ = "reviews"
    fk_name = "review_id"
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 and rating <= 5",
            name="ck_rating_range",
        ),
        CheckConstraint(
            "deal_id is null or external_deal_id is null",
            name="ck_review_deal_or_external_deal_not_null",
        ),
        UniqueConstraint(
            "author_id",
            "subject_user_id",
            name="uq_reviews_author_id_subject_user_id",
        ),
        UniqueConstraint(
            "author_id",
            "subject_reputation_user_id",
            name="uq_reviews_author_id_subject_reputation_user_id",
        ),
    )
    message: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    author: Mapped[UserModel] = relationship(
        foreign_keys=[author_id],
        back_populates="reviews_written",
    )
    subject_reputation_user_id: Mapped[int] = mapped_column(
        ForeignKey("reputation_users.id"), index=True
    )
    subject_reputation_user: Mapped[ReputationUserModel] = relationship(
        foreign_keys=[subject_reputation_user_id],
        back_populates="reviews_received",
    )
    subject_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    subject_user: Mapped[UserModel] = relationship(
        foreign_keys=[subject_user_id],
        back_populates="reviews_received",
    )
    deal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("deals.id"), index=True)
    deal: Mapped[Optional[DealModel]] = relationship(
        back_populates="reviews", foreign_keys=[deal_id]
    )
    external_deal_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("external_deals.id"), index=True
    )
    external_deal: Mapped[Optional[ExternalDealModel]] = relationship(
        back_populates="reviews", foreign_keys=[external_deal_id]
    )
