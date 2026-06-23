from aiogram.filters import BaseFilter
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from bot.data.deep_link import parse_check_start_payload


class CheckStartDeepLinkFilter(BaseFilter):

    async def __call__(
        self, message: Message, command: CommandObject | None = None
    ) -> bool | dict[str, str]:
        if command is None:
            return False

        search = parse_check_start_payload(command.args)
        
        if search is None:
            return False

        return {"check_search": search}
