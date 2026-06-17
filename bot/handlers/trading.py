from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram import Bot, Router

from domain.objects import dtos, entities, types, exceptions, NoZeroInt
from domain.services import TradingService, UserService
from bot.data import text, keyboards, states, callbacks
from bot.filters import GroupsFilter
from bot.actions import UserActions


trading_router = Router()


@trading_router.message(
    Command("deal", ignore_case=True),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def deal_handler(message: Message, state: FSMContext):
    await message.answer(
        text.EXTERNAL_DEAL_BUYER_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )
    await state.set_state(states.ExternalDealState.buyer_id)


@trading_router.message(
    states.ExternalDealState.buyer_id,
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True, "cast": types.UsernameOrTelegramID},
)
async def deal_buyer_id_handler(
    message: Message,
    state_data: types.UsernameOrTelegramID,
    user_actions: UserActions,
    state: FSMContext,
):
    try:
        buyer = await user_actions.get_telegram_user(state_data.username)
    except exceptions.UserNotFoundException:
        await message.answer(text.DEAL_USER_NOT_FOUND.format(state_data.username))
        return

    await state.update_data(buyer_id=buyer.id)
    await message.answer(
        text.EXTERNAL_DEAL_DESCRIPTION_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )
    await state.set_state(states.ExternalDealState.description)


@trading_router.message(
    states.ExternalDealState.description,
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True, "cast": types.Reason},
)
async def deal_description_handler(
    message: Message,
    state_data: types.Reason,
    state: FSMContext,
):
    await state.update_data(description=state_data)
    await message.answer(
        text.EXTERNAL_DEAL_AMOUNT_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )
    await state.set_state(states.ExternalDealState.amount)


@trading_router.message(
    states.ExternalDealState.amount,
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True, "cast": NoZeroInt},
)
async def deal_amount_handler(
    message: Message,
    state_data: NoZeroInt,
    state: FSMContext,
):
    await state.update_data(amount=state_data)
    await message.answer(
        text.EXTERNAL_DEAL_AGENT_MESSAGE,
        reply_markup=keyboards.get_skip_keyboard(message.from_user.id),
    )
    await state.set_state(states.ExternalDealState.agent_id)


@trading_router.message(
    states.ExternalDealState.agent_id,
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True, "cast": types.UsernameOrTelegramID},
)
async def deal_agent_id_handler(
    message: Message,
    state_data: types.UsernameOrTelegramID,
    user_actions: UserActions,
    trading_service: TradingService,
    state: FSMContext,
    user: entities.UserEntity,
    user_service: UserService,
    bot: Bot,
):
    try:
        agent = await user_actions.get_telegram_user(state_data.username)
    except exceptions.UserNotFoundException:
        await message.answer(text.DEAL_USER_NOT_FOUND.format(state_data.username))
        return

    await state.update_data(agent_id=agent.id)
    data = await state.get_data()
    dto = dtos.CreateExternalDealDTO(
        seller_id=user.id,
        buyer_id=data["buyer_id"],
        agent_id=data["agent_id"],
        amount=data["amount"],
        description=data["description"],
        expires_at=datetime.now() + timedelta(days=1),
    )

    try:
        guarantor = await user_service.get_warranty_reputation_user(
            [user.id, data["buyer_id"], data["agent_id"]]
        )
    except exceptions.UserIsNotGuarantorException:
        await message.answer(text.DEAL_USER_NOT_GUARANTOR)
        return

    deal = await trading_service.create_external_deal(dto)
    deal = await trading_service.get_external_deal(deal.id)

    try:
        chat_id = guarantor.users[0].telegram_id if guarantor.users else None
        await bot.send_message(
            chat_id,
            text.get_deal_message(deal),
            reply_markup=keyboards.get_external_deal_accept_keyboard(deal),
        )
    except TelegramAPIError:
        await message.answer(text.EXTERNAL_DEAL_ERROR_MESSAGE)
        return

    await message.answer(text.EXTERNAL_DEAL_SUCCESS_MESSAGE)


@trading_router.callback_query(
    callbacks.ExternalDealAcceptCallback.filter(),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def external_deal_accept_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ExternalDealAcceptCallback,
    trading_service: TradingService,
    user_service: UserService,
    user: entities.UserEntity,
    user_actions: UserActions,
):
    deal = await trading_service.get_external_deal(callback_data.id)

    try:
        guarantor = await user_service.get_warranty_reputation_user(
            [deal.seller_id, deal.buyer_id] + [deal.agent_id] if deal.agent_id else []
        )
        reputation_user = await user_service.get_reputation_user_by_user_id(user.id)
    except exceptions.UserIsNotGuarantorException:
        await callback.message.answer(text.DEAL_USER_NOT_GUARANTOR)
        return

    if guarantor.id != reputation_user.id or deal.status != types.DealStatus.DRAFT:
        await callback.message.answer(text.ACCESS_DENIED)
        return

    await trading_service.start_external_deal(callback_data.id)
    await user_actions.send_message_to_users(deal)
    await callback.message.edit_text(text.EXTERNAL_DEAL_SUCCESS_MESSAGE)


@trading_router.callback_query(
    callbacks.ExternalDealDeleteCallback.filter(),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def external_deal_delete_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ExternalDealDeleteCallback,
    trading_service: TradingService,
    user_service: UserService,
    user: entities.UserEntity,
):
    deal = await trading_service.get_external_deal(callback_data.id)

    try:
        guarantor = await user_service.get_warranty_reputation_user(
            [deal.seller_id, deal.buyer_id] + [deal.agent_id] if deal.agent_id else []
        )
        reputation_user = await user_service.get_reputation_user_by_user_id(user.id)
    except exceptions.UserIsNotGuarantorException:
        await callback.message.answer(text.DEAL_USER_NOT_GUARANTOR)
        return

    if guarantor.id != reputation_user.id or deal.status != types.DealStatus.DRAFT:
        await callback.message.answer(text.ACCESS_DENIED)
        return

    await trading_service.delete_external_deal(callback_data.id)
    await callback.message.edit_text(text.EXTERNAL_DEAL_DELETED_MESSAGE)


@trading_router.callback_query(
    callbacks.FinishExternalDealCallback.filter(),
    GroupsFilter([ChatType.PRIVATE]),
    flags={"subscriptions": True},
)
async def finish_external_deal_handler(
    callback: CallbackQuery,
    callback_data: callbacks.FinishExternalDealCallback,
    trading_service: TradingService,
    user_actions: UserActions,
    user: entities.UserEntity,
):
    await trading_service.accept_external_deal(callback_data.id, user.id)
    deal = await trading_service.get_external_deal(callback_data.id)
    await callback.message.edit_text(text.EXTERNAL_DEAL_SUCCESS_MESSAGE)
    await user_actions.send_message_to_users(deal)
