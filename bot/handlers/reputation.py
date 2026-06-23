from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
    CallbackQuery,
)
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType
from aiogram import F, Bot, Router
from contextlib import suppress
from typing import Optional

from bot.filters import GroupsFilter, UsersFilter, CheckStartDeepLinkFilter
from bot.actions import MediaActions, ModerationActions, ReputationActions
from domain.objects.types import UserRole, UserReputationRole
from domain.objects import dtos, exceptions, entities, types
from domain.services import UserService, TradingService
from bot.data import states, text, keyboards, callbacks
from bot.actions import UserActions


reputation_router = Router()


@reputation_router.message(
    CommandStart(deep_link=True),
    CheckStartDeepLinkFilter(),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def start_check_handler(
    message: Message,
    check_search: str,
    reputation_actions: ReputationActions,
):
    await reputation_actions.send_check(message, check_search)


@reputation_router.message(
    Command("check", ignore_case=True),
    flags={"command_model": dtos.CheckCommandDTO, "subscriptions": True},
)
async def check_handler(
    message: Message,
    command_data: dtos.CheckCommandDTO,
    reputation_actions: ReputationActions,
    reply_to_user: Optional[entities.UserEntity] = None,
):
    if reply_to_user:
        await reputation_actions.send_check_by_reply(message, reply_to_user)
        return

    await reputation_actions.send_check(message, command_data.search)


@reputation_router.callback_query(
    F.data == "check_user",
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def check_user_callback_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(states.CheckState.search)
    await callback.message.answer(
        text.CHECK_USER_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id),
    )
    await callback.answer()


@reputation_router.message(
    states.CheckState.search,
    flags={"cast": types.Text},
)
async def check_user_search_handler(
    message: Message,
    state_data: types.Text,
    state: FSMContext,
    reputation_actions: ReputationActions,
):
    await state.clear()
    await reputation_actions.send_check(message, state_data)


@reputation_router.message(
    Command("me", ignore_case=True),
    flags={"subscriptions": True},
)
async def me_handler(
    message: Message,
    user: entities.UserEntity,
    reputation_actions: ReputationActions,
):
    await reputation_actions.send_own_reputation(message, user.id)


@reputation_router.callback_query(
    F.data == "my_reputation",
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def my_reputation_callback_handler(
    callback: CallbackQuery,
    user: entities.UserEntity,
    reputation_actions: ReputationActions,
):
    await reputation_actions.send_own_reputation(callback.message, user.id)


@reputation_router.callback_query(
    callbacks.ReputationUserCallback.filter(), flags={"subscriptions": True}
)
async def reputation_user_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ReputationUserCallback,
    user_service: UserService,
    reputation_actions: ReputationActions,
    media_actions: MediaActions,
):
    try:
        reputation_user = await user_service.get_reputation_user(callback_data.id)
    except exceptions.ObjectNotFoundException:
        await callback.answer()
        await callback.message.answer_photo(
            photo=await media_actions.get_telegram_file("unknown_user"),
            caption=text.get_check_error_message(),
        )
        return

    await callback.answer()
    loading = await callback.message.answer(text.PLEASE_WAIT_MESSAGE)

    try:
        await reputation_actions.send_card(callback.message, reputation_user)
    finally:
        with suppress(TelegramBadRequest):
            await loading.delete()


@reputation_router.callback_query(
    callbacks.CheckCallback.filter(),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def check_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.CheckCallback,
    trading_service: TradingService,
    media_actions: MediaActions,
):
    await callback.answer()
    loading = await callback.message.answer(text.PLEASE_WAIT_MESSAGE)
    scam_report = await trading_service.get_scam_report(
        callback_data.report_id,
    )
    attachments = await media_actions.create_media_group(
        scam_report.attachments, scam_report.description
    )

    if not attachments:
        await loading.edit_text(text.ATTACHMENTS_UNAVAILABLE)
        return

    await callback.message.answer_media_group(attachments)

    with suppress(TelegramBadRequest):
        await loading.delete()


@reputation_router.callback_query(
    callbacks.ScamReportAcceptCallback.filter(),
    UsersFilter([UserRole.ADMIN, UserRole.MODERATOR]),
)
async def scam_report_accept_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ScamReportAcceptCallback,
    trading_service: TradingService,
    user: entities.UserEntity,
):
    try:
        await trading_service.update_scam_report(
            callback_data.id, dtos.UpdateScamReportDTO(applied_by_user_id=user.id)
        )
        report = await trading_service.get_scam_report(callback_data.id)
        await callback.message.edit_text(
            text.get_scam_report_message(report),
            reply_markup=keyboards.get_scam_report_keyboard(report),
        )
    except exceptions.ObjectNotFoundException:
        await callback.answer()
        await callback.message.answer(text.OBJECT_NOT_FOUND)


@reputation_router.callback_query(
    callbacks.ScamReportStatusCallback.filter(),
    UsersFilter([UserRole.ADMIN, UserRole.MODERATOR]),
)
async def scam_report_status_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ScamReportStatusCallback,
    trading_service: TradingService,
    user: entities.UserEntity,
    state: FSMContext,
):
    report = await trading_service.get_scam_report(callback_data.id)

    if report.applied_by_user_id is not None and report.applied_by_user_id != user.id:
        await callback.answer()
        await callback.message.answer(text.ACCESS_DENIED)
        return

    await state.update_data(
        scam_report_message_id=callback.message.message_id,
        scam_report_id=callback_data.id,
        status=callback_data.status,
    )
    await state.set_state(states.AnswerScamReportState.comment)
    await callback.answer()
    await callback.message.reply(
        text.REPORT_COMMENT_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(callback.message.from_user.id),
    )


@reputation_router.message(
    states.AnswerScamReportState.comment,
    UsersFilter([UserRole.ADMIN, UserRole.MODERATOR]),
    flags={"cast": types.Text},
)
async def answer_scam_report_comment_handler(
    message: Message,
    state: FSMContext,
    trading_service: TradingService,
    moderation_actions: ModerationActions,
    user: entities.UserEntity,
    bot: Bot,
):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    dto = dtos.UpdateScamReportDTO(
        status=data["status"],
        comment=data["comment"],
        applied_by_user_id=user.id,
    )
    await trading_service.update_scam_report(data["scam_report_id"], dto)
    report = await trading_service.get_scam_report(data["scam_report_id"])
    await bot.edit_message_text(
        text.get_scam_report_message(report),
        chat_id=message.chat.id,
        message_id=data["scam_report_message_id"],
        reply_markup=keyboards.get_scam_report_keyboard(report),
    )
    await moderation_actions.send_scam_report_updated_message(report)
    await message.answer(text.REPORT_STATUS_UPDATED)
    await state.clear()


@reputation_router.message(
    Command("review", ignore_case=True),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"command_model": dtos.ReviewCommandDTO, "subscriptions": True},
)
async def review_handler(
    message: Message,
    command_data: dtos.ReviewCommandDTO,
    user_service: UserService,
    user_actions: UserActions,
    user: entities.UserEntity,
    state: FSMContext,
    trading_service: TradingService,
):
    try:
        target_user = await user_actions.get_telegram_user(command_data.username)
        reputation_user = await user_service.get_reputation_user_by_user_id(
            target_user.id
        )

        if reputation_user.role == UserReputationRole.SCAMMER:
            await message.answer(text.USER_IS_SCAMMER)
            return
    except exceptions.ObjectNotFoundException:
        await message.answer(text.USER_NOT_HAS_REPUTATION_USER)
        return

    if await trading_service.review_exists(user.id, target_user.id, reputation_user.id):
        await message.answer(text.REVIEW_ALREADY_EXISTS)
        return

    await state.update_data(user_id=target_user.id)
    await state.set_state(states.ReviewState.rating)
    await message.answer(
        text.REVIEW_RATING_MESSAGE, reply_markup=keyboards.REVIEW_RATING_KEYBOARD
    )


@reputation_router.callback_query(
    callbacks.ReviewCallback.filter(),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def review_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ReviewCallback,
    user_service: UserService,
    user: entities.UserEntity,
    trading_service: TradingService,
    state: FSMContext,
):
    try:
        target_user = await user_service.get_by_id(callback_data.user_id)
        reputation_user = await user_service.get_reputation_user_by_user_id(
            target_user.id
        )

        if reputation_user.role == UserReputationRole.SCAMMER:
            await callback.message.answer(text.USER_IS_SCAMMER)
            return
    except exceptions.ObjectNotFoundException:
        await callback.message.answer(text.USER_NOT_HAS_REPUTATION_USER)
        return

    if await trading_service.review_exists(user.id, target_user.id, reputation_user.id):
        await callback.message.answer(text.REVIEW_ALREADY_EXISTS)
        return

    await state.update_data(user_id=target_user.id)
    await state.set_state(states.ReviewState.rating)
    await callback.message.answer(
        text.REVIEW_RATING_MESSAGE, reply_markup=keyboards.REVIEW_RATING_KEYBOARD
    )


@reputation_router.callback_query(
    callbacks.ReviewRatingCallback.filter(),
    states.ReviewState.rating,
    GroupsFilter([ChatType.PRIVATE]),
)
async def review_rating_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ReviewRatingCallback,
    state: FSMContext,
):
    await state.update_data(rating=callback_data.rating)
    await state.set_state(states.ReviewState.message)
    await callback.answer()
    await callback.message.answer(
        text.REVIEW_MESSAGE_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(callback.message.from_user.id),
    )


@reputation_router.message(
    states.ReviewState.message,
    GroupsFilter([ChatType.PRIVATE]),
    flags={"cast": types.Text},
)
async def review_message_handler(
    message: Message,
    user: entities.UserEntity,
    state: FSMContext,
    trading_service: TradingService,
):
    await state.update_data(message=message.text)
    data = await state.get_data()
    await state.clear()
    dto = dtos.CreateReviewDTO(
        author_id=user.id,
        subject_user_id=data["user_id"],
        rating=data["rating"],
        message=data["message"],
    )
    await trading_service.create_review(dto)
    await message.answer(text.REVIEW_SUCCESS)


@reputation_router.callback_query(
    callbacks.ReviewsCallback.filter(),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def reviews_callback(
    callback: CallbackQuery,
    callback_data: callbacks.ReviewsCallback,
    trading_service: TradingService,
    user_service: UserService,
):
    reputation_user = await user_service.get_reputation_user(
        callback_data.reputation_user_id
    )
    dto = dtos.GetReviewsDTO(
        reputation_user_id=reputation_user.id,
        limit=6,
        offset=callback_data.offset,
    )
    reviews = await trading_service.get_reviews(dto)
    has_more = len(reviews) == dto.limit
    reviews = reviews[:-1] if has_more else reviews

    if callback_data.new_message:
        await callback.answer()
        await callback.message.answer(
            text.get_reviews_message(reputation_user, reviews),
            reply_markup=keyboards.get_reviews_keyboard(
                callback_data.offset,
                dto.limit - 1,
                callback_data.reputation_user_id,
                has_more,
            ),
        )
    else:
        await callback.answer()
        await callback.message.edit_text(
            text.get_reviews_message(reputation_user, reviews),
            reply_markup=keyboards.get_reviews_keyboard(
                callback_data.offset,
                dto.limit - 1,
                callback_data.reputation_user_id,
                has_more,
            ),
        )


@reputation_router.inline_query()
async def check_inline_handler(
    inline_query: InlineQuery,
    user_service: UserService,
):
    query_text = inline_query.query.strip()

    if not query_text or len(query_text) < 3:
        return

    reputation_users = await user_service.get_reputation_users(query_text)
    results = []

    if not reputation_users:
        results.append(
            InlineQueryResultArticle(
                id="unknown_user",
                title="Неизвестный пользователь",
                description=f"Подходящей записи по запросу {query_text} не найдено",
                input_message_content=InputTextMessageContent(
                    message_text=text.get_check_error_message(query_text)
                ),
            )
        )

    else:
        for reputation in reputation_users:
            description = text.format_reputation_user(reputation)
            caption_text = text.get_check_success_message(reputation)
            results.append(
                InlineQueryResultArticle(
                    id=f"rep_{reputation.id}",
                    title=f"{text.INLINE_REPUTATION_ROLES[reputation.role]}",
                    description=description,
                    input_message_content=InputTextMessageContent(
                        message_text=caption_text
                    ),
                )
            )

    await inline_query.answer(results, cache_time=5, is_personal=True)
