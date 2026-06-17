from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatType
from typing import List


class GroupsFilter(BaseFilter):
    def __init__(self, group_types: List[ChatType]) -> None:
        self.group_types = group_types

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        if isinstance(event, CallbackQuery):
            return event.message.chat.type in self.group_types

        return event.chat.type in self.group_types
