from aiogram.types import Message
from aiogram.enums import ChatType

from domain.objects import entities, exceptions
from domain.services import UserService, TradingService
from bot.actions.media import MediaActions
from bot.data import text, keyboards


class ReputationActions:

    def __init__(
        self,
        user_service: UserService,
        trading_service: TradingService,
        media_actions: MediaActions,
    ) -> None:
        self.user_service = user_service
        self.trading_service = trading_service
        self.media_actions = media_actions

    async def send_check(self, message: Message, search: str) -> None:
        reputation_users = await self.user_service.get_reputation_users(search)

        if not reputation_users:
            image = await self.media_actions.get_telegram_file("unknown_user")
            await message.answer_photo(
                photo=image,
                caption=text.get_check_error_message(search),
            )
            return

        if len(reputation_users) > 1:
            await message.answer(
                text.MANY_REPUTATION_USERS,
                reply_markup=keyboards.get_reputation_user_keyboard(reputation_users),
            )
            return

        await self.send_card(message, reputation_users[0])

    async def send_card(
        self,
        message: Message,
        reputation: entities.ReputationUserWithRelationsEntity,
    ) -> None:
        bot = await message.bot.get_me()
        scam_reports = await self.trading_service.get_scam_reports(reputation.id)
        image = await self.media_actions.get_telegram_file(reputation.role.value)
        is_private = message.chat.type == ChatType.PRIVATE
        await message.answer_photo(
            photo=image,
            caption=text.get_check_success_message(reputation),
            reply_markup=(
                keyboards.get_check_keyboard(bot.username, reputation, scam_reports)
                if is_private
                else None
            ),
        )

    async def send_check_by_reply(
        self, message: Message, reply_to_user: entities.UserEntity
    ) -> None:
        try:
            reputation = await self.user_service.get_reputation_user_by_user_id(
                reply_to_user.id
            )
        except exceptions.ObjectNotFoundException:
            image = await self.media_actions.get_telegram_file("unknown_user")
            await message.answer_photo(
                photo=image,
                caption=text.get_check_error_message(),
            )
            return

        await self.send_card(message, reputation)

    async def send_own_reputation(self, message: Message, user_id: int) -> None:
        try:
            reputation = await self.user_service.get_reputation_user_by_user_id(user_id)
        except exceptions.ObjectNotFoundException:
            image = await self.media_actions.get_telegram_file("unknown_user")
            await message.answer_photo(
                photo=image,
                caption=text.get_check_error_message(),
            )
            return

        await self.send_card(message, reputation)
