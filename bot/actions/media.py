from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo
from aiogram.exceptions import TelegramAPIError
from typing import List, Optional
from pathlib import Path

from domain.services import MediaService, ConfigService
from domain.objects import exceptions
from bot.core import BotProtocol
from bot.core import MEDIA_MAP


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
            try:
                file = await self.bot.get_file(attachment)

                if "photo" in file.file_path:
                    attachments.append(
                        InputMediaPhoto(
                            media=file.file_id,
                            caption=caption if not has_caption else None,
                        )
                    )
                elif "video" in file.file_path:
                    attachments.append(
                        InputMediaVideo(
                            media=file.file_id,
                            caption=caption if not has_caption else None,
                        )
                    )

                has_caption = True
            except TelegramAPIError:
                continue

        return attachments
