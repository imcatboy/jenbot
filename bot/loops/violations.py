import asyncio

from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ChatMemberStatus
from datetime import datetime
from aiogram import Bot
from typing import List

from domain.services import ModerationService, ConfigService
from domain.objects.types import ViolationType
from domain.objects import entities


async def _check_warn_active(violation: entities.ChatViolationWithUserEntity) -> bool:
    if not violation.expires_at or violation.expires_at > datetime.now():
        return True

    return False


async def _check_status_active(
    status: ChatMemberStatus,
    violation: entities.ChatViolationWithUserEntity,
    bot: Bot,
    chat_ids: List[int],
) -> bool:
    check_chat_ids = (
        [violation.telegram_chat_id] if violation.telegram_chat_id else chat_ids
    )
    has_active_status = False

    for chat_id in check_chat_ids:
        try:
            member = await bot.get_chat_member(chat_id, violation.user.telegram_id)

            if member.status == status:
                has_active_status = True
                break
        except TelegramBadRequest:
            continue

    return has_active_status


async def actualize_violations_loop(
    bot: Bot, moderation_service: ModerationService, config_service: ConfigService
):
    violations = await moderation_service.get_violations_to_actualize()
    inactive_violations_ids: List[int] = []
    chat_ids: List[int] = await config_service.get("chats", [])

    for violation in violations:
        if violation.type == ViolationType.WARN:
            if not await _check_warn_active(violation):
                inactive_violations_ids.append(violation.id)
        elif violation.type == ViolationType.MUTE:
            if not await _check_status_active(
                ChatMemberStatus.RESTRICTED, violation, bot, chat_ids
            ):
                inactive_violations_ids.append(violation.id)
        elif violation.type == ViolationType.BAN:
            if not await _check_status_active(
                ChatMemberStatus.KICKED, violation, bot, chat_ids
            ):
                inactive_violations_ids.append(violation.id)

        await asyncio.sleep(1)

    if inactive_violations_ids:
        await moderation_service.set_violations_active(inactive_violations_ids, False)
