import logging

from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.enums import ChatMemberStatus
from aiogram import Bot
from typing import List

from domain.services import ModerationService, ConfigService
from domain.objects.types import ViolationType
from domain.objects import entities


logger = logging.getLogger(__name__)

STATUS_VIOLATIONS_BATCH_SIZE = 50


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
) -> None:
    expired_warns = await moderation_service.deactivate_expired_warn_violations()

    if expired_warns:
        logger.info("Deactivated %s expired warn violations", expired_warns)

    violations = await moderation_service.get_status_violations_to_actualize(
        STATUS_VIOLATIONS_BATCH_SIZE
    )

    if not violations:
        return

    chat_ids: List[int] = await config_service.get("chats", [])
    inactive_violations_ids: List[int] = []
    checked_violations_ids: List[int] = []

    for violation in violations:
        checked_violations_ids.append(violation.id)

        try:
            if violation.type == ViolationType.MUTE:
                if not await _check_status_active(
                    ChatMemberStatus.RESTRICTED, violation, bot, chat_ids
                ):
                    inactive_violations_ids.append(violation.id)
            elif violation.type == ViolationType.BAN:
                if not await _check_status_active(
                    ChatMemberStatus.KICKED, violation, bot, chat_ids
                ):
                    inactive_violations_ids.append(violation.id)
        except TelegramNetworkError:
            checked_violations_ids.pop()
            raise

    still_active_ids = [
        vid for vid in checked_violations_ids if vid not in inactive_violations_ids
    ]

    if inactive_violations_ids:
        await moderation_service.set_violations_active(inactive_violations_ids, False)
        logger.info(
            "Deactivated %s mute/ban violations after status check",
            len(inactive_violations_ids),
        )

    if still_active_ids:
        await moderation_service.touch_violations_updated_at(still_active_ids)
