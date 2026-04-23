from aiogram.exceptions import TelegramAPIError

from domain.services import UserService
from domain.objects import entities, exceptions
from bot.core import BotProtocol


class UserActions:
    
    def __init__(self, user_service: UserService, bot: BotProtocol):
        self.user_service = user_service
        self.bot = bot
    
    async def get_telegram_user(self, username: str | int) -> entities.UserEntity:
        try:
            if isinstance(username, str):
                return await self.user_service.get_by_username(username)
            
            chat = await self.bot.get_chat(username)
            return await self.user_service.get_or_create(chat.id, chat.username)
        except (exceptions.ObjectNotFoundException, TelegramAPIError):
            raise exceptions.UserNotFoundException(str(username))