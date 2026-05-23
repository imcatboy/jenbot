from typing import Callable, Dict, Any, Awaitable, Union
from aiogram.types import Message, CallbackQuery
from aiogram import BaseMiddleware

from domain.services import UserService


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

        return await handler(event, data)
