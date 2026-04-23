from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, String
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from objects.types import TransactionType
from .base import EntityModel

if TYPE_CHECKING:
    from .user import UserModel
    from .trading import DealModel


class TransactionModel(EntityModel):
    __tablename__ = "transactions"
    fk_name = "transaction_id"

    amount: Mapped[int]
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="TRANSACTION_TYPE"),
    )
    description: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
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

    is_used: Mapped[bool]
    expires_at: Mapped[Optional[datetime]]
    price: Mapped[int]
    product_id: Mapped[int] = mapped_column(ForeignKey("chat_products.id"))
    product: Mapped[ChatProductModel] = relationship(back_populates="purchases")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(
        back_populates="purchases", foreign_keys=[user_id]
    )


class ReviewModel(EntityModel):
    __tablename__ = "reviews"
    fk_name = "review_id"

    message: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column("review")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    for_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id"))
    author: Mapped[UserModel] = relationship(
        foreign_keys=[user_id],
        back_populates="reviews_written",
    )
    subject: Mapped[UserModel] = relationship(
        foreign_keys=[for_user_id],
        back_populates="reviews_received",
    )
    deal: Mapped[DealModel] = relationship(
        back_populates="reviews", foreign_keys=[deal_id]
    )
