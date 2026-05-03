from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING


from .base import EntityWithMetadata

if TYPE_CHECKING:
    from .messaging import FileEntity
    from .trading import TradeWithRelations, TradeEntity
    from .user import UserWithMarketplaceUserEntity


class CategoryEntity(EntityWithMetadata):
    name: str
    parent_category_id: Optional[int] = None
    is_draft: bool


class CategoryWithParentEntity(CategoryEntity):
    parent_category: Optional[CategoryEntity] = None


class ProductEntity(EntityWithMetadata):
    name: str
    is_draft: bool
    category_id: int


class ProductEntityWithRelations(ProductEntity):
    product_types: List[ProductTypeWithOptionsEntity]
    category: CategoryWithParentEntity
    images: List[FileEntity]


class ProductWithCategoryEntity(ProductEntity):
    category: CategoryWithParentEntity


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


class AdvertisementOptionPriceWithCurrency(AdvertisementOptionPriceEntity):
    currency: CurrencyEntity


class AdvertisementOptionWithRelations(AdvertisementOptionEntity):
    prices: List[AdvertisementOptionPriceWithCurrency]
    trades: List[TradeWithRelations]
    product_options: List[ProductOptionEntity]


class AdvertisementEntityWithOptions(AdvertisementEntity):
    options: List[AdvertisementOptionWithRelations]
    product: ProductEntityWithRelations
    user: UserWithMarketplaceUserEntity


class AdvertisementEntityWithRelations(AdvertisementEntity):
    product: ProductWithCategoryEntity
    user: UserWithMarketplaceUserEntity


class AdvertisementOptionEntityWithAdvertisement(AdvertisementOptionEntity):
    advertisement: AdvertisementEntityWithRelations
    prices: List[AdvertisementOptionPriceWithCurrency]
    trades: List[TradeEntity]
    product_options: List[ProductOptionEntity]