from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from .base import EntityWithMetadata


class CategoryEntity(EntityWithMetadata):
    name: str
    parent_category_id: Optional[int] = None


class ProductEntity(EntityWithMetadata):
    name: str
    images: List[str]
    category_id: int


class ProductTypeEntity(EntityWithMetadata):
    name: str
    can_many: bool


class ProductOptionEntity(EntityWithMetadata):
    name: str
    product_type_id: int


class CurrencyEntity(EntityWithMetadata):
    name: str
    sign: str
    description: Optional[str] = None


class AdvertisementEntity(EntityWithMetadata):
    user_id: int
    product_id: int


class AdvertisementOptionEntity(EntityWithMetadata):
    count: int
    sold_count: int
    advertisement_id: int


class AdvertisementOptionPriceEntity(EntityWithMetadata):
    amount: Decimal
    currency_id: int
    advertisement_option_id: int
