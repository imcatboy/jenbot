import logging
import asyncio

from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.enums import ChatMemberStatus
from aiogram.types import ChatPermissions
from typing import List, Optional
from datetime import datetime

from domain.services import (
    ModerationService,
    ConfigService,
    UserService,
    TradingService,
)
from domain.objects.types import UserRole, ViolationType
from domain.objects import dtos, entities, exceptions
from bot.data import text, keyboards
from bot.core import BotProtocol
from .media import MediaActions


logger = logging.getLogger(__name__)


class ModerationActions:

    def __init__(
        self,
        moderation_service: ModerationService,
        user_service: UserService,
        bot: BotProtocol,
        config_service: ConfigService,
        media_actions: MediaActions,
        trading_service: TradingService,
    ) -> None:
        self.moderation_service = moderation_service
        self.config_service = config_service
        self.user_service = user_service
        self.media_actions = media_actions
        self.bot = bot
        self.trading_service = trading_service

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
            media_group = await self.media_actions.create_media_group(
                report.attachments
            )

            if media_group:
                await self.bot.send_media_group(
                    admin_chat_id,
                    media_group,
                )

            await self.bot.send_message(
                admin_chat_id,
                text.get_report_message(report),
                reply_markup=keyboards.get_report_keyboard(report),
            )
            return

        await self.bot.send_message(
            admin_chat_id,
            text.get_report_message(report),
            reply_markup=keyboards.get_report_keyboard(report),
        )

    async def send_scam_report_message(self, scam_report_id: int) -> None:
        scam_report = await self.trading_service.get_scam_report(scam_report_id)
        moderation_chat_id = await self.config_service.get("moderation_chat_id")

        if not moderation_chat_id:
            raise exceptions.ConfigNotFoundException("moderation_chat_id")

        if scam_report.attachments:
            media_group = await self.media_actions.create_media_group(
                scam_report.attachments
            )

            if media_group:
                await self.bot.send_media_group(moderation_chat_id, media_group)

        await self.bot.send_message(
            moderation_chat_id,
            text.get_scam_report_message(scam_report),
            reply_markup=keyboards.get_scam_report_keyboard(scam_report),
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

    async def send_reputation_request_updated_message(
        self, user: entities.UserEntity, reason: Optional[str] = None
    ) -> None:
        try:
            await self.bot.send_message(
                user.telegram_id,
                (
                    text.REPUTATION_REQUEST_REJECTED.format(reason)
                    if reason
                    else text.REPUTATION_REQUEST_ACCEPTED
                ),
            )
        except TelegramAPIError:
            pass

    async def send_reputation_request_message(
        self, reputation_request: entities.ReputationRequestWithUserEntity
    ) -> None:
        moderation_chat_id = await self.config_service.get("moderation_chat_id")

        if not moderation_chat_id:
            raise exceptions.ConfigNotFoundException("moderation_chat_id")

        await self.bot.send_message(
            moderation_chat_id,
            text.get_reputation_request_message(reputation_request),
            reply_markup=keyboards.get_reputation_request_keyboard(reputation_request),
        )

    async def send_scam_report_updated_message(
        self, scam_report: entities.ScamReportWithRelationsEntity
    ) -> None:
        try:
            await self.bot.send_message(
                scam_report.user.telegram_id,
                text.get_scam_report_updated_message(scam_report),
            )
        except TelegramAPIError:
            pass

    async def send_new_review_message(
        self, review: entities.ReviewWithRelationsEntity
    ) -> None:
        moderation_chat_id = await self.config_service.get("moderation_chat_id")

        if not moderation_chat_id:
            raise exceptions.ConfigNotFoundException("moderation_chat_id")

        await self.bot.send_message(
            moderation_chat_id,
            text.get_new_review_message(review),
            reply_markup=keyboards.get_review_admin_keyboard(review),
        )

    async def send_review_deleted_message(
        self, review: entities.ReviewWithRelationsEntity, reason: Optional[str] = None
    ) -> None:
        try:
            await self.bot.send_message(
                review.author.telegram_id,
                text.get_review_deleted_message(review, reason),
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
            await self.bot.send_message(
                tracker.tracking_user.telegram_id,
                text.TRACKER_ADDED.format(
                    text.format_user_handle(tracker.tracked_user)
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
            await self.bot.send_message(
                tracking_user.telegram_id,
                text.TRACKER_REMOVED.format(text.format_user_handle(tracked_user)),
            )
        except TelegramAPIError:
            raise exceptions.ChatNotFoundException(tracking_user.telegram_id)
