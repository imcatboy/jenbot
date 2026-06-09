from aiogram.exceptions import TelegramAPIError
from typing import Optional

from domain.services import UserService
from domain.objects import entities, exceptions
from bot.core import BotProtocol


class UserActions:

    def __init__(self, user_service: UserService, bot: BotProtocol):
        self.user_service = user_service
        self.bot = bot

    async def get_telegram_user(
        self, username: str | int, chat_id: Optional[int] = None
    ) -> entities.UserEntity:
        if isinstance(username, str):
            return await self.user_service.get_by_username(username)

        try:
            chat = await self.bot.get_chat(username)
            usernames = chat.active_usernames
            return await self.user_service.get_or_create(chat.id, usernames)
        except TelegramAPIError:
            pass

        if chat_id:
            try:
                member = await self.bot.get_chat_member(chat_id, username)

                try:
                    chat = await self.bot.get_chat(member.user.id)
                    usernames = chat.active_usernames
                except TelegramAPIError:
                    usernames = [member.user.username]

                return await self.user_service.get_or_create(member.user.id, usernames)
            except TelegramAPIError:
                pass

        raise exceptions.UserNotFoundException(str(username))
