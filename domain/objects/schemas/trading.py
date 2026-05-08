from datetime import datetime
from typing import Optional

from domain.objects.types import DealType, DealStatus, DealCondition, ID, NoZeroInt
from .base import BaseRequest, BaseResponse


class BuyAdvertisementOptionRequest(BaseRequest):
    advertisement_option_id: ID
    count: NoZeroInt
    option_price_id: Optional[ID] = None
    trade_id: Optional[ID] = None
    with_agent: Optional[bool] = None


class UpdateDealConditionRequest(BaseRequest):
    condition: DealCondition


class DealResponse(BaseResponse):
    id: int
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
