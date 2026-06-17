from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram import Router

from domain.services import UserService, TradingService
from bot.data import text, keyboards, callbacks
from bot.actions import MediaActions
from domain.objects import dtos, exceptions


reputation_router = Router()


@reputation_router.message(
    Command("check", ignore_case=True),
    flags={"command_model": dtos.CheckCommandDTO, "subscriptions": True},
)
async def check_handler(
    message: Message,
    command_data: dtos.CheckCommandDTO,
    media_actions: MediaActions,
    user_service: UserService,
    trading_service: TradingService,
):
    reputation_users = await user_service.get_reputation_users(command_data.search)

    if not reputation_users:
        image = await media_actions.get_telegram_file("unknown_user")
        await message.answer_photo(
            photo=image,
            caption=text.get_check_error_message(command_data.search),
        )
        return

    if len(reputation_users) > 1:
        await message.answer(
            text.MANY_REPUTATION_USERS,
            reply_markup=keyboards.get_reputation_user_keyboard(reputation_users),
        )
        return

    reputation = reputation_users[0]
    scam_reports = await trading_service.get_scam_reports(reputation.id)
    image = await media_actions.get_telegram_file(reputation.role.value)
    isPrivate = message.chat.type == ChatType.PRIVATE
    await message.answer_photo(
        photo=image,
        caption=text.get_check_success_message(reputation),
        reply_markup=keyboards.get_check_keyboard(scam_reports) if isPrivate else None,
    )


@reputation_router.callback_query(
    callbacks.ReputationUserCallback.filter(), flags={"subscriptions": True}
)
async def reputation_user_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ReputationUserCallback,
    user_service: UserService,
    media_actions: MediaActions,
    trading_service: TradingService,
):
    try:
        reputation_user = await user_service.get_reputation_user(callback_data.id)
    except exceptions.ObjectNotFoundException:
        image = await media_actions.get_telegram_file("unknown_user")
        await callback.message.answer_photo(
            photo=image,
            caption=text.get_check_error_message(),
        )
        return

    scam_reports = await trading_service.get_scam_reports(reputation_user.id)
    image = await media_actions.get_telegram_file(reputation_user.role.value)
    isPrivate = callback.message.chat.type == ChatType.PRIVATE
    await callback.message.answer_photo(
        photo=image,
        caption=text.get_check_success_message(reputation_user),
        reply_markup=keyboards.get_check_keyboard(scam_reports) if isPrivate else None,
    )


@reputation_router.callback_query(
    callbacks.CheckCallback.filter(), flags={"subscriptions": True}
)
async def check_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.CheckCallback,
    trading_service: TradingService,
    media_actions: MediaActions,
):
    scam_report = await trading_service.get_scam_report(
        callback_data.report_id,
    )
    attachments = await media_actions.create_media_group(
        scam_report.attachments, scam_report.description
    )
    await callback.message.answer_media_group(attachments)
