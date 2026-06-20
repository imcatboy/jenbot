from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram import F, Bot, Router

from domain.services import UserService, ModerationService, TradingService
from domain.objects import exceptions, dtos, types, entities
from domain.objects.types import ReportStatus, UserRole
from bot.data import states, callbacks, keyboards, text
from bot.filters import GroupsFilter, UsersFilter
from bot.actions import ModerationActions


report_router = Router()


@report_router.message(
    Command("report", "rep", ignore_case=True), GroupsFilter([ChatType.PRIVATE])
)
async def report_handler(message: Message):
    await message.answer(
        text.REPORT_TYPE_MESSAGE, reply_markup=keyboards.REPORT_TYPE_KEYBOARD
    )


@report_router.callback_query(
    F.data == "dispute_report",
    GroupsFilter([ChatType.PRIVATE]),
)
async def dispute_report_handler(
    callback: CallbackQuery,
    user: entities.UserEntity,
    moderation_service: ModerationService,
    state: FSMContext,
):
    reports = await moderation_service.get_reports(
        dtos.GetReportsDTO(user_id=user.id, status=ReportStatus.PENDING)
    )

    if reports and user.role == UserRole.USER:
        await callback.answer()
        await callback.message.answer(text.REPORT_ALREADY_PENDING)
        return

    await state.update_data(type=types.ReportType.UNBAN)
    await state.set_state(states.ReportState.reason)
    await callback.answer()
    await callback.message.answer(
        text.REPORT_REASON_MESSAGE, reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id)
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
            reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id),
        )
        return

    await state.set_state(states.ReportState.reason)
    await callback.message.edit_text(
        text.REPORT_REASON_MESSAGE, reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id)
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
    await state.update_data(reason=state_data, attachments=[])
    await state.set_state(states.ReportState.attachments)
    await message.answer(
        text.REPORT_ATTACHMENTS_MESSAGE,
        reply_markup=keyboards.get_attachments_keyboard(
            message.from_user.id, 0, allow_skip=True
        ),
    )


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
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )


@report_router.callback_query(
    F.data == "create_scam_report",
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def create_scam_report_handler(
    callback: CallbackQuery,
    user: entities.UserEntity,
    trading_service: TradingService,
    state: FSMContext,
):
    scam_report_count = await trading_service.get_user_scam_report_count(
        user.id, types.ReportStatus.PENDING
    )

    if scam_report_count >= 3:
        await callback.answer()
        await callback.message.answer(text.SCAM_REPORT_COUNT_MESSAGE)
        return

    await state.set_state(states.ScamReportState.description)
    await callback.answer()
    await callback.message.answer(
        text.SCAM_REPORT_DESCRIPTION_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id),
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
    await state.update_data(contact_info=state_data, attachments=[])
    await state.set_state(states.ScamReportState.attachments)
    await message.answer(
        text.SCAM_REPORT_ATTACHMENTS_MESSAGE,
        reply_markup=keyboards.get_attachments_keyboard(
            message.from_user.id, 0, allow_skip=False
        ),
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

    await state.update_data(contact_info=None, attachments=[])
    await state.set_state(states.ScamReportState.attachments)
    await callback.answer()
    await callback.message.answer(
        text.SCAM_REPORT_ATTACHMENTS_MESSAGE,
        reply_markup=keyboards.get_attachments_keyboard(
            callback.from_user.id, 0, allow_skip=False
        ),
    )


@report_router.message(
    Command("reputation", ignore_case=True),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def reputation_handler(
    message: Message,
    user: entities.UserEntity,
    moderation_service: ModerationService,
    state: FSMContext,
):
    if await moderation_service.has_active_reputation_request(user.id):
        await message.answer(text.REPUTATION_REQUEST_EXISTS)
        return

    await state.set_state(states.ReputationRequestState.about)
    await message.answer(
        text.REPUTATION_REQUEST_MESSAGE,
        reply_markup=keyboards.get_skip_keyboard(message.from_user.id),
    )


@report_router.message(
    states.ReputationRequestState.about,
    GroupsFilter([ChatType.PRIVATE]),
    flags={"cast": types.Reason},
)
async def reputation_request_about_handler(
    message: Message,
    state_data: types.Reason,
    state: FSMContext,
    moderation_service: ModerationService,
    user: entities.UserEntity,
    moderation_actions: ModerationActions,
):
    reputation_request = await moderation_service.create_reputation_request(
        user.id, state_data
    )
    reputation_request = await moderation_service.get_reputation_request(
        reputation_request.id
    )
    await moderation_actions.send_reputation_request_message(reputation_request)
    await message.answer(text.REPUTATION_REQUEST_SUCCESS)
    await state.clear()


@report_router.callback_query(
    callbacks.SkipCallback.filter(),
    states.ReputationRequestState.about,
    GroupsFilter([ChatType.PRIVATE]),
)
async def reputation_request_accept_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.SkipCallback,
    state: FSMContext,
    user: entities.UserEntity,
    moderation_service: ModerationService,
    moderation_actions: ModerationActions,
):
    if callback.from_user.id != callback_data.user_id:
        return

    await state.clear()
    reputation_request = await moderation_service.create_reputation_request(user.id)
    reputation_request = await moderation_service.get_reputation_request(
        reputation_request.id
    )
    await moderation_actions.send_reputation_request_message(reputation_request)
    await callback.answer()
    await callback.message.answer(text.REPUTATION_REQUEST_SUCCESS)


@report_router.callback_query(
    callbacks.ReputationRequestCallback.filter(F.is_accepted == True),
    UsersFilter([UserRole.ADMIN, UserRole.MODERATOR]),
)
async def reputation_request_accept_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ReputationRequestCallback,
    user: entities.UserEntity,
    moderation_service: ModerationService,
    moderation_actions: ModerationActions,
):
    await moderation_service.update_reputation_request(callback_data.id, user.id, True)
    reputation_request = await moderation_service.get_reputation_request(
        callback_data.id
    )
    await moderation_actions.send_reputation_request_updated_message(user)
    await callback.message.edit_text(
        text.get_reputation_request_message(reputation_request),
    )
    await callback.answer()
    await callback.message.answer(text.REPUTATION_REQUEST_SUCCESS)


@report_router.callback_query(
    callbacks.ReputationRequestCallback.filter(F.is_accepted == False),
    UsersFilter([UserRole.ADMIN, UserRole.MODERATOR]),
)
async def reputation_request_reject_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ReputationRequestCallback,
    state: FSMContext,
):
    await state.set_state(states.ReputationRequestAcceptState.comment)
    await state.update_data(id=callback_data.id, message_id=callback.message.message_id)
    await callback.answer()
    await callback.message.answer(text.REPUTATION_REQUEST_COMMENT_MESSAGE)


@report_router.message(
    states.ReputationRequestAcceptState.comment,
    UsersFilter([UserRole.ADMIN, UserRole.MODERATOR]),
    flags={"cast": types.Text},
)
async def reputation_request_comment_handler(
    message: Message,
    state_data: types.Text,
    state: FSMContext,
    moderation_service: ModerationService,
    user: entities.UserEntity,
    moderation_actions: ModerationActions,
    bot: Bot,
):
    await state.update_data(comment=state_data)
    data = await state.get_data()
    await moderation_service.update_reputation_request(data["id"], user.id, False)
    await state.clear()
    reputation_request = await moderation_service.get_reputation_request(data["id"])
    await bot.edit_message_text(
        text.get_reputation_request_message(reputation_request),
        chat_id=message.chat.id,
        message_id=data["message_id"],
    )
    await moderation_actions.send_reputation_request_updated_message(
        reputation_request.user, data["comment"]
    )
    await message.answer(text.REPUTATION_REQUEST_COMMENT_SUCCESS)
