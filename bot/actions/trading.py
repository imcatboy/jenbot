import logging

from domain.objects import entities, dtos, exceptions, types
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardMarkup
from typing import Optional

from domain.services import TradingService, ConfigService
from bot.data import text, keyboards
from bot.core import BotProtocol


logger = logging.getLogger(__name__)


class TradingActions:

    def __init__(
        self,
        bot: BotProtocol,
        trading_service: TradingService,
        config_service: ConfigService,
    ):
        self.bot = bot
        self.trading_service = trading_service
        self.config_service = config_service

    async def send_external_deal_message(
        self,
        external_deal: entities.ExternalDealWithRelationsEntity,
        user: entities.UserEntity,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> None:
        try:
            chat_id = user.telegram_id
            message = await self.bot.send_message(
                chat_id,
                text.get_external_deal_message(external_deal),
                reply_markup=reply_markup,
            )
            dto = dtos.CreateExternalDealNotificationDTO(
                external_deal_id=external_deal.id,
                user_id=user.id,
                telegram_message_id=message.message_id,
                telegram_chat_id=chat_id,
            )
            await self.trading_service.create_or_update_external_deal_notification(dto)
        except TelegramAPIError:
            raise exceptions.ChatNotFoundException(user.telegram_id)

    async def send_draft_external_deal_message(
        self, external_deal: entities.ExternalDealWithRelationsEntity
    ) -> None:
        reply_markup = keyboards.get_external_deal_accept_keyboard(external_deal)
        user = external_deal.warranty_reputation_user.users[0]
        await self.send_external_deal_message(external_deal, user, reply_markup)

    async def update_external_deal_message(
        self,
        external_deal: entities.ExternalDealWithRelationsEntity,
        user: entities.UserEntity,
        is_agent: bool = False,
    ) -> None:
        reply_markup: Optional[InlineKeyboardMarkup] = None

        if not is_agent and external_deal.status == types.DealStatus.PENDING:
            reply_markup = keyboards.get_change_external_deal_status_keyboard(
                external_deal, user.id == external_deal.seller_id
            )

        try:
            notification = await self.trading_service.get_external_deal_notification(
                external_deal.id, user.id
            )
        except exceptions.ObjectNotFoundException:
            await self.send_external_deal_message(external_deal, user, reply_markup)
            return

        try:
            await self.bot.edit_message_text(
                text.get_external_deal_message(external_deal),
                chat_id=notification.telegram_chat_id,
                message_id=notification.telegram_message_id,
                reply_markup=reply_markup,
            )
        except TelegramAPIError:
            await self.send_external_deal_message(external_deal, user, reply_markup)

    async def send_external_deal_messages(
        self, external_deal: entities.ExternalDealWithRelationsEntity
    ) -> None:
        await self.update_external_deal_message(external_deal, external_deal.seller)
        await self.update_external_deal_message(external_deal, external_deal.buyer)

        if external_deal.agent:
            await self.update_external_deal_message(
                external_deal, external_deal.agent, is_agent=True
            )

        if external_deal.status in [
            types.DealStatus.EXPIRED,
            types.DealStatus.REJECTED,
        ]:
            await self.send_external_deal_resolve_message(external_deal)

    async def send_expired_external_deal_messages(
        self, external_deal: entities.ExternalDealWithRelationsEntity
    ) -> None:
        participants = [external_deal.seller, external_deal.buyer]

        if external_deal.agent:
            participants.append(external_deal.agent)

        for user in participants:
            try:
                await self.update_external_deal_message(
                    external_deal,
                    user,
                    is_agent=external_deal.agent_id == user.id,
                )
                await self.bot.send_message(
                    user.telegram_id, text.EXTERNAL_DEAL_STATUS_CHANGED_MESSAGE
                )
            except exceptions.ChatNotFoundException as e:
                logger.warning(
                    "Could not notify user %s about expired external deal #%s",
                    e.chat_id,
                    external_deal.id,
                )

        if external_deal.status in [
            types.DealStatus.EXPIRED,
            types.DealStatus.REJECTED,
        ]:
            await self.send_external_deal_resolve_message(external_deal)

    async def send_external_deal_resolve_message(
        self, external_deal: entities.ExternalDealWithRelationsEntity
    ) -> None:
        admin_chat_id = await self.config_service.get("admin_chat_id")
        await self.bot.send_message(
            admin_chat_id,
            text.get_external_deal_message(external_deal),
            reply_markup=keyboards.get_resolve_external_deal_keyboard(external_deal),
        )
