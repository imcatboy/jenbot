from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, String
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from objects.types import TransactionType
from .base import EntityModel

if TYPE_CHECKING:
    from .user import UserModel


class TransactionModel(EntityModel):
    __tablename__ = "transactions"
    fk_name = "transaction_id"

    amount: Mapped[int] = mapped_column(default=0)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
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

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    price: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    purchases: Mapped[List[ChatPurchaseModel]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ChatPurchaseModel(EntityModel):
    __tablename__ = "chat_purchases"
    fk_name = "chat_purchase_id"

    is_used: Mapped[bool] = mapped_column(default=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(default=datetime.now)
    price: Mapped[int] = mapped_column(default=0)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped[ChatProductModel] = relationship(back_populates="purchases")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(back_populates="purchases")
