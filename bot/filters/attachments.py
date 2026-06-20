from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from bot.data import states


class CollectAttachmentsFilter(BaseFilter):
    async def __call__(self, event, state: FSMContext) -> bool:
        current = await state.get_state()
        return current in {
            states.ReportState.attachments.state,
            states.ScamReportState.attachments.state,
        }
