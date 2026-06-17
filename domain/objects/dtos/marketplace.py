from typing import Dict, List, Optional

from domain.objects.types import SortType, SuggestionType
from domain.objects import entities
from .base import BaseDTO, GetDTO


class CreateAdvertisementOptionPriceDTO(BaseDTO):
    currency_id: int
    amount: float


class CreateAdvertisementTradeDTO(BaseDTO):
    product_id: int
    product_option_ids: List[int]
    count: int


class CreateAdvertisementOptionDTO(BaseDTO):
    product_option_ids: List[int]
    count: int
    prices: List[CreateAdvertisementOptionPriceDTO]
    trades: List[CreateAdvertisementTradeDTO]


class CreateAdvertisementDTO(BaseDTO):
    product_id: int
    user_id: int
    options: List[CreateAdvertisementOptionDTO]


class UpdateAdvertisementTradeDTO(BaseDTO):
    id: Optional[int] = None
    product_id: int
    product_option_ids: List[int]
    count: int


class UpdateAdvertisementOptionPriceDTO(BaseDTO):
    id: Optional[int] = None
    currency_id: int
    amount: float


class UpdateAdvertisementOptionDTO(BaseDTO):
    id: Optional[int] = None
    product_option_ids: List[int]
    count: int
    prices: List[UpdateAdvertisementOptionPriceDTO]
    trades: List[UpdateAdvertisementTradeDTO]


class UpdateAdvertisementDTO(BaseDTO):
    user_id: int
    is_draft: bool
    options: List[UpdateAdvertisementOptionDTO]


class SellerDTO(BaseDTO):
    name: Optional[str]
    usernames: List[str]
    rating: float
    avatar_id: Optional[int] = None
    advertisement_count: int
    review_count: int
    deal_count: int


class AdvertisementOptionPriceDTO(BaseDTO):
    id: int
    amount: float
    currency_sign: str


class ProductDTO(BaseDTO):
    id: int
    name: str
    images: List[entities.FileEntity]
    category_path: str


class TradeDTO(BaseDTO):
    id: int
    count: int
    product: ProductDTO
    product_options: List[entities.ProductOptionEntity]


class AdvertisementOptionDTO(BaseDTO):
    id: int
    count: int
    prices: List[AdvertisementOptionPriceDTO]
    product_options: List[entities.ProductOptionEntity]
    trades: List[TradeDTO]


class AdvertisementDTO(BaseDTO):
    id: int
    name: str
    category_path: str
    user: SellerDTO
    product_types: List[entities.ProductTypeWithOptionsEntity]
    options: Dict[str, AdvertisementOptionDTO]


class GetCatalogDTO(GetDTO):
    sort_type: SortType
    category_ids: Optional[List[int]] = None
    product_ids: Optional[List[int]] = None
    seller_ids: Optional[List[int]] = None
    product_option_ids: Optional[List[int]] = None
    min_count: Optional[int] = None
    high_rating: Optional[bool] = None


class AdvertisementsDTO(BaseDTO):
    items: List[AdvertisementDTO]
    has_more: bool


class AdvertisementOptionShortDTO(BaseDTO):
    id: int
    name: str
    category_path: str
    has_trades: bool
    image_url: str
    user: SellerDTO
    options: List[str]
    prices: List[str]


class CatalogDTO(BaseDTO):
    items: List[AdvertisementOptionShortDTO]
    has_more: bool


class GetAdvertisementSuggestionsDTO(GetDTO):
    category_ids: Optional[List[int]] = None
    product_ids: Optional[List[int]] = None
    seller_ids: Optional[List[int]] = None
    product_option_ids: Optional[List[int]] = None


class AdvertisementSuggestionDTO(BaseDTO):
    id: int
    kind: SuggestionType
    title: str