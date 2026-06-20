from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from contextlib import suppress
from aiogram import Router
from typing import List

from domain.services import ModerationService, TradingService
from bot.data import states, callbacks, keyboards, text
from bot.actions import ModerationActions, MediaActions
from bot.filters import CollectAttachmentsFilter
from domain.objects import entities, dtos
from bot.core.settings import Settings


attachments_router = Router()


@attachments_router.message(
    CollectAttachmentsFilter(),
    flags={"collect_files": True},
)
async def collect_attachment_handler(
    message: Message,
    file_ids: List[str],
    state: FSMContext,
    settings: Settings,
):
    data = await state.get_data()
    attachments = list(data.get("attachments", []))
    new_ids = [file_id for file_id in file_ids if file_id not in attachments]
    duplicates = len(file_ids) - len(new_ids)
    current_state = await state.get_state()
    allow_skip = current_state == states.ReportState.attachments.state
    keyboard = keyboards.get_attachments_keyboard(
        message.from_user.id, len(attachments), allow_skip
    )

    if not new_ids:
        await message.answer(
            text.ATTACHMENTS_DUPLICATES_ONLY.format(len(attachments), duplicates),
            reply_markup=keyboard,
        )
        return

    if len(attachments) + len(new_ids) > settings.MAX_ATTACHMENTS:
        await message.answer(
            text.ATTACHMENTS_LIMIT.format(settings.MAX_ATTACHMENTS),
            reply_markup=keyboard,
        )
        return

    attachments.extend(new_ids)
    await state.update_data(attachments=attachments)
    keyboard = keyboards.get_attachments_keyboard(
        message.from_user.id, len(attachments), allow_skip
    )

    response = text.ATTACHMENTS_RECEIVED.format(
        len(new_ids),
        len(attachments),
        settings.MAX_ATTACHMENTS,
    )

    if duplicates:
        response += text.ATTACHMENTS_DUPLICATES_SUFFIX.format(duplicates)

    await message.answer(response, reply_markup=keyboard)


@attachments_router.callback_query(
    callbacks.AttachmentsPreviewCallback.filter(),
    CollectAttachmentsFilter(),
)
async def attachments_preview_handler(
    callback: CallbackQuery,
    callback_data: callbacks.AttachmentsPreviewCallback,
    state: FSMContext,
    media_actions: MediaActions,
):
    if callback.from_user.id != callback_data.user_id:
        return

    data = await state.get_data()
    attachments = list(data.get("attachments", []))

    if not attachments:
        await callback.answer(text.ATTACHMENTS_PREVIEW_EMPTY, show_alert=True)
        return

    await callback.answer()
    loading = await callback.message.answer(text.ATTACHMENTS_PREVIEW_LOADING)
    
    try:
        await media_actions.send_preview(
            callback.message.chat.id,
            attachments,
        )
    finally:
        with suppress(TelegramBadRequest):
            await loading.delete()


@attachments_router.callback_query(
    callbacks.AttachmentsClearCallback.filter(),
    CollectAttachmentsFilter(),
)
async def attachments_clear_handler(
    callback: CallbackQuery,
    callback_data: callbacks.AttachmentsClearCallback,
    state: FSMContext,
):
    if callback.from_user.id != callback_data.user_id:
        return

    await callback.answer()
    await state.update_data(attachments=[])
    current_state = await state.get_state()
    allow_skip = current_state == states.ReportState.attachments.state

    await callback.message.edit_text(
        text.ATTACHMENTS_CLEARED,
        reply_markup=keyboards.get_attachments_keyboard(
            callback.from_user.id, 0, allow_skip
        ),
    )


@attachments_router.callback_query(
    callbacks.AttachmentsDoneCallback.filter(),
    CollectAttachmentsFilter(),
)
async def attachments_done_handler(
    callback: CallbackQuery,
    callback_data: callbacks.AttachmentsDoneCallback,
    state: FSMContext,
    moderation_service: ModerationService,
    trading_service: TradingService,
    user: entities.UserEntity,
    moderation_actions: ModerationActions,
):
    if callback.from_user.id != callback_data.user_id:
        return

    data = await state.get_data()
    attachments = list(data.get("attachments", []))

    if not attachments:
        await callback.answer(text.ATTACHMENTS_DONE_EMPTY, show_alert=True)
        return

    await callback.answer()
    current_state = await state.get_state()
    submitting_text = (
        text.REPORT_SUBMITTING
        if current_state == states.ReportState.attachments.state
        else text.SCAM_REPORT_SUBMITTING
    )
    await callback.message.edit_text(submitting_text)
    await state.clear()

    if current_state == states.ReportState.attachments.state:
        dto = dtos.AddReportDTO(
            reason=data["reason"],
            attachments=attachments,
            type=data["type"],
            user_id=user.id,
            accused_user_id=data.get("accused_user_id"),
        )
        report = await moderation_service.add_report(dto)
        await moderation_actions.publish_report(report.id)
        await callback.message.edit_text(
            text.REPORT_WITH_ATTACHMENTS_SUCCESS.format(len(attachments))
        )
    elif current_state == states.ScamReportState.attachments.state:
        dto = dtos.CreateScamReportDTO(
            description=data["description"],
            contact_info=data["contact_info"],
            attachments=attachments,
            user_id=user.id,
        )
        report = await trading_service.create_scam_report(dto)
        await moderation_actions.send_scam_report_message(report.id)
        await callback.message.edit_text(
            text.REPORT_WITH_ATTACHMENTS_SUCCESS.format(len(attachments))
        )


@attachments_router.callback_query(
    callbacks.SkipCallback.filter(),
    StateFilter(states.ReportState.attachments),
)
async def attachments_skip_handler(
    callback: CallbackQuery,
    callback_data: callbacks.SkipCallback,
    state: FSMContext,
    moderation_service: ModerationService,
    user: entities.UserEntity,
    moderation_actions: ModerationActions,
):
    if callback.from_user.id != callback_data.user_id:
        return

    data = await state.get_data()
    attachments = list(data.get("attachments", []))

    if attachments:
        await callback.answer(text.ATTACHMENTS_SKIP_FORBIDDEN, show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(text.REPORT_SUBMITTING)
    await state.update_data(attachments=[])
    dto = dtos.AddReportDTO(
        reason=data["reason"],
        attachments=[],
        type=data["type"],
        user_id=user.id,
        accused_user_id=data.get("accused_user_id"),
    )
    report = await moderation_service.add_report(dto)
    await moderation_actions.publish_report(report.id)
    await callback.message.edit_text(text.REPORT_SUCCESS)
    await state.clear()
