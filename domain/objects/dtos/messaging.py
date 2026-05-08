from .base import BaseDTO, GetDTO

from typing import Optional, List


class CreateFileDTO(BaseDTO):
    name: str
    display_name: str
    extension: str
    uploaded_by_user_id: int


class CreateChatDTO(BaseDTO):
    name: str
    author_id: Optional[int] = None
    deal_id: Optional[int] = None
    participant_ids: List[int]


class CreateMessageDTO(BaseDTO):
    body: Optional[str] = None
    user_id: int
    chat_id: int
    file_ids: Optional[List[int]] = None


class GetChatsDTO(GetDTO):
    user_id: int


class GetMessagesDTO(GetDTO):
    user_id: int
    chat_id: int
    