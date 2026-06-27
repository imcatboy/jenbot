from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from typing import Optional

from domain.services import ModerationService, ConfigService
from domain.objects.types import ChatAction, ChatEvent
from bot.core import BotProtocol, with_telegram_retry
from domain.objects import entities, exceptions
from bot.data import text


class AuditActions:

    def __init__(
        self,
        moderation_service: ModerationService,
        bot: BotProtocol,
        config_service: ConfigService,
    ) -> None:
        self.moderation_service = moderation_service
        self.config_service = config_service
        self.bot = bot

    async def upload_audit(
        self, violation_id: int, message: Optional[Message] = None
    ) -> None:
        violation = await self.moderation_service.get_violation(violation_id)
        audit_chat_id = await self.config_service.get("audit_chat_id")

        if not audit_chat_id:
            raise exceptions.ConfigNotFoundException("audit_chat_id")

        if message:
            try:
                await with_telegram_retry(
                    lambda: self.bot.forward_message(
                        audit_chat_id, message.chat.id, message.message_id
                    )
                )
                await with_telegram_retry(lambda: message.delete())
            except TelegramBadRequest:
                pass

        await with_telegram_retry(
            lambda: self.bot.send_message(
                audit_chat_id, text.get_audit_message(violation)
            )
        )

    async def upload_action_audit(
        self,
        action: ChatAction,
        user: entities.UserEntity,
        applied_by_user: entities.UserEntity,
        violation_id: Optional[int] = None,
    ) -> None:
        audit_chat_id = await self.config_service.get("audit_chat_id")

        if not audit_chat_id:
            raise exceptions.ConfigNotFoundException("audit_chat_id")

        await with_telegram_retry(
            lambda: self.bot.send_message(
                audit_chat_id,
                text.get_action_audit_message(
                    action, user, applied_by_user, violation_id
                ),
            )
        )

    async def upload_event_audit(
        self,
        event: ChatEvent,
        user: entities.UserEntity,
        telegram_chat_id: int,
        comment: Optional[str] = None,
        message: Optional[Message] = None,
    ) -> None:
        audit_chat_id = await self.config_service.get("audit_chat_id")

        if not audit_chat_id:
            raise exceptions.ConfigNotFoundException("audit_chat_id")

        await with_telegram_retry(
            lambda: self.bot.send_message(
                audit_chat_id,
                text.get_event_audit_message(event, user, telegram_chat_id, comment),
            )
        )

        if message:
            try:
                await with_telegram_retry(
                    lambda: self.bot.forward_message(
                        audit_chat_id, message.chat.id, message.message_id
                    )
                )
                await with_telegram_retry(lambda: message.delete())
            except TelegramBadRequest:
                pass
