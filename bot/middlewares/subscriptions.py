from aiogram.dispatcher.event.handler import HandlerObject
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError
from aiogram.enums import ChatMemberStatus
from aiogram import BaseMiddleware

from domain.services import ConfigService
from bot.data import text, keyboards


class SubscriptionsMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[
            [Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]
        ],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        handler_object: HandlerObject | None = data["handler"]

        if not handler_object or not handler_object.flags.get("subscriptions"):
            return await handler(event, data)

        config_service: ConfigService = data["config_service"]

        if not getattr(event, "from_user", None):
            return await handler(event, data)

        subscriptions = await config_service.get("subscriptions", [])
        message: Message | None = None

        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            message = event.message

        if not message:
            return await handler(event, data)

        for subscription in subscriptions:
            try:
                chat_member = await event.bot.get_chat_member(
                    subscription, event.from_user.id
                )

                if not chat_member.status in [
                    ChatMemberStatus.MEMBER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                ]:
                    return await message.answer(
                        text.SUBSCRIPTION_ERROR,
                        reply_markup=keyboards.get_subscriptions_keyboard(
                            subscriptions
                        ),
                    )
            except TelegramAPIError:
                return await message.answer(
                    text.SUBSCRIPTION_ERROR,
                    reply_markup=keyboards.get_subscriptions_keyboard(subscriptions),
                )

        return await handler(event, data)
