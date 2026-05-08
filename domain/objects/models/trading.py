from __future__ import annotations

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

from .associate_tables import (
    deals_product_options,
    trade_deals_product_options,
    trades_product_options,
)
from domain.objects.types import DealCondition, DealStatus, DealType
from .base import EntityModel

if TYPE_CHECKING:
    from .marketplace import AdvertisementOptionPriceModel, CurrencyModel, ProductModel
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
        back_populates="trades",
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
        CheckConstraint(
            """
            (deal_type = 'money' AND amount IS NOT NULL AND currency_id IS NOT NULL
             AND amount > 0 AND trade_product_id IS NULL AND trade_count IS NULL)
            OR
            (deal_type = 'trade' AND trade_product_id IS NOT NULL
             AND trade_count IS NOT NULL AND trade_count >= 1
             AND amount IS NULL AND currency_id IS NULL)
            """,
            name="ck_deal_type_matches_money_or_trade_snapshot",
        ),
        Index("ix_deals_status_expires_at", "status", "expires_at"),
    )

    count: Mapped[int]
    deal_type: Mapped[DealType] = mapped_column(
        Enum(DealType, name="DEAL_TYPE"),
        index=True,
    )
    amount: Mapped[Optional[float]] = mapped_column(Numeric(precision=10, scale=2))
    trade_count: Mapped[Optional[int]]
    expires_at: Mapped[datetime]
    status: Mapped[DealStatus] = mapped_column(
        Enum(DealStatus, name="DEAL_STATUS"), default=DealStatus.PENDING, index=True
    )
    seller_condition: Mapped[Optional[DealCondition]] = mapped_column(
        Enum(DealCondition, name="DEAL_CONDITION"), index=True
    )
    buyer_condition: Mapped[Optional[DealCondition]] = mapped_column(
        Enum(DealCondition, name="DEAL_CONDITION"), index=True
    )
    seller_acceptance: Mapped[bool] = mapped_column(default=False)
    buyer_acceptance: Mapped[bool] = mapped_column(default=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    product: Mapped[ProductModel] = relationship(
        back_populates="deals",
        foreign_keys=[product_id],
    )
    advertisement_option_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("advertisement_options.id"), index=True
    )
    advertisement_option: Mapped[Optional[AdvertisementOptionModel]] = relationship(
        back_populates="deals",
    )
    trade_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trades.id"), index=True)
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
    currency_id: Mapped[Optional[int]] = mapped_column(ForeignKey("currencies.id"))
    currency: Mapped[Optional[CurrencyModel]] = relationship(
        back_populates="deals",
    )
    trade_product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"))
    trade_product: Mapped[Optional[ProductModel]] = relationship(
        back_populates="trade_deals",
        foreign_keys=[trade_product_id],
    )
    product_options: Mapped[List[ProductOptionModel]] = relationship(
        secondary=deals_product_options,
        back_populates="deals",
    )
    trade_product_options: Mapped[List[ProductOptionModel]] = relationship(
        secondary=trade_deals_product_options,
        back_populates="trade_deals",
    )
    reviews: Mapped[List[ReviewModel]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )
    chats: Mapped[List[ChatModel]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )
