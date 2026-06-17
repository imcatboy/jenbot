import logging
import asyncio

from aiogram.types import InputMediaPhoto, InputMediaVideo, ChatPermissions
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.enums import ChatMemberStatus
from typing import List, Optional
from datetime import datetime

from domain.services import ModerationService, ConfigService, UserService
from domain.objects.types import UserRole, ViolationType
from domain.objects import dtos, entities, exceptions
from bot.data import text, keyboards
from bot.core import BotProtocol


logger = logging.getLogger(__name__)


class ModerationActions:

    def __init__(
        self,
        moderation_service: ModerationService,
        user_service: UserService,
        bot: BotProtocol,
        config_service: ConfigService,
    ) -> None:
        self.moderation_service = moderation_service
        self.config_service = config_service
        self.user_service = user_service
        self.bot = bot

    async def _safe_ban(
        self, chat_id: int, user: entities.UserEntity, expires_at: Optional[datetime]
    ) -> bool:
        try:
            member = await self.bot.get_chat_member(chat_id, user.telegram_id)

            if member.status == ChatMemberStatus.KICKED:
                return False
        except TelegramBadRequest:
            pass

        try:
            await self.bot.ban_chat_member(chat_id, user.telegram_id, expires_at)
            return True
        except TelegramAPIError as e:
            logger.warning(f"Ban failed in chat {chat_id}: {e}")
            return False

    async def _execute_global_ban(
        self, user: entities.UserEntity, dto: dtos.GlobalBanUserDTO
    ) -> entities.ChatViolationEntity:
        if user.role != UserRole.USER:
            raise exceptions.ModerationException(user.id, ViolationType.BAN)

        chats: List[int] = await self.config_service.get("chats", [])

        if not chats:
            raise exceptions.ModerationException(dto.user_id, ViolationType.BAN)

        semaphore = asyncio.Semaphore(5)

        async def ban_with_limit(chat_id: int) -> bool:
            async with semaphore:
                return await self._safe_ban(chat_id, user, dto.expires_at)

        results = await asyncio.gather(*(ban_with_limit(chat_id) for chat_id in chats))
        success_count = sum(results)
        failed_count = len(results) - success_count

        if failed_count > 0:
            logger.warning(
                f"Global ban for {user.telegram_id}: {success_count}/{len(results)} chats succeeded. "
                f"Failed chats: {[chat_id for chat_id, success in zip(chats, results) if not success]}"
            )

        if success_count == 0:
            raise exceptions.ModerationException(dto.user_id, ViolationType.BAN)

        violation_dto = dtos.AddViolationDTO(**dto.model_dump(), type=ViolationType.BAN)
        return await self.moderation_service.add_violation(violation_dto)

    async def publish_report(self, report_id: int) -> None:
        report = await self.moderation_service.get_report(report_id)
        admin_chat_id = await self.config_service.get("admin_chat_id")

        if not admin_chat_id:
            raise exceptions.ConfigNotFoundException("admin_chat_id")

        if report.attachments:
            attachments = []

            for attachment in report.attachments:
                try:
                    file = await self.bot.get_file(attachment)

                    if "photo" in file.file_path:
                        attachments.append(InputMediaPhoto(media=file.file_id))
                    elif "video" in file.file_path:
                        attachments.append(InputMediaVideo(media=file.file_id))
                except TelegramAPIError:
                    continue

            if attachments:
                await self.bot.send_media_group(admin_chat_id, attachments)

        await self.bot.send_message(
            admin_chat_id,
            text.get_report_message(report),
            reply_markup=keyboards.get_report_keyboard(report),
        )

    async def send_report_updated_message(
        self, report: entities.ReportWithUserEntity
    ) -> None:
        try:
            await self.bot.send_message(
                report.user.telegram_id,
                text.get_report_updated_message(report),
            )
        except TelegramAPIError:
            pass

    async def ban_user(self, dto: dtos.BanUserDTO) -> entities.ChatViolationEntity:
        user = await self.user_service.get_by_id(dto.user_id)

        if user.role != UserRole.USER:
            raise exceptions.ModerationException(dto.user_id, ViolationType.BAN)

        try:
            await self.bot.ban_chat_member(
                dto.telegram_chat_id, user.telegram_id, dto.expires_at
            )
        except TelegramAPIError:
            raise exceptions.ModerationException(dto.user_id, ViolationType.BAN)

        violation_dto = dtos.AddViolationDTO(**dto.model_dump(), type=ViolationType.BAN)
        violation = await self.moderation_service.add_violation(violation_dto)
        return violation

    async def global_ban_user(
        self, dto: dtos.GlobalBanUserDTO
    ) -> entities.ChatViolationEntity:
        user = await self.user_service.get_by_id(dto.user_id)

        if user.role != UserRole.USER:
            raise exceptions.ModerationException(dto.user_id, ViolationType.BAN)

        return await self._execute_global_ban(user, dto)

    async def unban_user(self, user_id: int, telegram_chat_id: int) -> None:
        user = await self.user_service.get_by_id(user_id)

        try:
            await self.bot.unban_chat_member(
                telegram_chat_id, user.telegram_id, only_if_banned=True
            )
        except TelegramAPIError:
            raise exceptions.ModerationException(user_id, ViolationType.BAN)

        await self.moderation_service.set_violations_inactive(
            user_id, ViolationType.BAN
        )

    async def mute_user(self, dto: dtos.MuteUserDTO) -> entities.ChatViolationEntity:
        user = await self.user_service.get_by_id(dto.user_id)

        if user.role != UserRole.USER:
            raise exceptions.ModerationException(dto.user_id, ViolationType.MUTE)

        permissions = ChatPermissions.model_validate(
            await self.config_service.get("muted_user_permissions", {})
        )

        try:
            await self.bot.restrict_chat_member(
                dto.telegram_chat_id,
                user.telegram_id,
                permissions,
                until_date=dto.expires_at,
            )
        except TelegramAPIError:
            raise exceptions.ModerationException(dto.user_id, ViolationType.MUTE)

        violation_dto = dtos.AddViolationDTO(
            **dto.model_dump(), type=ViolationType.MUTE
        )
        violation = await self.moderation_service.add_violation(violation_dto)
        return violation

    async def unmute_user(self, user_id: int, telegram_chat_id: int) -> None:
        user = await self.user_service.get_by_id(user_id)
        permissions = ChatPermissions.model_validate(
            await self.config_service.get("user_permissions", {})
        )

        try:
            await self.bot.restrict_chat_member(
                telegram_chat_id,
                user.telegram_id,
                permissions,
                until_date=None,
            )
        except TelegramAPIError:
            raise exceptions.ModerationException(user_id, ViolationType.MUTE)

        await self.moderation_service.set_violations_inactive(
            user_id, ViolationType.MUTE
        )

    async def add_tracker(self, dto: dtos.AddTrackerDTO) -> entities.TrackerEntity:
        tracker = await self.moderation_service.add_tracker(dto)

        try:
            username = (
                tracker.tracked_user.usernames[0].username
                if tracker.tracked_user.usernames
                else None
            )
            await self.bot.send_message(
                tracker.tracking_user.telegram_id,
                text.TRACKER_ADDED.format(
                    text.format_user_handle(username, tracker.tracked_user.telegram_id)
                ),
            )
        except TelegramAPIError:
            raise exceptions.ChatNotFoundException(tracker.tracking_user.telegram_id)

        return tracker

    async def remove_tracker(
        self, tracked_user: entities.UserEntity, tracking_user: entities.UserEntity
    ) -> None:
        await self.moderation_service.disable_tracker(tracked_user.id, tracking_user.id)

        try:
            username = (
                tracked_user.usernames[0].username if tracked_user.usernames else None
            )
            await self.bot.send_message(
                tracking_user.telegram_id,
                text.TRACKER_REMOVED.format(
                    text.format_user_handle(username, tracked_user.telegram_id)
                ),
            )
        except TelegramAPIError:
            raise exceptions.ChatNotFoundException(tracking_user.telegram_id)
