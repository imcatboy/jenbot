from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ARRAY, Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .associate_tables import (
    advertisement_options_product_options,
    product_types_products,
)
from .base import EntityModel

if TYPE_CHECKING:
    from .user import UserModel
    from .trading import TradeModel, DealModel, TradeProductOptionModel
    from .marketplace import AdvertisementOptionPriceModel, AdvertisementOptionModel


class CategoryModel(EntityModel):
    __tablename__ = "categories"
    fk_name = "category_id"

    name: Mapped[str] = mapped_column(String(100))
    parent_category_id: Mapped[Optional[int]] = mapped_column(
        "parent_category", ForeignKey("categories.id")
    )
    products: Mapped[list[ProductModel]] = relationship(
        back_populates="category"
    )


class ProductModel(EntityModel):
    __tablename__ = "products"
    fk_name = "product_id"

    name: Mapped[str] = mapped_column(String(100))
    images: Mapped[list[str]] = mapped_column(ARRAY(String(100)))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped[CategoryModel] = relationship(back_populates="products")
    product_types: Mapped[list[ProductTypeModel]] = relationship(
        secondary=product_types_products,
        back_populates="products",
    )
    advertisements: Mapped[list[AdvertisementModel]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )


class ProductTypeModel(EntityModel):
    __tablename__ = "product_types"
    fk_name = "product_type_id"

    name: Mapped[str] = mapped_column(String(255))
    can_many: Mapped[bool] = mapped_column(Boolean)
    products: Mapped[list[ProductModel]] = relationship(
        secondary=product_types_products,
        back_populates="product_types",
    )
    options: Mapped[list[ProductOptionModel]] = relationship(
        back_populates="product_type",
        cascade="all, delete-orphan",
    )


class ProductOptionModel(EntityModel):
    __tablename__ = "product_options"
    fk_name = "product_option_id"

    name: Mapped[str] = mapped_column(String(100))
    product_type_id: Mapped[int] = mapped_column(ForeignKey("product_types.id"))
    product_type: Mapped[ProductTypeModel] = relationship(
        back_populates="options"
    )
    advertisement_options: Mapped[list[AdvertisementOptionModel]] = relationship(
        secondary=advertisement_options_product_options,
        back_populates="product_options",
    )
    trade_product_options: Mapped[list[TradeProductOptionModel]] = relationship(
        back_populates="product_option",
        cascade="all, delete-orphan",
    )


class CurrencyModel(EntityModel):
    __tablename__ = "currencies"
    fk_name = "currency_id"

    name: Mapped[str] = mapped_column(String(50))
    sign: Mapped[str] = mapped_column(String(5))
    description: Mapped[str | None] = mapped_column(String(255))
    option_prices: Mapped[list[AdvertisementOptionPriceModel]] = relationship(
        back_populates="currency",
        cascade="all, delete-orphan",
    )


class AdvertisementModel(EntityModel):
    __tablename__ = "advertisements"
    fk_name = "advertisement_id"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    user: Mapped[UserModel] = relationship(
        back_populates="advertisements", foreign_keys=[user_id]
    )
    product: Mapped[ProductModel] = relationship(
        back_populates="advertisements"
    )
    options: Mapped[list[AdvertisementOptionModel]] = relationship(
        back_populates="advertisement",
        cascade="all, delete-orphan",
    )


class AdvertisementOptionModel(EntityModel):
    __tablename__ = "advertisement_options"
    fk_name = "advertisement_option_id"

    option_count: Mapped[int] = mapped_column("count")
    advertisement_id: Mapped[int] = mapped_column(ForeignKey("advertisements.id"))
    advertisement: Mapped[AdvertisementModel] = relationship(
        back_populates="options"
    )
    prices: Mapped[list[AdvertisementOptionPriceModel]] = relationship(
        back_populates="advertisement_option",
        cascade="all, delete-orphan",
    )
    product_options: Mapped[list[ProductOptionModel]] = relationship(
        secondary=advertisement_options_product_options,
        back_populates="advertisement_options",
    )
    trades: Mapped[list["TradeModel"]] = relationship(
        back_populates="advertisement_option",
        cascade="all, delete-orphan",
    )
    deals: Mapped[list["DealModel"]] = relationship(
        back_populates="advertisement_option",
        cascade="all, delete-orphan",
    )


class AdvertisementOptionPriceModel(EntityModel):
    __tablename__ = "advertisement_option_prices"
    fk_name = "advertisement_option_price_id"

    amount: Mapped[Decimal] = mapped_column(Numeric)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id"))
    advertisement_option_id: Mapped[int] = mapped_column(
        ForeignKey("advertisement_options.id")
    )
    currency: Mapped[CurrencyModel] = relationship(back_populates="option_prices")
    advertisement_option: Mapped[AdvertisementOptionModel] = relationship(
        back_populates="prices"
    )
    deals: Mapped[list["DealModel"]] = relationship(
        back_populates="advertisement_option_price",
        cascade="all, delete-orphan",
    )
