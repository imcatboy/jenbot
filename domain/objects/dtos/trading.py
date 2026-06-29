from typing import Optional, List
from datetime import datetime

from domain.objects.types import DealCondition, DealStatus, DealType, ReportStatus
from .base import BaseDTO, GetDTO


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


class CreateScamReportDTO(BaseDTO):
    description: Optional[str] = None
    contact_info: Optional[str] = None
    attachments: List[str]
    user_id: int


class UpdateScamReportDTO(BaseDTO):
    status: Optional[ReportStatus] = None
    comment: Optional[str] = None
    applied_by_user_id: Optional[int] = None
    accused_reputation_user_id: Optional[int] = None


class CreateReviewDTO(BaseDTO):
    message: str
    rating: int
    author_id: int
    subject_user_id: int


class InsertReviewDTO(CreateReviewDTO):
    subject_reputation_user_id: int


class CreateExternalDealDTO(BaseDTO):
    deal_amount: float
    payment: Optional[str] = None
    description: str
    expires_at: datetime
    seller_id: int
    buyer_id: int
    agent_id: Optional[int] = None
    created_by_user_id: int


class InsertExternalDealDTO(CreateExternalDealDTO):
    refund_amount: float
    warranty_reputation_user_id: int


class UpdateExternalDealDTO(BaseDTO):
    status: Optional[DealStatus] = None
    seller_condition: Optional[DealCondition] = None
    buyer_condition: Optional[DealCondition] = None


class GetReviewsDTO(GetDTO):
    reputation_user_id: int


class GetMyReviewsDTO(GetDTO):
    user_id: int


class CreateExternalDealNotificationDTO(BaseDTO):
    external_deal_id: int
    user_id: int
    telegram_chat_id: int
    telegram_message_id: int


class UpdateExternalDealNotificationDTO(BaseDTO):
    telegram_message_id: Optional[int] = None
    telegram_chat_id: Optional[int] = None