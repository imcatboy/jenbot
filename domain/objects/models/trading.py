from __future__ import annotations

from sqlalchemy import (
    ARRAY,
    BigInteger,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

from .associate_tables import (
    deals_product_options,
    trade_deals_product_options,
    trades_product_options,
)
from domain.objects.types import DealCondition, DealStatus, DealType, ReportStatus
from .base import EntityModel

if TYPE_CHECKING:
    from .marketplace import AdvertisementOptionPriceModel, CurrencyModel, ProductModel
    from .marketplace import AdvertisementOptionModel, ProductOptionModel
    from .user import UserModel, ReputationUserModel
    from .economy import ReviewModel
    from .messaging import ChatModel


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
        CheckConstraint(
            "expires_at > created_at",
            name="ck_deals_expires_at_in_future",
        ),
        CheckConstraint(
            "seller_id != buyer_id AND seller_id != agent_id AND buyer_id != agent_id",
            name="ck_deals_seller_and_buyer_and_agent_different",
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
    chats: Mapped[List[ChatModel]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )


class ExternalDealModel(EntityModel):
    __tablename__ = "external_deals"
    fk_name = "external_deal_id"
    __table_args__ = (
        CheckConstraint(
            "deal_amount > 0",
            name="ck_external_deals_deal_amount_positive",
        ),
        CheckConstraint(
            "refund_amount > 0",
            name="ck_external_deals_refund_amount_positive",
        ),
        CheckConstraint(
            "deal_amount >= refund_amount",
            name="ck_external_deals_deal_amount_greater_than_refund_amount",
        ),
        CheckConstraint(
            "expires_at > created_at",
            name="ck_external_deals_expires_at_in_future",
        ),
        Index(
            "ix_external_deals_agent_id_status",
            "agent_id",
            postgresql_where="status IN ('PENDING', 'EXPIRED', 'REJECTED')",
        ),
        CheckConstraint(
            "seller_id != buyer_id AND seller_id != agent_id AND buyer_id != agent_id",
            name="ck_external_deals_seller_and_buyer_and_agent_different",
        ),
    )

    deal_amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    refund_amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    payment: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(index=True)
    status: Mapped[DealStatus] = mapped_column(
        Enum(DealStatus, name="DEAL_STATUS"), default=DealStatus.DRAFT, index=True
    )
    seller_condition: Mapped[Optional[DealCondition]] = mapped_column(
        Enum(DealCondition, name="DEAL_CONDITION"), index=True
    )
    buyer_condition: Mapped[Optional[DealCondition]] = mapped_column(
        Enum(DealCondition, name="DEAL_CONDITION"), index=True
    )
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    seller: Mapped[UserModel] = relationship(
        back_populates="external_seller_deals", foreign_keys=[seller_id]
    )
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    buyer: Mapped[UserModel] = relationship(
        back_populates="external_buyer_deals", foreign_keys=[buyer_id]
    )
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)
    agent: Mapped[Optional[UserModel]] = relationship(
        back_populates="external_agent_deals", foreign_keys=[agent_id]
    )
    warranty_reputation_user_id: Mapped[int] = mapped_column(
        ForeignKey("reputation_users.id"), index=True
    )
    warranty_reputation_user: Mapped[ReputationUserModel] = relationship(
        back_populates="warranty_external_deals",
        foreign_keys=[warranty_reputation_user_id],
    )
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_by_user: Mapped[UserModel] = relationship(
        back_populates="created_external_deals", foreign_keys=[created_by_user_id]
    )
    notifications: Mapped[List[ExternalDealNotificationModel]] = relationship(
        back_populates="external_deal", cascade="all, delete-orphan"
    )


class ExternalDealNotificationModel(EntityModel):
    __tablename__ = "external_deal_notifications"
    fk_name = "external_deal_notification_id"
    __table_args__ = (
        Index(
            "ix_external_deal_notifications_external_deal_id_user_id",
            "external_deal_id",
            "user_id",
            unique=True,
        ),
    )

    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    telegram_message_id: Mapped[int] = mapped_column(BigInteger, index=True)
    external_deal_id: Mapped[int] = mapped_column(
        ForeignKey("external_deals.id"), index=True
    )
    external_deal: Mapped[ExternalDealModel] = relationship(
        back_populates="notifications"
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped[UserModel] = relationship(back_populates="external_deal_notifications")


class ScamReportModel(EntityModel):
    __tablename__ = "scam_reports"
    fk_name = "scam_report_id"

    description: Mapped[str] = mapped_column(String(1024))
    contact_info: Mapped[Optional[str]] = mapped_column(String(255))
    attachments: Mapped[List[str]] = mapped_column(ARRAY(String(255)))
    comment: Mapped[Optional[str]] = mapped_column(String(1024))
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="REPORT_STATUS"),
        default=ReportStatus.PENDING,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped[UserModel] = relationship(
        back_populates="scam_reports", foreign_keys=[user_id]
    )
    accused_reputation_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("reputation_users.id"), index=True
    )
    accused_reputation_user: Mapped[Optional[ReputationUserModel]] = relationship(
        back_populates="accused_reports",
        foreign_keys=[accused_reputation_user_id],
    )
    applied_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    applied_by_user: Mapped[Optional[UserModel]] = relationship(
        back_populates="applied_scam_reports",
        foreign_keys=[applied_by_user_id],
    )
