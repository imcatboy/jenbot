from __future__ import annotations

from typing import Optional

from .base import EntityWithMetadata


class ChatEntity(EntityWithMetadata):
    name: str
    author_id: Optional[int] = None
    deal_id: Optional[int] = None


class MessageEntity(EntityWithMetadata):
    body: Optional[str] = None
    user_id: int
    chat_id: int


class ChatParticipantEntity(EntityWithMetadata):
    user_id: int
    chat_id: int
    last_read_message_id: Optional[int] = None


class FileEntity(EntityWithMetadata):
    name: str
    display_name: str
    extension: str
    message_id: Optional[int] = None
    product_id: Optional[int] = None
    uploaded_by_user_id: int
