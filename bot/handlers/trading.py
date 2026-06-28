from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram import Bot, Router, F

from domain.objects.types import Reason, UserReputationRole, UsernameOrTelegramID
from domain.objects import dtos, entities, exceptions, NoZeroInt
from domain.services import TradingService, UserService
from bot.data import text, keyboards, states, callbacks
from bot.actions import UserActions, TradingActions
from bot.filters import GroupsFilter


trading_router = Router()
trading_router.message.filter(GroupsFilter([ChatType.PRIVATE]))
trading_router.callback_query.filter(GroupsFilter([ChatType.PRIVATE]))


@trading_router.message(
    Command("deal", ignore_case=True),
    flags={"subscriptions": True},
)
async def deal_handler(
    message: Message, user_service: UserService, user: entities.UserEntity
):
    with_agent = False

    try:
        reputation_user = await user_service.get_reputation_user_by_user_id(user.id)

        if reputation_user.role == UserReputationRole.SCAMMER:
            raise exceptions.UserIsScammerException(user.id)

        with_agent = reputation_user.role in [
            UserReputationRole.SMALL_GUARANTOR,
            UserReputationRole.GUARANTOR,
            UserReputationRole.BIG_GUARANTOR,
        ]
    except exceptions.ObjectNotFoundException:
        pass

    await message.answer(
        text.EXTERNAL_DEAL_FIRST_ROLE_MESSAGE,
        reply_markup=keyboards.get_external_deal_first_role_keyboard(with_agent),
    )


@trading_router.callback_query(
    callbacks.ExternalDealFirstRoleCallback.filter(F.is_seller | F.is_buyer)
)
async def external_deal_first_role_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ExternalDealFirstRoleCallback,
    user: entities.UserEntity,
    state: FSMContext,
):

    if callback_data.is_seller:
        await state.update_data(seller_id=user.id)
    elif callback_data.is_buyer:
        await state.update_data(buyer_id=user.id)

    await state.set_state(states.ExternalDealState.second_participant_id)
    await callback.answer()
    await callback.message.answer(
        text.EXTERNAL_DEAL_SECOND_PARTICIPANT_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id),
    )


@trading_router.message(
    states.ExternalDealState.second_participant_id,
    flags={"cast": UsernameOrTelegramID},
)
async def external_deal_second_participant_id_handler(
    message: Message,
    state_data: UsernameOrTelegramID,
    state: FSMContext,
    user_actions: UserActions,
):
    user = await user_actions.get_telegram_user(state_data)
    data = await state.get_data()

    if data.get("buyer_id"):
        await state.update_data(seller_id=user.id)
    elif data.get("seller_id"):
        await state.update_data(buyer_id=user.id)

    await state.set_state(states.ExternalDealState.agent_id)
    await message.answer(
        text.EXTERNAL_DEAL_AGENT_MESSAGE,
        reply_markup=keyboards.get_skip_keyboard(message.from_user.id),
    )


@trading_router.callback_query(
    callbacks.SkipCallback.filter(),
    states.ExternalDealState.agent_id,
)
async def external_deal_agent_id_skip_handler(
    callback: CallbackQuery,
    state: FSMContext,
    user_service: UserService,
    trading_service: TradingService,
):
    data = await state.get_data()

    try:
        warranty_reputation_user = await user_service.get_warranty_reputation_user(
            [data["seller_id"], data["buyer_id"]]
        )
        used_amount = await trading_service.get_external_deal_amount(
            warranty_reputation_user.id
        )
        free_amount = warranty_reputation_user.amount - used_amount
    except exceptions.UserIsNotGuarantorException:
        await state.clear()
        await callback.message.answer(
            text.EXTERNAL_DEAL_WITHOUT_WARRANTY_REPUTATION_USER
        )
        return

    await callback.answer()
    await state.update_data(agent_id=None)
    await state.set_state(states.ExternalDealState.deal_amount)
    await callback.message.answer(
        text.EXTERNAL_DEAL_AMOUNT_MESSAGE.format(
            f"{max(0, free_amount)} {text.get_count_word(max(0, free_amount), "рубль", "рубля", "рублей")}",
            f"{warranty_reputation_user.amount} {text.get_count_word(warranty_reputation_user.amount, "рубль", "рубля", "рублей")}",
        ),
        reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id),
    )


@trading_router.message(
    states.ExternalDealState.agent_id,
    flags={"cast": UsernameOrTelegramID},
)
async def external_deal_agent_id_handler(
    message: Message,
    state_data: UsernameOrTelegramID,
    state: FSMContext,
    user_actions: UserActions,
    user_service: UserService,
):
    user = await user_actions.get_telegram_user(state_data)

    try:
        reputation_user = await user_service.get_reputation_user_by_user_id(user.id)

        if reputation_user.role not in [
            UserReputationRole.SMALL_GUARANTOR,
            UserReputationRole.GUARANTOR,
            UserReputationRole.BIG_GUARANTOR,
        ]:
            await message.answer(text.USER_IS_NOT_GUARANTOR)
            return
    except exceptions.ObjectNotFoundException:
        await message.answer(text.USER_IS_NOT_GUARANTOR)
        return

    await state.update_data(agent_id=user.id)
    await state.set_state(states.ExternalDealState.payment)
    await message.answer(
        text.EXTERNAL_DEAL_PAYMENT_MESSAGE,
        reply_markup=keyboards.get_skip_keyboard(message.from_user.id),
    )


@trading_router.callback_query(
    callbacks.SkipCallback.filter(),
    states.ExternalDealState.payment,
)
async def external_deal_payment_skip_handler(
    callback: CallbackQuery,
    state: FSMContext,
    user_service: UserService,
    trading_service: TradingService,
):
    data = await state.get_data()

    try:
        warranty_reputation_user = await user_service.get_warranty_reputation_user(
            [data["agent_id"]]
            if data.get("agent_id")
            else [data["seller_id"], data["buyer_id"]]
        )
        used_amount = await trading_service.get_external_deal_amount(
            warranty_reputation_user.id
        )
        free_amount = warranty_reputation_user.amount - used_amount
    except exceptions.UserIsNotGuarantorException:
        await state.clear()
        await callback.message.answer(
            text.EXTERNAL_DEAL_WITHOUT_WARRANTY_REPUTATION_USER
        )
        return

    await callback.answer()
    await state.update_data(payment=None)
    await state.set_state(states.ExternalDealState.deal_amount)
    await callback.message.answer(
        text.EXTERNAL_DEAL_AMOUNT_MESSAGE.format(
            f"{max(0, free_amount)} {text.get_count_word(max(0, free_amount), "рубль", "рубля", "рублей")}",
            f"{warranty_reputation_user.amount} {text.get_count_word(warranty_reputation_user.amount, "рубль", "рубля", "рублей")}",
        ),
        reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id),
    )


@trading_router.message(
    states.ExternalDealState.payment,
    flags={"cast": Reason},
)
async def external_deal_payment_handler(
    message: Message,
    state_data: Reason,
    state: FSMContext,
    user_service: UserService,
    trading_service: TradingService,
):
    await state.update_data(payment=state_data)
    data = await state.get_data()
    try:
        warranty_reputation_user = await user_service.get_warranty_reputation_user(
            [data["agent_id"]]
            if data.get("agent_id")
            else [data["seller_id"], data["buyer_id"]]
        )
        used_amount = await trading_service.get_external_deal_amount(
            warranty_reputation_user.id
        )
        free_amount = warranty_reputation_user.amount - used_amount
    except exceptions.UserIsNotGuarantorException:
        await state.clear()
        await message.answer(text.EXTERNAL_DEAL_WITHOUT_WARRANTY_REPUTATION_USER)
        return

    await state.set_state(states.ExternalDealState.deal_amount)
    await message.answer(
        text.EXTERNAL_DEAL_AMOUNT_MESSAGE.format(
            f"{max(0, free_amount)} {text.get_count_word(max(0, free_amount), "рубль", "рубля", "рублей")}",
            f"{warranty_reputation_user.amount} {text.get_count_word(warranty_reputation_user.amount, "рубль", "рубля", "рублей")}",
        ),
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )


@trading_router.callback_query(
    callbacks.ExternalDealFirstRoleCallback.filter(F.is_agent)
)
async def external_deal_agent_callback_handler(
    callback: CallbackQuery,
    user: entities.UserEntity,
    state: FSMContext,
):
    await state.update_data(agent_id=user.id)
    await state.set_state(states.ExternalDealState.buyer_id)
    await callback.answer()
    await callback.message.answer(
        text.EXTERNAL_DEAL_BUYER_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(callback.from_user.id),
    )


@trading_router.message(
    states.ExternalDealState.buyer_id,
    flags={"cast": UsernameOrTelegramID},
)
async def external_deal_buyer_id_handler(
    message: Message,
    state_data: UsernameOrTelegramID,
    state: FSMContext,
    user_actions: UserActions,
):
    buyer = await user_actions.get_telegram_user(state_data)
    await state.update_data(buyer_id=buyer.id)
    await state.set_state(states.ExternalDealState.seller_id)
    await message.answer(
        text.EXTERNAL_DEAL_SELLER_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )


@trading_router.message(
    states.ExternalDealState.seller_id,
    flags={"cast": UsernameOrTelegramID},
)
async def external_deal_seller_id_handler(
    message: Message,
    state_data: UsernameOrTelegramID,
    state: FSMContext,
    user_actions: UserActions,
):
    seller = await user_actions.get_telegram_user(state_data)
    await state.update_data(seller_id=seller.id)
    await state.set_state(states.ExternalDealState.payment)
    await message.answer(
        text.EXTERNAL_DEAL_PAYMENT_MESSAGE,
        reply_markup=keyboards.get_skip_keyboard(message.from_user.id),
    )


@trading_router.message(
    states.ExternalDealState.deal_amount,
    flags={"cast": NoZeroInt},
)
async def external_deal_deal_amount_handler(
    message: Message,
    state_data: NoZeroInt,
    state: FSMContext,
):
    await state.update_data(deal_amount=state_data)
    await state.set_state(states.ExternalDealState.description)
    await message.answer(
        text.EXTERNAL_DEAL_DESCRIPTION_MESSAGE,
        reply_markup=keyboards.get_cancel_keyboard(message.from_user.id),
    )


@trading_router.message(
    states.ExternalDealState.description,
    flags={"cast": Reason},
)
async def external_deal_description_handler(
    message: Message,
    state_data: Reason,
    state: FSMContext,
    user: entities.UserEntity,
    trading_service: TradingService,
    trading_actions: TradingActions,
):
    await state.update_data(description=state_data)
    data = await state.get_data()
    dto = dtos.CreateExternalDealDTO(
        deal_amount=data["deal_amount"],
        payment=data.get("payment"),
        description=data["description"],
        expires_at=datetime.now() + timedelta(days=1),
        seller_id=data["seller_id"],
        buyer_id=data["buyer_id"],
        agent_id=data.get("agent_id"),
        created_by_user_id=user.id,
    )
    deal = await trading_service.create_external_deal(dto)
    await state.clear()
    deal = await trading_service.get_external_deal(deal.id)
    await trading_actions.send_draft_external_deal_message(deal)
    await message.answer(text.get_external_deal_success_message(deal))


@trading_router.callback_query(
    callbacks.ChangeExternalDealDraftCallback.filter(F.is_accepted == True),
)
async def change_external_deal_draft_accept_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ChangeExternalDealDraftCallback,
    trading_service: TradingService,
    user: entities.UserEntity,
    trading_actions: TradingActions,
):
    await trading_service.start_external_deal(callback_data.id, user.id)
    await callback.answer()
    deal = await trading_service.get_external_deal(callback_data.id)
    await trading_actions.send_external_deal_messages(deal)


@trading_router.callback_query(
    callbacks.ChangeExternalDealDraftCallback.filter(F.is_accepted == False),
)
async def change_external_deal_draft_cancel_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ChangeExternalDealDraftCallback,
    trading_service: TradingService,
    user: entities.UserEntity,
):
    await trading_service.delete_external_deal(callback_data.id, user.id)
    await callback.answer()
    await callback.message.edit_text(text.EXTERNAL_DEAL_DELETED_MESSAGE)


@trading_router.callback_query(
    callbacks.ChangeExternalDealStatusCallback.filter(),
)
async def change_external_deal_status_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.ChangeExternalDealStatusCallback,
    trading_service: TradingService,
    user: entities.UserEntity,
    trading_actions: TradingActions,
):
    await trading_service.change_external_deal_condition(
        callback_data.id, user.id, callback_data.condition
    )
    await callback.answer()
    deal = await trading_service.get_external_deal(callback_data.id)
    await trading_actions.send_external_deal_messages(deal)
