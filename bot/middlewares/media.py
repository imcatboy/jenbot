from aiogram.dispatcher.event.handler import HandlerObject
from typing import Callable, Dict, Any, Awaitable, List
from aiogram.types.message import Message
from aiogram import BaseMiddleware

from bot.data import text, keyboards


class MediaCheckMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        handler_object: HandlerObject | None = data.get("handler")

        if not handler_object or not handler_object.flags.get("want_files"):
            return await handler(event, data)

        files: List[str] = []

        if "album" in data:
            for message in data["album"]:
                file_id = self._get_file_id(message)

                if not file_id:
                    continue

                files.append(file_id)
        else:
            file_id = self._get_file_id(event)

            if file_id:
                files.append(file_id)

        if not files:
            return await event.answer(text.REPORT_ATTACHMENTS_ERROR, reply_markup=keyboards.REPORT_ATTACHMENTS_KEYBOARD)

        data["file_ids"] = files
        return await handler(event, data)

    def _get_file_id(self, message: Message) -> str:
        if message.photo:
            return message.photo[-1].file_id
        if message.video:
            return message.video.file_id
        
        return None
