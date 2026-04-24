from __future__ import annotations

from datetime import datetime
from typing import Optional

from objects.types import DealStatus
from .base import BaseEntity, EntityWithMetadata


class TradeProductOptionEntity(BaseEntity):
    trade_id: int
    product_option_id: int


class TradeEntity(EntityWithMetadata):
    count: int
    advertisement_option_id: int
    product_id: int


class DealEntity(EntityWithMetadata):
    count: int
    expires_at: datetime
    status: DealStatus
    trade_id: Optional[int] = None
    advertisement_option_id: int
    user_id: int
    seller_id: int
    agent_id: Optional[int] = None
    advertisement_option_price_id: Optional[int] = None
