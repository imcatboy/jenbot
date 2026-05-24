from aiogram.dispatcher.event.handler import HandlerObject
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message
from aiogram import BaseMiddleware
from typing import Type
from pydantic import TypeAdapter, ValidationError

from bot.data import text, keyboards


class StateMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        handler_object: HandlerObject = data["handler"]
        target_type: Type | None = handler_object.flags.get("cast")

        if not target_type:
            return await handler(event, data)

        try:
            result = TypeAdapter(target_type).validate_python(event.text)
        except ValidationError:
            return await event.answer(
                text.STATE_VALIDATION_ERROR,
                reply_markup=keyboards.get_cancel_keyboard(event.from_user.id),
            )

        data["state_data"] = result
        return await handler(event, data)
