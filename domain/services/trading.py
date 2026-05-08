from datetime import datetime, timedelta
from typing import List
from domain.repositories import (
    TradingRepository,
    MarketplaceRepository,
    MessagingRepository,
)
from domain.objects import entities, dtos, exceptions, types


class TradingService:

    def __init__(
        self,
        trading_repository: TradingRepository,
        marketplace_repository: MarketplaceRepository,
        messaging_repository: MessagingRepository,
    ) -> None:
        self.trading_repository = trading_repository
        self.marketplace_repository = marketplace_repository
        self.messaging_repository = messaging_repository

    async def buy_advertisement_option(
        self, dto: dtos.BuyAdvertisementOptionDTO
    ) -> entities.DealEntity:
        get_deals_dto = dtos.GetDealsDTO(
            user_id=dto.user_id, status=types.DealStatus.PENDING
        )
        deals = await self.trading_repository.get_deals(get_deals_dto)

        if len(deals) >= 3:
            raise exceptions.TooManyObjectsFoundException(
                "Deal", user_id=dto.user_id, status=types.DealStatus.PENDING
            )

        advertisement_option = (
            await self.marketplace_repository.get_advertisement_option(
                dto.advertisement_option_id
            )
        )

        if advertisement_option.count < dto.count:
            raise exceptions.NotEnoughInventoryException(
                dto.advertisement_option_id,
                dto.count,
            )

        if dto.user_id == advertisement_option.advertisement.user_id:
            raise exceptions.DealSelfPurchaseException(
                deal_id=dto.advertisement_option_id,
            )

        if (
            dto.trade_id
            and dto.option_price_id
            or not dto.trade_id
            and not dto.option_price_id
        ):
            raise exceptions.InvalidDataException(
                trade_id=dto.trade_id,
                option_price_id=dto.option_price_id,
            )

        trade_product_id = None
        trade_product_option_ids = None
        trade_count = None
        amount = None
        currency_id = None

        if dto.trade_id:
            trade = await self.marketplace_repository.get_advertisement_option_trade(
                dto.trade_id
            )

            if trade.advertisement_option_id != advertisement_option.id:
                raise exceptions.ObjectNotFoundException("Trade", [dto.trade_id])

            trade_product_id = trade.product_id
            trade_product_option_ids = [
                product_option.id for product_option in trade.product_options
            ]
            deal_type = types.DealType.TRADE

        if dto.option_price_id:
            price = await self.marketplace_repository.get_advertisement_option_price(
                dto.option_price_id
            )

            if price.advertisement_option_id != advertisement_option.id:
                raise exceptions.ObjectNotFoundException(
                    "AdvertisementOptionPrice", [dto.option_price_id]
                )

            amount = price.amount
            currency_id = price.currency_id
            deal_type = types.DealType.MONEY

        await self.marketplace_repository.update_advertisement_option_count(
            advertisement_option.id, dto.count
        )
        deal = await self.trading_repository.create_deal(
            dtos.CreateDealDTO(
                advertisement_option_id=advertisement_option.id,
                deal_type=deal_type,
                count=dto.count,
                expires_at=datetime.now() + timedelta(days=1),
                product_id=advertisement_option.advertisement.product_id,
                product_option_ids=[
                    product_option.id
                    for product_option in advertisement_option.product_options
                ],
                seller_id=advertisement_option.advertisement.user_id,
                user_id=dto.user_id,
                option_price_id=dto.option_price_id,
                amount=amount,
                currency_id=currency_id,
                trade_count=trade_count,
                trade_id=dto.trade_id,
                trade_product_id=trade_product_id,
                trade_product_option_ids=trade_product_option_ids,
            )
        )
        options = [
            product_option.name
            for product_option in advertisement_option.product_options
        ]
        await self.messaging_repository.create_chat(
            dtos.CreateChatDTO(
                name=f"Покупка {advertisement_option.advertisement.product.name} {', '.join(options)}",
                deal_id=deal.id,
                participant_ids=[
                    dto.user_id,
                    advertisement_option.advertisement.user_id,
                ],
            )
        )
        return deal

    async def update_deal(
        self, id: int, dto: dtos.UpdateDealDTO
    ) -> entities.DealEntity:
        return await self.trading_repository.update_deal(id, dto)

    async def change_condition(
        self, id: int, user_id: int, condition: types.DealCondition
    ) -> None:
        deal = await self.trading_repository.get_deal(id, user_id)

        if deal.user_id != user_id and deal.seller_id != user_id:
            raise exceptions.ObjectNotFoundException("Deal", [id])

        if deal.status != types.DealStatus.PENDING:
            raise exceptions.DealNotPendingException(
                deal_id=id,
            )

        if deal.user_id == user_id:
            await self.trading_repository.update_deal(
                id, dtos.UpdateDealDTO(buyer_condition=condition)
            )

        await self.trading_repository.update_deal(
            id, dtos.UpdateDealDTO(seller_condition=condition)
        )

    async def change_status(self, id: int) -> None:
        deal = await self.trading_repository.get_deal(id)

        if deal.status != types.DealStatus.PENDING:
            raise exceptions.DealNotPendingException(
                deal_id=id,
            )
        if deal.expires_at < datetime.now():
            await self.trading_repository.update_deal(
                id, dtos.UpdateDealDTO(status=types.DealStatus.EXPIRED)
            )
            return

        if (
            deal.seller_condition == types.DealCondition.COMPLAINT
            or deal.buyer_condition == types.DealCondition.COMPLAINT
        ):
            await self.trading_repository.update_deal(
                id, dtos.UpdateDealDTO(status=types.DealStatus.REJECTED)
            )
        elif (
            deal.seller_condition == types.DealCondition.ACCEPTED
            and deal.buyer_condition == types.DealCondition.ACCEPTED
        ):
            await self.trading_repository.update_deal(
                id, dtos.UpdateDealDTO(status=types.DealStatus.COMPLETED)
            )

            if deal.advertisement_option_id:
                await self.marketplace_repository.update_advertisement_option_sold_count(
                    deal.advertisement_option_id, deal.count
                )
        elif (
            deal.seller_condition == types.DealCondition.CANCELLED
            and deal.buyer_condition == types.DealCondition.CANCELLED
        ):
            await self.trading_repository.update_deal(
                id, dtos.UpdateDealDTO(status=types.DealStatus.CANCELLED)
            )

    async def get_deal(self, id: int, user_id: int) -> entities.DealEntity:
        return await self.trading_repository.get_deal(id, user_id)

    async def get_deals(self, dto: dtos.GetDealsDTO) -> List[entities.DealEntity]:
        return await self.trading_repository.get_deals(dto)
