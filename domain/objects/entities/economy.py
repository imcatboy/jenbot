from __future__ import annotations

from typing import Optional
from datetime import datetime

from domain.objects.types import TransactionType
from .base import EntityWithMetadata


class TransactionEntity(EntityWithMetadata):
    amount: int
    type: TransactionType
    description: str
    user_id: int
    receiver_id: Optional[int] = None


class ChatProductEntity(EntityWithMetadata):
    name: str
    description: str
    price: int
    is_active: bool


class ChatPurchaseEntity(EntityWithMetadata):
    is_used: bool
    expires_at: Optional[datetime] = None
    price: int
    product_id: int
    user_id: int


class ReviewEntity(EntityWithMetadata):
    message: str
    rating: int
    user_id: int
    for_user_id: int
    deal_id: int
