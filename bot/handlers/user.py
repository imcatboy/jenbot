from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatType
from aiogram.types import Message
from aiogram import Router, Bot

from bot.filters import GroupsFilter, CheckStartDeepLinkFilter
from bot.actions import ReputationActions
from bot.data import text, keyboards


user_router = Router()


@user_router.message(CommandStart(deep_link=False), GroupsFilter([ChatType.PRIVATE]))
async def start_handler(message: Message, bot: Bot):
    me = await bot.get_me()
    await message.answer(
        text.START_MESSAGE.format(bot_username=me.username),
        reply_markup=keyboards.START_KEYBOARD,
    )


@user_router.message(
    CommandStart(deep_link=True),
    CheckStartDeepLinkFilter(),
    GroupsFilter([ChatType.PRIVATE]),
)
async def start_check_handler(
    message: Message, check_search: str, reputation_actions: ReputationActions
):
    await reputation_actions.send_check(message, check_search)


@user_router.message(CommandStart(deep_link=True), GroupsFilter([ChatType.PRIVATE]))
async def start_unknown_deep_link_handler(message: Message, bot: Bot):
    me = await bot.get_me()
    await message.answer(
        text.START_MESSAGE.format(bot_username=me.username),
        reply_markup=keyboards.START_KEYBOARD,
    )


@user_router.message(
    Command("help", ignore_case=True), GroupsFilter([ChatType.PRIVATE])
)
async def help_handler(message: Message, bot: Bot):
    me = await bot.get_me()
    await message.answer(text.HELP_MESSAGE.format(bot_username=me.username))
