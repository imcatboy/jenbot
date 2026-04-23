import asyncio

from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ChatMemberStatus
from datetime import datetime
from aiogram import Bot
from typing import List

from domain.services import ModerationService
from domain.objects.types import ViolationType


async def actualize_violations_loop(bot: Bot, moderation_service: ModerationService):
    violations = await moderation_service.get_violations_to_actualize()
    inactive_violations_ids: List[int] = []

    for violation in violations:
        if violation.type == ViolationType.WARN:
            if violation.expires_at and violation.expires_at < datetime.now():
                inactive_violations_ids.append(violation.id)
        elif violation.type == ViolationType.MUTE:
            try:
                member = await bot.get_chat_member(violation.telegram_chat_id, violation.user.telegram_id)

                if member.status != ChatMemberStatus.RESTRICTED:
                    inactive_violations_ids.append(violation.id)
            except TelegramBadRequest:
                inactive_violations_ids.append(violation.id)
        elif violation.type == ViolationType.BAN:
            try:
                member = await bot.get_chat_member(violation.telegram_chat_id, violation.user.telegram_id)

                if member.status != ChatMemberStatus.KICKED:
                    inactive_violations_ids.append(violation.id)
            except TelegramBadRequest:
                inactive_violations_ids.append(violation.id)
        
        await asyncio.sleep(1)
    
    if inactive_violations_ids:
        await moderation_service.set_violations_active(inactive_violations_ids, False)