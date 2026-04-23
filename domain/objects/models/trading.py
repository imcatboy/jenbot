from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from objects.types import DealStatus
from .base import BaseModel, EntityModel
from .marketplace import AdvertisementOptionModel, ProductOptionModel

if TYPE_CHECKING:
    from .marketplace import AdvertisementOptionPriceModel
    from .economy import ReviewModel
    from .messaging import ChatModel
    from .user import UserModel


class TradeModel(EntityModel):
    __tablename__ = "trades"
    fk_name = "trade_id"

    advertisement_option_id: Mapped[int] = mapped_column(
        ForeignKey("advertisement_options.id")
    )
    advertisement_option: Mapped[AdvertisementOptionModel] = relationship(
        back_populates="trades",
    )
    product_options: Mapped[List[TradeProductOptionModel]] = relationship(
        back_populates="trade",
        cascade="all, delete-orphan",
    )
    deals: Mapped[List[DealModel]] = relationship(
        back_populates="trade",
        cascade="all, delete-orphan",
    )


class TradeProductOptionModel(BaseModel):
    __tablename__ = "trades_product_options"
    __table_args__ = (PrimaryKeyConstraint("trade_id", "product_option_id"),)
    fk_name = "trade_id"

    count: Mapped[int]
    trade_id: Mapped[int] = mapped_column(ForeignKey("trades.id"), primary_key=True)
    trade: Mapped[TradeModel] = relationship(back_populates="product_options")
    product_option_id: Mapped[int] = mapped_column(
        ForeignKey("product_options.id"), primary_key=True
    )
    product_option: Mapped[ProductOptionModel] = relationship(
        back_populates="trade_product_options"
    )


class DealModel(EntityModel):
    __tablename__ = "deals"
    fk_name = "deal_id"

    count: Mapped[int]
    expires_at: Mapped[datetime]
    status: Mapped[DealStatus] = mapped_column(Enum(DealStatus, name="DEAL_STATUS"))
    trade_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trades.id"))
    advertisement_option_id: Mapped[int] = mapped_column(
        ForeignKey("advertisement_options.id")
    )
    advertisement_option: Mapped[AdvertisementOptionModel] = relationship(
        back_populates="deals",
    )
    trade: Mapped[Optional[TradeModel]] = relationship(
        back_populates="deals",
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    buyer: Mapped[UserModel] = relationship(
        back_populates="buyer_deals", foreign_keys=[user_id]
    )
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    seller: Mapped[UserModel] = relationship(
        back_populates="seller_deals", foreign_keys=[seller_id]
    )
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    agent: Mapped[Optional[UserModel]] = relationship(
        back_populates="agent_deals", foreign_keys=[agent_id]
    )
    advertisement_option_price_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("advertisement_option_prices.id")
    )
    advertisement_option_price: Mapped[Optional[AdvertisementOptionPriceModel]] = relationship(
        back_populates="deals",
    )
    reviews: Mapped[List[ReviewModel]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )
    chats: Mapped[List[ChatModel]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )
