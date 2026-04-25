from typing import List, Optional, Set
from datetime import datetime

from domain.objects.types import ID, DealStatus, Text
from .base import BaseRequest, BaseResponse


class MessageUserResponse(BaseResponse):
    id: int
    avatar_url: Optional[str]
    username: Optional[str]


class FileResponse(BaseResponse):
    id: int
    name: str
    display_name: str
    extension: str


class MessageResponse(BaseResponse):
    id: int
    body: Optional[str] = None
    files: List[FileResponse]
    user: MessageUserResponse
    created_at: datetime


class ChatListItemResponse(BaseResponse):
    id: int
    name: str
    author: MessageUserResponse
    last_message: Optional[MessageResponse] = None
    unread_count: int


class ChatsResponse(BaseResponse):
    items: List[ChatListItemResponse]
    has_more: bool


class ProductResponse(BaseResponse):
    id: int
    name: str
    image_url: str
    category_path: str


class ProductOptionResponse(BaseResponse):
    id: int
    name: str


class TradeResponse(BaseResponse):
    id: int
    count: int
    product: ProductResponse
    product_options: List[ProductOptionResponse]


class AdvertisementOptionPriceResponse(BaseResponse):
    id: int
    amount: float
    currency_sign: str


class AdvertisementResponse(BaseResponse):
    id: int
    name: str
    category_path: str
    trade: Optional[TradeResponse] = None
    payment_option: Optional[AdvertisementOptionPriceResponse] = None


class DealResponse(BaseResponse):
    id: int
    count: int
    expires_at: datetime
    status: DealStatus
    advertisement: AdvertisementResponse


class ChatResponse(BaseResponse):
    id: int
    name: str
    deal: DealResponse
    participants: List[MessageUserResponse]
    messages: List[MessageResponse]


class CreateChatRequest(BaseRequest):
    user_id: ID
    body: Optional[Text] = None


class CreateMessageRequest(BaseRequest):
    file_ids: Optional[Set[ID]] = None
    body: Optional[Text] = None
    chat_id: ID


class ReadChatRequest(BaseRequest):
    chat_id: ID
