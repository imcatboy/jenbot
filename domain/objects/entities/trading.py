from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from domain.objects.types import DealCondition, DealType, DealStatus
from .base import BaseEntity, EntityWithMetadata

if TYPE_CHECKING:
    from .marketplace import ProductWithImagesEntity, ProductOptionEntity


class TradeProductOptionEntity(BaseEntity):
    trade_id: int
    product_option_id: int


class TradeEntity(EntityWithMetadata):
    count: int
    advertisement_option_id: int
    product_id: int


class TradeWithRelations(TradeEntity):
    product_options: List[ProductOptionEntity]
    product: ProductWithImagesEntity


class DealEntity(EntityWithMetadata):
    count: int
    deal_type: DealType
    amount: Optional[float] = None
    expires_at: datetime
    status: DealStatus
    trade_id: Optional[int] = None
    advertisement_option_id: int
    user_id: int
    seller_id: int
    product_id: int
    seller_condition: Optional[DealCondition] = None
    buyer_condition: Optional[DealCondition] = None
    agent_id: Optional[int] = None
    advertisement_option_price_id: Optional[int] = None
    amount: Optional[float] = None
    trade_count: Optional[int] = None
    trade_product_id: Optional[int] = None
    currency_id: Optional[int] = None
