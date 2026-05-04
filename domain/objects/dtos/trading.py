from typing import Optional, List
from datetime import datetime

from .base import BaseDTO
from domain.objects.types import DealCondition, DealStatus, DealType


class BuyAdvertisementOptionDTO(BaseDTO):
    user_id: int
    advertisement_option_id: int
    count: int
    option_price_id: Optional[int] = None
    trade_id: Optional[int] = None
    with_agent: Optional[bool] = None


class CreateDealDTO(BaseDTO):
    advertisement_option_id: int
    deal_type: DealType
    count: int
    expires_at: datetime
    product_id: int
    product_option_ids: List[int]
    seller_id: int
    agent_id: Optional[int] = None
    user_id: int
    option_price_id: Optional[int] = None
    amount: Optional[float] = None
    currency_id: Optional[int] = None
    trade_count: Optional[int] = None
    trade_id: Optional[int] = None
    trade_product_id: Optional[int] = None
    trade_product_option_ids: Optional[List[int]] = None


class UpdateDealDTO(BaseDTO):
    status: Optional[DealStatus] = None
    seller_condition: Optional[DealCondition] = None
    buyer_condition: Optional[DealCondition] = None


class GetDealsDTO(BaseDTO):
    user_id: int
    buyer_id: Optional[int] = None
    seller_id: Optional[int] = None
    agent_id: Optional[int] = None
    expires_at: Optional[datetime] = None
    status: Optional[DealStatus] = None
    product_id: Optional[int] = None
