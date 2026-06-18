import logging
import asyncio

from typing import Callable, Dict, Any, Awaitable
from aiogram.exceptions import TelegramAPIError
from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import Message
from datetime import datetime

from domain.services import ModerationService
from domain.objects import entities
from bot.data import text


logger = logging.getLogger(__name__)


class TrackerMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            return await handler(event, data)

        moderation_service: ModerationService = data["moderation_service"]
        user: entities.UserEntity | None = data.get("user")

        if not user:
            return await handler(event, data)

        trackers = await moderation_service.get_trackers(user.id)

        if not trackers:
            return await handler(event, data)

        for tracker in trackers:
            if tracker.expires_at and tracker.expires_at < datetime.now():
                await moderation_service.disable_tracker(
                    tracker.tracked_user_id, tracker.tracking_user_id
                )
                continue

            old_message_id = await moderation_service.get_tracker_message(tracker.id)

            if old_message_id:
                try:
                    await event.bot.delete_message(
                        chat_id=tracker.tracking_user.telegram_id,
                        message_id=old_message_id,
                    )
                except TelegramAPIError:
                    pass

            try:
                new_message = await event.bot.send_message(
                    chat_id=tracker.tracking_user.telegram_id,
                    text=text.TRACKER_MESSAGE.format(
                        event.get_url(),
                        text.format_user_handle(
                            tracker.tracked_user.usernames,
                            tracker.tracked_user.telegram_id,
                        ),
                    ),
                )
                await moderation_service.set_tracker_message(
                    tracker.id, new_message.message_id
                )
            except TelegramAPIError:
                logger.warning(
                    f"Moderator {tracker.tracking_user.telegram_id} blocked bot. Disabling tracker."
                )
                await moderation_service.disable_tracker(tracker.id)

        return await handler(event, data)
