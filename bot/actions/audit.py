from aiogram.types import Message
from typing import Optional

from domain.services import ModerationService, ConfigService
from bot.core import BotProtocol
from bot.data import text
from domain.objects import entities
from domain.objects.types import ChatAction


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
        audit_chat_id = await self.config_service.get("audit_chat_id", 0)

        if message:
            await self.bot.forward_message(
                audit_chat_id, message.chat.id, message.message_id
            )
            await message.delete()

        await self.bot.send_message(audit_chat_id, text.get_audit_message(violation))

    async def upload_action_audit(
        self,
        action: ChatAction,
        user: entities.UserEntity,
        applied_by_user: entities.UserEntity,
        violation_id: Optional[int] = None,
    ) -> None:
        audit_chat_id = await self.config_service.get("audit_chat_id", 0)
        await self.bot.send_message(
            audit_chat_id,
            text.get_action_audit_message(action, user, applied_by_user, violation_id),
        )
