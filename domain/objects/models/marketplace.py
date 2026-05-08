from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional

from .associate_tables import (
    advertisement_options_product_options,
    product_types_products,
    trade_deals_product_options,
    trades_product_options,
    deals_product_options,
)
from .base import EntityModel

if TYPE_CHECKING:
    from .user import UserModel
    from .messaging import FileModel
    from .trading import TradeModel, DealModel
    from .marketplace import AdvertisementOptionPriceModel, AdvertisementOptionModel


class CategoryModel(EntityModel):
    __tablename__ = "categories"
    fk_name = "category_id"

    name: Mapped[str] = mapped_column(String(100), index=True)
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_category_id: Mapped[Optional[int]] = mapped_column(
        "parent_category", ForeignKey("categories.id"), index=True
    )
    parent_category: Mapped[Optional[CategoryModel]] = relationship(
        back_populates="categories",
        remote_side=lambda: CategoryModel.id,
    )
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)
    author: Mapped[Optional[UserModel]] = relationship(back_populates="categories")
    categories: Mapped[List[CategoryModel]] = relationship(
        back_populates="parent_category"
    )
    products: Mapped[List[ProductModel]] = relationship(back_populates="category")


class ProductModel(EntityModel):
    __tablename__ = "products"
    fk_name = "product_id"
    __table_args__ = (Index("ix_products_category_id", "category_id", "is_draft"),)

    name: Mapped[str] = mapped_column(String(100), index=True)
    images: Mapped[List[FileModel]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    category: Mapped[CategoryModel] = relationship(back_populates="products")
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)
    author: Mapped[Optional[UserModel]] = relationship(back_populates="products")
    product_types: Mapped[List[ProductTypeModel]] = relationship(
        secondary=product_types_products,
        back_populates="products",
    )
    advertisements: Mapped[List[AdvertisementModel]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    trades: Mapped[List[TradeModel]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    deals: Mapped[List[DealModel]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        foreign_keys="DealModel.product_id",
    )
    trade_deals: Mapped[List[DealModel]] = relationship(
        back_populates="trade_product",
        cascade="all, delete-orphan",
        foreign_keys="DealModel.trade_product_id",
    )


class ProductTypeModel(EntityModel):
    __tablename__ = "product_types"
    fk_name = "product_type_id"

    name: Mapped[str] = mapped_column(String(255), index=True)
    can_many: Mapped[bool] = mapped_column(Boolean)
    products: Mapped[List[ProductModel]] = relationship(
        secondary=product_types_products,
        back_populates="product_types",
    )
    options: Mapped[List[ProductOptionModel]] = relationship(
        back_populates="product_type",
        cascade="all, delete-orphan",
    )


class ProductOptionModel(EntityModel):
    __tablename__ = "product_options"
    fk_name = "product_option_id"

    name: Mapped[str] = mapped_column(String(100), index=True)
    product_type_id: Mapped[int] = mapped_column(
        ForeignKey("product_types.id"), index=True
    )
    product_type: Mapped[ProductTypeModel] = relationship(back_populates="options")
    advertisement_options: Mapped[List[AdvertisementOptionModel]] = relationship(
        secondary=advertisement_options_product_options,
        back_populates="product_options",
    )
    trades: Mapped[List[TradeModel]] = relationship(
        secondary=trades_product_options,
        back_populates="product_options",
    )
    deals: Mapped[List[DealModel]] = relationship(
        secondary=deals_product_options,
        back_populates="product_options",
    )
    trade_deals: Mapped[List[DealModel]] = relationship(
        secondary=trade_deals_product_options,
        back_populates="trade_product_options",
    )


class CurrencyModel(EntityModel):
    __tablename__ = "currencies"
    fk_name = "currency_id"

    name: Mapped[str] = mapped_column(String(50), index=True)
    sign: Mapped[str] = mapped_column(String(5))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    option_prices: Mapped[List[AdvertisementOptionPriceModel]] = relationship(
        back_populates="currency",
        cascade="all, delete-orphan",
    )
    deals: Mapped[List[DealModel]] = relationship(
        back_populates="currency",
        cascade="all, delete-orphan",
    )


class AdvertisementModel(EntityModel):
    __tablename__ = "advertisements"
    fk_name = "advertisement_id"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped[UserModel] = relationship(
        back_populates="advertisements", foreign_keys=[user_id]
    )
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)
    pays_for_agent: Mapped[bool] = mapped_column(default=False)
    ready_to_bargain: Mapped[bool] = mapped_column(default=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    product: Mapped[ProductModel] = relationship(back_populates="advertisements")
    options: Mapped[List[AdvertisementOptionModel]] = relationship(
        back_populates="advertisement",
        cascade="all, delete-orphan",
    )


class AdvertisementOptionModel(EntityModel):
    __tablename__ = "advertisement_options"
    fk_name = "advertisement_option_id"
    __table_args__ = (
        CheckConstraint(
            "count >= 0",
            name="ck_advertisement_option_count_positive",
        ),
        CheckConstraint(
            "sold_count >= 0",
            name="ck_advertisement_option_sold_count_positive",
        ),
    )

    count: Mapped[int]
    sold_count: Mapped[int] = mapped_column(default=0)
    advertisement_id: Mapped[int] = mapped_column(
        ForeignKey("advertisements.id"), index=True
    )
    advertisement: Mapped[AdvertisementModel] = relationship(back_populates="options")
    prices: Mapped[List[AdvertisementOptionPriceModel]] = relationship(
        back_populates="advertisement_option",
        cascade="all, delete-orphan",
    )
    product_options: Mapped[List[ProductOptionModel]] = relationship(
        secondary=advertisement_options_product_options,
        back_populates="advertisement_options",
    )
    trades: Mapped[List[TradeModel]] = relationship(
        back_populates="advertisement_option",
        cascade="all, delete-orphan",
    )
    deals: Mapped[List[DealModel]] = relationship(
        back_populates="advertisement_option",
        cascade="all, delete-orphan",
    )


class AdvertisementOptionPriceModel(EntityModel):
    __tablename__ = "advertisement_option_prices"
    fk_name = "advertisement_option_price_id"
    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_advertisement_option_price_amount_positive",
        ),
    )

    amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id"), index=True)
    advertisement_option_id: Mapped[int] = mapped_column(
        ForeignKey("advertisement_options.id"), index=True
    )
    currency: Mapped[CurrencyModel] = relationship(back_populates="option_prices")
    advertisement_option: Mapped[AdvertisementOptionModel] = relationship(
        back_populates="prices"
    )
    deals: Mapped[List[DealModel]] = relationship(
        back_populates="advertisement_option_price",
        cascade="all, delete-orphan",
    )
