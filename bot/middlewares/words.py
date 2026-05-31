import asyncio
import re

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Message
from typing import List
from html import escape

from domain.objects.types import UserRole, ChatEvent
from domain.services import ConfigService
from bot.actions import AuditActions
from domain.objects import entities
from bot.data import text


class WordsMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user: entities.UserEntity = data["user"]
        audit_actions: AuditActions = data["audit_actions"]

        if (
            user.role in [UserRole.ADMIN, UserRole.MODERATOR]
            or event.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]
            or (not event.text and not event.caption)
        ):
            return await handler(event, data)

        config_service: ConfigService = data["config_service"]
        words: List[str] = await config_service.get("ban_words", [])
        normalized_message = self._normalize_message(event.text or event.caption)

        for word in words:
            if word.lower() in normalized_message:
                message = await event.answer(
                    text.BAN_WORD_ERROR.format(
                        text.format_user_handle(
                            event.from_user.username, event.from_user.id
                        ),
                        escape(word),
                    )
                )
                await audit_actions.upload_event_audit(
                    ChatEvent.BAN_WORD,
                    user,
                    event.chat.id,
                    word,
                    event,
                )
                await asyncio.sleep(5)
                await message.delete()
                return

        return await handler(event, data)

    def _normalize_message(self, message: str) -> str:
        message = message.lower()
        message = message.translate(text.HOMOGLYPHS)
        message = re.sub(r"[^а-яёa-z0-9]", "", message)
        return message
