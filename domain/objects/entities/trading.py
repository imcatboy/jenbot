from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from domain.objects.entities.user import ReputationUserWithUsersEntity
from domain.objects.types import DealCondition, DealType, DealStatus, ReportStatus
from .base import BaseEntity, EntityWithMetadata

if TYPE_CHECKING:
    from .marketplace import ProductOptionEntity, ProductWithImagesEntity
    from .user import UserEntity


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


class ExternalDealEntity(EntityWithMetadata):
    amount: float
    description: str
    expires_at: datetime
    status: DealStatus
    seller_id: int
    buyer_id: int
    agent_id: Optional[int] = None


class ScamReportEntity(EntityWithMetadata):
    description: Optional[str] = None
    contact_info: Optional[str] = None
    attachments: List[str]
    comment: Optional[str] = None
    status: ReportStatus
    user_id: int
    accused_reputation_user_id: Optional[int] = None
    applied_by_user_id: Optional[int] = None


class ScamReportWithRelationsEntity(ScamReportEntity):
    user: UserEntity
    accused_reputation_user: Optional[ReputationUserWithUsersEntity] = None
    applied_by_user: Optional[UserEntity] = None
