from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

from .associate_tables import trades_product_options
from objects.types import DealStatus
from .base import EntityModel

if TYPE_CHECKING:
    from .marketplace import AdvertisementOptionPriceModel, ProductModel
    from .marketplace import AdvertisementOptionModel, ProductOptionModel
    from .economy import ReviewModel
    from .messaging import ChatModel
    from .user import UserModel


class TradeModel(EntityModel):
    __tablename__ = "trades"
    fk_name = "trade_id"
    __table_args__ = (
        CheckConstraint(
            "count >= 1",
            name="ck_trade_count_positive",
        ),
    )

    count: Mapped[int] = mapped_column(default=1)
    advertisement_option_id: Mapped[int] = mapped_column(
        ForeignKey("advertisement_options.id"), index=True
    )
    advertisement_option: Mapped[AdvertisementOptionModel] = relationship(
        back_populates="trades",
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    product: Mapped[ProductModel] = relationship(
        back_populates="trades",
    )
    product_options: Mapped[List[ProductOptionModel]] = relationship(
        secondary=trades_product_options,
        back_populates="trade",
    )
    deals: Mapped[List[DealModel]] = relationship(
        back_populates="trade",
        cascade="all, delete-orphan",
    )


class DealModel(EntityModel):
    __tablename__ = "deals"
    fk_name = "deal_id"
    __table_args__ = (
        CheckConstraint(
            "count >= 1",
            name="ck_deal_count_positive",
        ),
        Index("ix_deals_status_expires_at", "status", "expires_at"),
    )

    count: Mapped[int]
    expires_at: Mapped[datetime]
    status: Mapped[DealStatus] = mapped_column(
        Enum(DealStatus, name="DEAL_STATUS"), index=True
    )
    trade_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trades.id"), index=True)
    advertisement_option_id: Mapped[int] = mapped_column(
        ForeignKey("advertisement_options.id"), index=True
    )
    advertisement_option: Mapped[AdvertisementOptionModel] = relationship(
        back_populates="deals",
    )
    trade: Mapped[Optional[TradeModel]] = relationship(
        back_populates="deals",
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    buyer: Mapped[UserModel] = relationship(
        back_populates="buyer_deals", foreign_keys=[user_id]
    )
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    seller: Mapped[UserModel] = relationship(
        back_populates="seller_deals", foreign_keys=[seller_id]
    )
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)
    agent: Mapped[Optional[UserModel]] = relationship(
        back_populates="agent_deals", foreign_keys=[agent_id]
    )
    advertisement_option_price_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("advertisement_option_prices.id"), index=True
    )
    advertisement_option_price: Mapped[Optional[AdvertisementOptionPriceModel]] = (
        relationship(
            back_populates="deals",
        )
    )
    reviews: Mapped[List[ReviewModel]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )
    chats: Mapped[List[ChatModel]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )
