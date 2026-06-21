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

        if isinstance(event, Message) and event.sender_chat:
            return

        if not getattr(event, "from_user", None) or event.from_user.is_bot:
            return await handler(event, data)

        from_user = event.from_user
        usernames = [from_user.username.lower()] if from_user.username else []
        user = await user_service.get_or_create(from_user.id, usernames)
        data["user"] = user

        if (
            isinstance(event, Message)
            and event.reply_to_message
            and not event.reply_to_message.sender_chat
            and event.reply_to_message.from_user
            and not event.reply_to_message.from_user.is_bot
        ):
            reply_from_user = event.reply_to_message.from_user
            reply_usernames = (
                [reply_from_user.username.lower()] if reply_from_user.username else []
            )
            reply_to_user = await user_service.get_or_create(
                reply_from_user.id, reply_usernames
            )
            data["reply_to_user"] = reply_to_user

        return await handler(event, data)
