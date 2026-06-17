from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from datetime import datetime

from domain.objects.types import TransactionType
from .base import EntityWithMetadata


if TYPE_CHECKING:
    from .user import UserWithReputationUserEntity


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
    author_id: int
    subject_user_id: int
    subject_reputation_user_id: int
    deal_id: Optional[int] = None
    external_deal_id: Optional[int] = None


class ReviewWithAuthorEntity(ReviewEntity):
    author: UserWithReputationUserEntity
