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


WORD_CHAR_CLASS = r"а-яёa-z0-9"


class WordsMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user: entities.UserEntity | None = data.get("user")

        if not user:
            return await handler(event, data)

        audit_actions: AuditActions = data["audit_actions"]

        if (
            user.role in [UserRole.ADMIN, UserRole.MODERATOR]
            or event.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]
            or (not event.text and not event.caption)
        ):
            return await handler(event, data)

        config_service: ConfigService = data["config_service"]
        words: List[str] = await config_service.get("ban_words", [])
        raw = event.text or event.caption
        spaced_message = self._normalize_spaced(raw)

        for word in words:
            if not word.strip():
                continue

            if self._matches_ban_word(spaced_message, word):
                message = await event.answer(
                    text.BAN_WORD_ERROR.format(
                        text.format_from_user(
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

    def _normalize_spaced(self, message: str) -> str:
        message = message.lower()
        message = message.translate(text.HOMOGLYPHS)
        message = re.sub(rf"[^{WORD_CHAR_CLASS}]+", " ", message)
        return re.sub(r" +", " ", message).strip()

    def _matches_ban_word(self, spaced_message: str, word: str) -> bool:
        translated = word.lower().strip().translate(text.HOMOGLYPHS)

        if not translated:
            return False

        pattern = (
            rf"(?<![{WORD_CHAR_CLASS}]){re.escape(translated)}(?![{WORD_CHAR_CLASS}])"
        )
        return re.search(pattern, spaced_message, re.IGNORECASE) is not None
