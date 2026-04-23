from aiogram.dispatcher.event.handler import HandlerObject
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram.types import Message, CallbackQuery
from aiogram import BaseMiddleware

from domain.services import UserService
from bot.data import text


class UserMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[
            [Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]
        ],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        user_service: UserService = data["user_service"]

        if not getattr(event, "from_user", None):
            return await handler(event, data)

        user = await user_service.get_or_create(
            event.from_user.id, event.from_user.username
        )
        data["user"] = user
        handler_object: HandlerObject = data["handler"]

        if (
            isinstance(event, Message)
            and event.reply_to_message
            and event.reply_to_message.from_user
        ):
            reply_to_user = await user_service.get_or_create(
                event.reply_to_message.from_user.id,
                event.reply_to_message.from_user.username,
            )
            data["reply_to_user"] = reply_to_user

        if handler_object.flags.get(
            "user_role"
        ) and not user.role in handler_object.flags.get("user_role"):
            message: Message | None = None

            if isinstance(event, Message):
                message = event
            elif isinstance(event, CallbackQuery):
                message = event.message

            if message:
                return await message.answer(text.USER_NOT_ALLOWED_TO_ACTION)

            return

        return await handler(event, data)
