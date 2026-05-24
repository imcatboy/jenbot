from aiogram.dispatcher.event.handler import HandlerObject
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram.types import Message, CallbackQuery
from aiogram import BaseMiddleware

from domain.objects import entities
from bot.data import text


class RoleMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[
            [Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]
        ],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        user: entities.UserEntity = data["user"]
        handler_object: HandlerObject = data["handler"]

        if not handler_object or not handler_object.flags.get("user_role") or not user:
            return await handler(event, data)

        if not user.role in handler_object.flags.get("user_role"):
            message: Message | None = None

            if isinstance(event, Message):
                message = event
            elif isinstance(event, CallbackQuery):
                message = event.message
            if message:
                return await message.answer(text.USER_NOT_ALLOWED_TO_ACTION)

            return

        return await handler(event, data)
