from __future__ import annotations

from typing import Optional
from datetime import datetime

from objects.types import TransactionType
from .base import BaseEntity


class TransactionEntity(BaseEntity):
    amount: int
    type: TransactionType
    description: str
    user_id: int
    receiver_id: Optional[int]


class ProductEntity(BaseEntity):
    name: str
    description: str
    price: int
    is_active: bool


class PurchaseEntity(BaseEntity):
    is_used: bool
    expires_at: Optional[datetime]
    price: int
    product_id: int
    user_id: int
