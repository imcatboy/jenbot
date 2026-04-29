from typing import Dict, List, Optional, Set

from .base import BaseRequest, BaseResponse
from domain.objects.types import ID, NoZeroFloat, NoZeroInt


class MarketplaceUserResponse(BaseResponse):
    name: Optional[str]
    username: Optional[str]
    rating: float
    avatar_url: Optional[str]
    advertisement_count: int
    review_count: int
    deal_count: int


class ProductOptionResponse(BaseResponse):
    id: int
    name: str


class ProductTypeResponse(BaseResponse):
    id: int
    name: str
    can_many: bool
    options: List[ProductOptionResponse]


class AdvertisementOptionPriceResponse(BaseResponse):
    id: int
    amount: float
    currency_sign: str


class ProductResponse(BaseResponse):
    id: int
    name: str
    image_url: str
    category_path: str


class TradeResponse(BaseResponse):
    id: int
    count: int
    product: ProductResponse
    product_options: List[ProductOptionResponse]


class AdvertisementOptionResponse(BaseResponse):
    id: int
    count: int
    prices: List[AdvertisementOptionPriceResponse]
    product_options: List[ProductOptionResponse]
    trades: List[TradeResponse]


class AdvertisementResponse(BaseResponse):
    id: int
    name: str
    category_path: str
    user: MarketplaceUserResponse
    product_types: List[ProductTypeResponse]
    options: Dict[str, AdvertisementOptionResponse]


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


class AdvertisementShortResponse(BaseResponse):
    id: int
    name: str
    category_path: str
    image_url: str


class AdvertisementsResponse(BaseResponse):
    items: List[AdvertisementShortResponse]
    has_more: bool


class BuyAdvertisementRequest(BaseRequest):
    advertisement_option_id: ID
    count: NoZeroInt
    option_price_id: Optional[ID] = None
    trade_id: Optional[ID] = None


class CreateAdvertisementOptionPriceRequest(BaseRequest):
    amount: NoZeroFloat
    currency_id: ID


class CreateTradeRequest(BaseRequest):
    product_id: ID
    product_option_ids: Set[ID]
    count: NoZeroInt


class CreateAdvertisementOptionRequest(BaseRequest):
    product_option_ids: Set[ID]
    count: NoZeroInt
    prices: List[CreateAdvertisementOptionPriceRequest]
    trades: List[CreateTradeRequest]


class CreateAdvertisementRequest(BaseRequest):
    product_id: ID
    options: List[CreateAdvertisementOptionRequest]


class UpdateAdvertisementOptionPriceRequest(BaseRequest):
    id: Optional[ID] = None
    amount: NoZeroFloat
    currency_id: ID


class UpdateTradeRequest(BaseRequest):
    id: Optional[ID] = None
    count: NoZeroInt
    product_option_ids: Set[ID]


class UpdateAdvertisementOptionRequest(BaseRequest):
    id: Optional[ID] = None
    count: NoZeroInt
    product_option_ids: Set[ID]
    prices: List[UpdateAdvertisementOptionPriceRequest]
    trades: List[UpdateTradeRequest]