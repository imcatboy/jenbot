from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable, List
from aiogram.types.message import Message
from aiogram import BaseMiddleware

from bot.data import text, keyboards, states, attachments


class MediaCheckMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        handler_object: HandlerObject | None = data.get("handler")

        if not handler_object or not handler_object.flags.get("collect_files"):
            return await handler(event, data)

        files: List[str] = []

        if "album" in data:
            for message in data["album"]:
                attachment = self._get_attachment(message)

                if not attachment:
                    continue

                files.append(attachment)
        else:
            attachment = self._get_attachment(event)

            if attachment:
                files.append(attachment)

        if not files:
            state: FSMContext | None = data.get("state")
            count = 0
            allow_skip = False

            if state:
                state_data = await state.get_data()
                count = len(state_data.get("attachments", []))
                current_state = await state.get_state()
                allow_skip = current_state == states.ReportState.attachments.state

            return await event.answer(
                text.REPORT_ATTACHMENTS_ERROR,
                reply_markup=keyboards.get_attachments_keyboard(
                    event.from_user.id, count, allow_skip
                ),
            )

        data["file_ids"] = files
        return await handler(event, data)

    def _get_attachment(self, message: Message) -> str | None:
        if message.photo:
            return attachments.encode_attachment(message.photo[-1].file_id, "photo")
        if message.video:
            return attachments.encode_attachment(message.video.file_id, "video")

        return None
