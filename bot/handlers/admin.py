import json

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router, Bot
from html import escape

from domain.services import ConfigService, ModerationService
from bot.data import text, callbacks, states, keyboards
from domain.objects import dtos, types, entities
from domain.objects.types import UserRole
from bot.actions import ModerationActions
from bot.filters import UsersFilter

admin_router = Router()
admin_router.message.filter(UsersFilter([UserRole.ADMIN]))
admin_router.callback_query.filter(UsersFilter([UserRole.ADMIN]))


@admin_router.message(
    Command("setsetting", "ss", ignore_case=True),
    flags={
        "command_model": dtos.SetSettingCommandDTO,
    },
)
async def setsetting_handler(
    message: Message,
    command_data: dtos.SetSettingCommandDTO,
    config_service: ConfigService,
):
    await config_service.set(command_data.name, json.loads(command_data.value))
    await message.answer(text.SET_SETTING_SUCCESS.format(escape(command_data.name)))


@admin_router.callback_query(callbacks.ReportStatusCallback.filter())
async def reportstatus_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ReportStatusCallback,
    state: FSMContext,
):
    await state.update_data(
        report_message_id=callback.message.message_id,
        report_id=callback_data.id,
        status=callback_data.status,
    )
    await state.set_state(states.AdminReportState.report_status)
    await callback.message.reply(
        text.REPORT_COMMENT_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(callback.message.from_user.id),
    )


@admin_router.message(
    states.AdminReportState.report_status,
    flags={"cast": types.Text},
)
async def reportstatus_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
    user: entities.UserEntity,
    moderation_service: ModerationService,
    moderation_actions: ModerationActions,
):
    await state.update_data(admin_comment=message.text)
    data = await state.get_data()
    await state.clear()
    dto = dtos.UpdateReportDTO(
        status=data["status"],
        admin_comment=data["admin_comment"],
        applied_by_user_id=user.id,
    )
    await moderation_service.update_report(data["report_id"], dto)
    report = await moderation_service.get_report(data["report_id"])
    await bot.edit_message_text(
        text.get_report_message(report),
        chat_id=message.chat.id,
        message_id=data["report_message_id"],
        reply_markup=keyboards.get_report_keyboard(report),
    )
    await moderation_actions.send_report_updated_message(report)
    await message.answer(text.REPORT_STATUS_UPDATED)
