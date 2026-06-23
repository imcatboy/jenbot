from typing import Callable, Dict, Any, Awaitable, Union, List
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError
from aiogram.enums import ChatMemberStatus
from aiogram import BaseMiddleware

from domain.services import ConfigService
from bot.data import text, keyboards


ALLOWED_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
    ChatMemberStatus.KICKED,
}


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

        if not await self.ensure_subscribed(event, config_service):
            return

        return await handler(event, data)

    async def ensure_subscribed(
        self,
        event: Union[Message, CallbackQuery],
        config_service: ConfigService,
    ) -> bool:
        if not getattr(event, "from_user", None):
            return True

        subscriptions: List[str] = await config_service.get("subscriptions", [])
        message: Message | None = None

        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            message = event.message

        if not message or not subscriptions:
            return True

        for subscription in subscriptions:
            try:
                chat_member = await event.bot.get_chat_member(
                    subscription, event.from_user.id
                )

                if chat_member.status not in ALLOWED_STATUSES:
                    await message.answer(
                        text.SUBSCRIPTION_ERROR,
                        reply_markup=keyboards.get_subscriptions_keyboard(
                            subscriptions
                        ),
                    )
                    return False
            except TelegramAPIError:
                await message.answer(
                    text.SUBSCRIPTION_ERROR,
                    reply_markup=keyboards.get_subscriptions_keyboard(subscriptions),
                )
                return False

        return True
