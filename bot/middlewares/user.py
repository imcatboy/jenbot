from typing import Callable, Dict, Any, Awaitable, Union
from aiogram.exceptions import TelegramAPIError
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

        try:
            chat = await event.bot.get_chat(event.from_user.id)
            usernames = [
                username.username.lower() for username in chat.active_usernames
            ]
        except TelegramAPIError:
            usernames = (
                [event.from_user.username.lower()] if event.from_user.username else []
            )

        user = await user_service.get_or_create(event.from_user.id, usernames)
        data["user"] = user

        if (
            isinstance(event, Message)
            and event.reply_to_message
            and event.reply_to_message.from_user
        ):
            try:
                chat = await event.bot.get_chat(event.reply_to_message.from_user.id)
                usernames = [
                    username.username.lower() for username in chat.active_usernames
                ]
            except TelegramAPIError:
                usernames = (
                    [event.reply_to_message.from_user.username.lower()]
                    if event.reply_to_message.from_user.username
                    else []
                )

            reply_to_user = await user_service.get_or_create(
                event.reply_to_message.from_user.id, usernames
            )
            data["reply_to_user"] = reply_to_user

        return await handler(event, data)
