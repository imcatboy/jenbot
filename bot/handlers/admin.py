from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router, Bot
from html import escape

from domain.services import ConfigService, ModerationService, UserService
from domain.objects.types import UserRole, UserReputationRole
from bot.data import text, callbacks, states, keyboards
from domain.objects import dtos, types, entities
from bot.actions import UserActions
from bot.filters import UsersFilter

admin_router = Router()
admin_router.message.filter(UsersFilter([UserRole.ADMIN]))
admin_router.callback_query.filter(UsersFilter([UserRole.ADMIN]))


@admin_router.message(
    Command("setsetting"),
    flags={
        "command_model": dtos.SetSettingCommandDTO,
    },
)
async def setsetting_handler(
    message: Message,
    command_data: dtos.SetSettingCommandDTO,
    config_service: ConfigService,
):
    await config_service.set(command_data.name, command_data.value)
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
        text.REPORT_COMMENT_MESSAGE, reply_markup=keyboards.CANCEL_KEYBOARD
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
    await message.answer(text.REPORT_STATUS_UPDATED)


@admin_router.callback_query(callbacks.ReportAccusedUserCallback.filter())
async def reportaccusseduser_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ReportAccusedUserCallback,
    state: FSMContext,
):
    await state.update_data(accused_user_id=callback_data.id)
    await state.set_state(states.AdminScamReportState.description)
    await callback.message.reply(
        text.REPORT_ACCUSED_DESCRIPTION_MESSAGE, reply_markup=keyboards.CANCEL_KEYBOARD
    )


@admin_router.message(
    states.AdminScamReportState.description,
    flags={"cast": types.Reason},
)
async def reportaccusseduserdescription_handler(
    message: Message,
    state: FSMContext,
    user: entities.UserEntity,
    user_service: UserService,
):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await state.clear()
    dto = dtos.CreateUserReputationDTO(
        user_id=data["accused_user_id"],
        description=data["description"],
        added_by_user_id=user.id,
        role=UserReputationRole.SCAMMER,
    )
    await user_service.create_or_update_user_reputation(dto)
    await message.answer(text.REPORT_ACCUSED_USER_UPDATED)


@admin_router.message(
    Command("setreputation"),
    flags={"command_model": dtos.SetReputationCommandDTO},
)
async def setreputation_handler(
    message: Message,
    command_data: dtos.SetReputationCommandDTO,
    user: entities.UserEntity,
    state: FSMContext,
    user_actions: UserActions,
):
    user = await user_actions.get_telegram_user(command_data.username)
    await state.update_data(user_id=user.id)
    await state.set_state(states.AdminSetReputationState.role)
    await message.answer(text.SET_REPUTATION_ROLE_MESSAGE, reply_markup=keyboards.REPUTATION_ROLE_KEYBOARD)


@admin_router.callback_query(callbacks.ReputationRoleCallback.filter(), states.AdminSetReputationState.role)
async def reputationrole_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ReputationRoleCallback,
    state: FSMContext,
):
    await state.update_data(role=callback_data.role)
    await state.set_state(states.AdminSetReputationState.description)
    await callback.message.reply(text.SET_REPUTATION_DESCRIPTION_MESSAGE, reply_markup=keyboards.CANCEL_KEYBOARD)


@admin_router.message(
    states.AdminSetReputationState.description,
    flags={"cast": types.Text},
)
async def reputationdescription_handler(
    message: Message,
    state: FSMContext,
    user: entities.UserEntity,
    user_service: UserService,
):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await state.clear()
    dto = dtos.CreateUserReputationDTO(
        user_id=data["user_id"],
        description=data["description"],
        role=data["role"],
        added_by_user_id=user.id,
    )
    await user_service.create_or_update_user_reputation(dto)
    await message.answer(text.SET_REPUTATION_SUCCESS)


@admin_router.message(Command("addbanword"), flags={
    "command_model": dtos.AddBanWordCommandDTO,
})
async def addbanword_handler(
    message: Message,
    command_data: dtos.AddBanWordCommandDTO,
    moderation_service: ModerationService,
):
    await moderation_service.add_ban_word(command_data.word)
    await message.answer(text.ADD_BAN_WORD_SUCCESS.format(escape(command_data.word)))


@admin_router.message(Command("removebanword"), flags={
    "command_model": dtos.RemoveBanWordCommandDTO,
})
async def removebanword_handler(
    message: Message,
    command_data: dtos.RemoveBanWordCommandDTO,
    moderation_service: ModerationService,
):
    await moderation_service.remove_ban_word(command_data.word)
    await message.answer(text.REMOVE_BAN_WORD_SUCCESS.format(escape(command_data.word)))