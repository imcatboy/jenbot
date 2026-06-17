from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram import Router
from typing import List

from domain.services import UserService, ModerationService, TradingService
from domain.objects import exceptions, dtos, types, entities
from domain.objects.types import ReportStatus, UserRole
from bot.data import states, callbacks, keyboards, text
from bot.actions import ModerationActions
from bot.filters import GroupsFilter


report_router = Router()


@report_router.message(
    Command("report", "rep", ignore_case=True), GroupsFilter([ChatType.PRIVATE])
)
async def report_handler(message: Message):
    await message.answer(
        text.REPORT_TYPE_MESSAGE, reply_markup=keyboards.REPORT_TYPE_KEYBOARD
    )


@report_router.callback_query(callbacks.ReportCallback.filter())
async def report_callback_handler(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: callbacks.ReportCallback,
    user: entities.UserEntity,
    moderation_service: ModerationService,
):
    reports = await moderation_service.get_reports(
        dtos.GetReportsDTO(user_id=user.id, status=ReportStatus.PENDING)
    )

    if reports and user.role == UserRole.USER:
        await callback.message.edit_text(text.REPORT_ALREADY_PENDING)
        return

    await state.update_data(type=callback_data.type)

    if callback_data.type == types.ReportType.VIOLATION:
        await state.set_state(states.ReportState.accused_user_id)
        await callback.message.edit_text(
            text.REPORT_ACCUSED_USER_ID_MESSAGE,
            reply_markup=keyboards.get_cancel_keyboard(user.id),
        )
        return

    await state.set_state(states.ReportState.reason)
    await callback.message.edit_text(
        text.REPORT_REASON_MESSAGE, reply_markup=keyboards.get_cancel_keyboard(user.id)
    )


@report_router.message(states.ReportState.accused_user_id, flags={"cast": int})
async def accused_user_id_handler(
    message: Message,
    state_data: int,
    user_service: UserService,
    state: FSMContext,
):
    try:
        accused_user = await user_service.get_by_telegram_id(state_data)
    except exceptions.ObjectNotFoundException:
        await state.update_data(accused_user_id=state_data)
        await state.set_state(states.ReportState.username)
        await message.answer(
            text.REPORT_USERNAME_MESSAGE,
            reply_markup=keyboards.get_skip_keyboard(message.from_user.id),
        )
        return

    await state.update_data(accused_user_id=accused_user.id)
    await state.set_state(states.ReportState.reason)
    await message.answer(
        text.REPORT_REASON_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )


@report_router.message(states.ReportState.username, flags={"cast": types.Username})
async def username_handler(
    message: Message,
    state_data: types.Username,
    user_service: UserService,
    state: FSMContext,
):
    state_payload = await state.get_data()
    telegram_id = state_payload["accused_user_id"]
    accused_user = await user_service.get_or_create(telegram_id, [state_data.lower()])
    await state.update_data(accused_user_id=accused_user.id)
    await state.set_state(states.ReportState.reason)
    await message.answer(
        text.REPORT_REASON_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )


@report_router.message(states.ReportState.reason, flags={"cast": types.Text})
async def reason_handler(message: Message, state_data: types.Text, state: FSMContext):
    await state.update_data(reason=state_data)
    await state.set_state(states.ReportState.attachments)
    await message.answer(
        text.REPORT_ATTACHMENTS_MESSAGE,
        reply_markup=keyboards.get_skip_keyboard(message.from_user.id),
    )


@report_router.callback_query(
    callbacks.SkipCallback.filter(), states.ReportState.attachments
)
async def skip_handler(
    callback: CallbackQuery,
    callback_data: callbacks.SkipCallback,
    state: FSMContext,
    moderation_service: ModerationService,
    user: entities.UserEntity,
    moderation_actions: ModerationActions,
):
    if callback.from_user.id != callback_data.user_id:
        return

    await state.update_data(attachments=[])
    data = await state.get_data()
    dto = dtos.AddReportDTO(
        reason=data["reason"],
        attachments=data["attachments"],
        type=data["type"],
        user_id=user.id,
        accused_user_id=data.get("accused_user_id"),
    )
    report = await moderation_service.add_report(dto)
    await moderation_actions.publish_report(report.id)
    await callback.message.edit_text(text.REPORT_SUCCESS)
    await state.clear()


@report_router.message(states.ReportState.attachments, flags={"want_files": True})
async def attachments_handler(
    message: Message,
    file_ids: List[str],
    moderation_service: ModerationService,
    user: entities.UserEntity,
    state: FSMContext,
    moderation_actions: ModerationActions,
):
    await state.update_data(attachments=file_ids)
    data = await state.get_data()
    await state.clear()
    dto = dtos.AddReportDTO(
        reason=data["reason"],
        attachments=data["attachments"],
        type=data["type"],
        user_id=user.id,
        accused_user_id=data.get("accused_user_id"),
    )
    report = await moderation_service.add_report(dto)
    await moderation_actions.publish_report(report.id)
    await message.answer(text.REPORT_WITH_ATTACHMENTS_SUCCESS.format(len(file_ids)))


@report_router.callback_query(callbacks.CancelCallback.filter())
async def cancel_handler(
    callback: CallbackQuery,
    callback_data: callbacks.CancelCallback,
    state: FSMContext,
):
    if callback.from_user.id != callback_data.user_id:
        return

    await state.clear()
    await callback.message.edit_text(text.STATE_CANCELLED)


@report_router.message(
    Command("scam", ignore_case=True),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def scam_handler(
    message: Message,
    user: entities.UserEntity,
    trading_service: TradingService,
    state: FSMContext,
):
    scam_report_count = await trading_service.get_user_scam_report_count(
        user.id, types.ReportStatus.PENDING
    )

    if scam_report_count >= 3:
        await message.answer(text.SCAM_REPORT_COUNT_MESSAGE)
        return

    await state.set_state(states.ScamReportState.description)
    await message.answer(
        text.SCAM_REPORT_DESCRIPTION_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(user.id),
    )


@report_router.message(
    states.ScamReportState.description,
    flags={"cast": types.Text},
)
async def scam_report_description_handler(
    message: Message,
    state_data: types.Text,
    state: FSMContext,
):
    await state.update_data(description=state_data)
    await state.set_state(states.ScamReportState.contact_info)
    await message.answer(
        text.SCAM_REPORT_CONTACT_INFO_MESSAGE,
        reply_markup=keyboards.get_skip_keyboard(message.from_user.id),
    )


@report_router.message(
    states.ScamReportState.contact_info,
    flags={"cast": types.Text},
)
async def scam_report_contact_info_handler(
    message: Message,
    state_data: types.Text,
    state: FSMContext,
):
    await state.update_data(contact_info=state_data)
    await state.set_state(states.ScamReportState.attachments)
    await message.answer(
        text.SCAM_REPORT_ATTACHMENTS_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )


@report_router.callback_query(
    callbacks.SkipCallback.filter(), states.ScamReportState.contact_info
)
async def skip_handler(
    callback: CallbackQuery,
    callback_data: callbacks.SkipCallback,
    state: FSMContext,
):
    if callback.from_user.id != callback_data.user_id:
        return

    await state.update_data(contact_info=None)
    await state.set_state(states.ScamReportState.attachments)
    await callback.message.answer(
        text.SCAM_REPORT_ATTACHMENTS_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id),
    )


@report_router.message(
    states.ScamReportState.attachments,
    flags={"want_files": True},
)
async def scam_report_attachments_handler(
    message: Message,
    file_ids: List[str],
    state: FSMContext,
    trading_service: TradingService,
    user: entities.UserEntity,
    moderation_actions: ModerationActions,
):
    await state.update_data(attachments=file_ids)
    data = await state.get_data()
    dto = dtos.CreateScamReportDTO(
        description=data["description"],
        contact_info=data["contact_info"],
        attachments=data["attachments"],
        user_id=user.id,
    )
    report = await trading_service.create_scam_report(dto)
    await moderation_actions.send_scam_report_message(report.id)
    await message.answer(text.REPORT_WITH_ATTACHMENTS_SUCCESS.format(len(file_ids)))
    await state.clear()
