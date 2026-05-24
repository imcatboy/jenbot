from aiogram.exceptions import TelegramAPIError
from aiogram.types import InputMediaPhoto, InputMediaVideo, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import F, Bot, Router
from typing import List
from html import escape

from bot.data import states, callbacks, keyboards, text
from domain.objects import exceptions, dtos, types, entities
from domain.services import UserService, ModerationService
from domain.objects.types import ReportStatus, ReportType
from bot.actions import ModerationActions, UserActions


report_router = Router()


@report_router.message(Command("report", "rep", ignore_case=True))
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

    if reports:
        await callback.message.edit_text(text.REPORT_ALREADY_PENDING)
        return

    await state.update_data(type=callback_data.type)

    if callback_data.type in [types.ReportType.SCAM, types.ReportType.VIOLATION]:
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


@report_router.message(
    states.ReportState.accused_user_id, flags={"cast": types.UsernameOrID}
)
async def accused_user_id_handler(
    message: Message,
    state_data: types.UsernameOrID,
    user_actions: UserActions,
    state: FSMContext,
):
    try:
        accused_user = await user_actions.get_telegram_user(state_data)
    except exceptions.UserNotFoundException:
        if isinstance(state_data, str):
            await message.answer(
                text.REPORT_USERNAME_NOT_FOUND.format(escape(state_data))
            )
            return

        await state.update_data(accused_user_id=state_data)
        await state.set_state(states.ReportState.username)
        await message.answer(
            text.REPORT_USERNAME_MESSAGE,
            reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
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
    accused_user = await user_service.get_or_create(telegram_id, state_data)
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
    await message.answer(text.REPORT_SUCCESS)


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


@report_router.message(Command("check"), flags={"command_model": dtos.CheckCommandDTO})
async def check_handler(
    message: Message,
    command_data: dtos.CheckCommandDTO,
    user_actions: UserActions,
    user_service: UserService,
    moderation_service: ModerationService,
):
    try:
        user = await user_actions.get_telegram_user(command_data.username)
        reputation = await user_service.get_user_reputation(user.id)
        reports = await moderation_service.get_reports(
            dtos.GetReportsDTO(
                accused_user_id=user.id,
                status=ReportStatus.APPROVED,
                type=ReportType.SCAM,
            )
        )
    except (exceptions.UserNotFoundException, exceptions.ObjectNotFoundException):
        await message.answer(text.get_check_error_message(str(command_data.username)))
        return

    await message.answer(
        text.get_check_success_message(reputation),
        reply_markup=keyboards.get_check_keyboard(reports),
    )


@report_router.callback_query(callbacks.CheckCallback.filter())
async def check_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.CheckCallback,
    moderation_service: ModerationService,
    bot: Bot,
):
    report = await moderation_service.get_user_report(
        dtos.GetUserReportDTO(
            report_id=callback_data.report_id,
            status=ReportStatus.APPROVED,
            type=ReportType.SCAM,
        )
    )

    if report.attachments:
        attachments = []
        has_caption = False

        for attachment in report.attachments:
            try:
                file = await bot.get_file(attachment)

                if "photo" in file.file_path:
                    attachments.append(
                        InputMediaPhoto(
                            media=file.file_id,
                            caption=report.reason if not has_caption else None,
                        )
                    )
                elif "video" in file.file_path:
                    attachments.append(
                        InputMediaVideo(
                            media=file.file_id,
                            caption=report.reason if not has_caption else None,
                        )
                    )

                has_caption = True
            except TelegramAPIError:
                continue

        if attachments:
            await callback.message.answer_media_group(attachments)
            return

    await callback.message.answer(report.reason)
