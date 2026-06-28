import logging

from aiogram.exceptions import TelegramNetworkError

from domain.services import TradingService
from bot.actions import TradingActions


logger = logging.getLogger(__name__)


async def expire_external_deals_loop(
    trading_service: TradingService, trading_actions: TradingActions
) -> None:
    expired_external_deals = await trading_service.expire_external_deals()

    if not expired_external_deals:
        return

    for external_deal in expired_external_deals:
        try:
            await trading_actions.send_expired_external_deal_messages(external_deal)
        except TelegramNetworkError:
            raise

    logger.info("Expired %s external deals", len(expired_external_deals))
