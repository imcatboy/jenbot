from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String

from .base import EntityModel
from .trading import DealModel

if TYPE_CHECKING:
    from .user import UserModel


class ChatModel(EntityModel):
    __tablename__ = "chats"
    fk_name = "chat_id"

    name: Mapped[str] = mapped_column(String(100))
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    author: Mapped[Optional[UserModel]] = relationship(
        back_populates="authored_chats",
        foreign_keys=[author_id],
    )
    deal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("deals.id"))
    deal: Mapped[Optional[DealModel]] = relationship(
        back_populates="chats",
    )
    participants: Mapped[List[ChatParticipantModel]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
    )
    messages: Mapped[List[MessageModel]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
    )


class MessageModel(EntityModel):
    __tablename__ = "messages"
    fk_name = "message_id"

    body: Mapped[Optional[str]] = mapped_column("text", String(1024))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(
        back_populates="messages",
        foreign_keys=[user_id],
    )
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    chat: Mapped[ChatModel] = relationship(
        back_populates="messages",
    )
    files: Mapped[List[MessageFileModel]] = relationship(
        back_populates="message",
        cascade="all, delete-orphan",
    )
    last_read_by: Mapped[List[ChatParticipantModel]] = relationship(
        back_populates="last_read_message",
        cascade="all, delete-orphan",
    )


class ChatParticipantModel(EntityModel):
    __tablename__ = "chat_participiants"
    fk_name = "chat_participant_id"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(
        back_populates="chat_participants",
        foreign_keys=[user_id],
    )
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    chat: Mapped[ChatModel] = relationship(
        back_populates="participants",
    )
    last_read_message_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("messages.id")
    )
    last_read_message: Mapped[Optional[MessageModel]] = relationship(
        back_populates="last_read_by",
        foreign_keys=[last_read_message_id],
    )


class MessageFileModel(EntityModel):
    __tablename__ = "files"
    fk_name = "file_id"

    name: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(100))
    extension: Mapped[str] = mapped_column(String(10))
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"))
    message: Mapped[MessageModel] = relationship(
        back_populates="files",
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UserModel] = relationship(
        back_populates="files",
        foreign_keys=[user_id],
    )
