from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo
from aiogram.exceptions import TelegramAPIError
from typing import List, Optional
from pathlib import Path

from domain.services import MediaService, ConfigService
from bot.data import text, attachments
from domain.objects import exceptions
from bot.core import BotProtocol
from bot.core import MEDIA_MAP


TELEGRAM_MEDIA_GROUP_LIMIT = 10


class MediaActions:

    def __init__(
        self,
        media_service: MediaService,
        bot: BotProtocol,
        config_service: ConfigService,
    ) -> None:
        self.media_service = media_service
        self.bot = bot
        self.config_service = config_service

    async def get_telegram_file(self, name: str) -> str:
        try:
            file = await self.media_service.get_telegram_file(name)
            return file.file_id
        except exceptions.ObjectNotFoundException:
            pass
        admin_chat_id = await self.config_service.get("admin_chat_id")

        if not admin_chat_id:
            raise exceptions.ConfigNotFoundException("admin_chat_id")

        path = Path(MEDIA_MAP[name])
        photo = await self.bot.send_photo(admin_chat_id, FSInputFile(path))
        file_id = photo.photo[-1].file_id
        await self.media_service.create_telegram_file(name, file_id)
        return file_id

    async def create_media_group(
        self, files: List[str], caption: Optional[str] = None
    ) -> List[InputMediaPhoto | InputMediaVideo]:
        attachments: List[InputMediaPhoto | InputMediaVideo] = []
        has_caption = False

        for attachment in files:
            item_caption = caption if not has_caption else None
            media = await self._create_input_media(attachment, item_caption)

            if media:
                attachments.append(media)
                has_caption = True
        
        return attachments

    async def _create_input_media(
        self,
        attachment: str,
        caption: Optional[str],
    ) -> InputMediaPhoto | InputMediaVideo | None:
        file_id, media_type = attachments.parse_attachment(attachment)

        if media_type == "video":
            return InputMediaVideo(media=file_id, caption=caption)

        if media_type == "photo":
            return InputMediaPhoto(media=file_id, caption=caption)

        try:
            file = await self.bot.get_file(file_id)
            path = file.file_path or ""

            if "video" in path:
                return InputMediaVideo(media=file.file_id, caption=caption)

            return InputMediaPhoto(media=file.file_id, caption=caption)
        except TelegramAPIError:
            return None

    async def send_preview(
        self,
        chat_id: int,
        file_ids: List[str],
    ) -> None:
        for index, offset in enumerate(
            range(0, len(file_ids), TELEGRAM_MEDIA_GROUP_LIMIT)
        ):
            chunk = file_ids[offset : offset + TELEGRAM_MEDIA_GROUP_LIMIT]
            caption = (
                text.ATTACHMENTS_PREVIEW_CAPTION.format(len(file_ids))
                if index == 0
                else None
            )
            media_group = await self.create_media_group(chunk, caption=caption)

            if media_group:
                await self.bot.send_media_group(chat_id, media_group)
