from typing import List, Optional

from domain.objects import UserRole
from .base import BaseResponse


class MarketplaceUserResponse(BaseResponse):
    name: Optional[str]
    description: Optional[str]
    rating: float
    advertisement_count: int
    deals_count: int
    reviews_count: int


class UserResponse(BaseResponse):
    telegram_id: int
    username: Optional[str]
    role: UserRole
    marketplace_user: Optional[MarketplaceUserResponse]


class ParentCategoryResponse(BaseResponse):
    id: int
    name: str


class CategoryResponse(BaseResponse):
    id: int
    name: str
    parent_category: Optional[ParentCategoryResponse]


class ProductResponse(BaseResponse):
    id: int
    name: str
    image_urls: List[str]
    category: CategoryResponse


class AdvertisementResponse(BaseResponse):
    id: int
    user: UserResponse
    product: ProductResponse


class CurrencyResponse(BaseResponse):
    id: int
    name: str
    sign: str
    description: Optional[str]


class TradeResponse(BaseResponse):
    id: int


class ProductOptionResponse(BaseResponse):
    id: int
    name: str


class AdvertisementOptionPriceResponse(BaseResponse):
    id: int
    amount: float
    currency: CurrencyResponse


class AdvertisementOptionResponse(BaseResponse):
    id: int
    count: int
    advertisement: AdvertisementResponse
    prices: List[AdvertisementOptionPriceResponse]
    product_options: List[ProductOptionResponse]
    trades: List[TradeResponse]


class UserShortResponse(BaseResponse):
    telegram_id: int
    username: Optional[str]
    name: Optional[str]
    rating: float


class AdvertisementOptionShortResponse(BaseResponse):
    id: int
    name: str
    category_path: str
    has_trades: bool
    user: UserShortResponse
    options: List[str]
    prices: List[str]


class CatalogResponse(BaseResponse):
    items: List[AdvertisementOptionShortResponse]
    has_more: bool