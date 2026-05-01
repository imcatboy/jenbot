from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from .base import EntityWithMetadata

if TYPE_CHECKING:
    from .messaging import FileEntity


class CategoryEntity(EntityWithMetadata):
    name: str
    parent_category_id: Optional[int] = None
    is_draft: bool


class ProductEntity(EntityWithMetadata):
    name: str
    images: List[FileEntity]
    is_draft: bool
    category_id: int


class ProductTypeEntity(EntityWithMetadata):
    name: str
    can_many: bool


class ProductTypeWithOptionsEntity(EntityWithMetadata):
    name: str
    can_many: bool
    options: List[ProductOptionEntity]


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
    is_draft: bool


class AdvertisementOptionEntity(EntityWithMetadata):
    count: int
    sold_count: int
    advertisement_id: int


class AdvertisementOptionPriceEntity(EntityWithMetadata):
    amount: float
    currency_id: int
    advertisement_option_id: int
