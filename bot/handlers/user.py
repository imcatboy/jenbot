from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatType
from aiogram.types import Message
from aiogram import Router

from bot.filters import GroupsFilter
from bot.data import text, keyboards

user_router = Router()


@user_router.message(
    Command("help", ignore_case=True), GroupsFilter([ChatType.PRIVATE])
)
@user_router.message(CommandStart(ignore_case=True), GroupsFilter([ChatType.PRIVATE]))
async def start_handler(message: Message):
    await message.answer(text.START_MESSAGE, reply_markup=keyboards.START_KEYBOARD)
