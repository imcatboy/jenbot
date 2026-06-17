from aiogram.exceptions import TelegramAPIError
from typing import Optional

from domain.objects import entities, exceptions
from domain.services import UserService
from bot.core import BotProtocol


class UserActions:

    def __init__(self, user_service: UserService, bot: BotProtocol):
        self.user_service = user_service
        self.bot = bot

    async def get_telegram_user(
        self, username_or_id: str | int, chat_id: Optional[int] = None
    ) -> entities.UserEntity:

        if isinstance(username_or_id, str):
            return await self.user_service.get_by_username(username_or_id.lower())

        collected_usernames = set()

        if chat_id:
            try:
                member = await self.bot.get_chat_member(
                    chat_id=chat_id, user_id=username_or_id
                )

                if member.user.username:
                    collected_usernames.add(member.user.username.lower())
            except TelegramAPIError:
                pass

        try:
            chat = await self.bot.get_chat(username_or_id)

            if chat.active_usernames:
                for username in chat.active_usernames:
                    collected_usernames.add(username.lower())
            elif chat.username:
                collected_usernames.add(chat.username.lower())
        except TelegramAPIError:
            pass

        if collected_usernames or chat_id:
            return await self.user_service.get_or_create(
                telegram_id=username_or_id, usernames=list(collected_usernames)
            )

        raise exceptions.UserNotFoundException(str(username_or_id))
