from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

from bot.data import text


user_router = Router()


@user_router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(text.HELP_MESSAGE)