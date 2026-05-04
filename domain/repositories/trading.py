from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select
from typing import List, Optional

from .base import BaseRepository
from domain.objects import exceptions, models, entities, dtos


class TradingRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_deal(self, dto: dtos.CreateDealDTO) -> entities.DealEntity:
        deal = models.DealModel(**dto.model_dump())
        await self.create_relation(
            deal, models.AdvertisementOptionModel, dto.advertisement_option_id
        )
        await self.create_relation(deal, models.UserModel, dto.user_id)
        await self.create_relation(deal, models.UserModel, dto.seller_id, "seller_id")
        await self.set_optional_relation(
            deal, models.UserModel, dto.agent_id, "agent_id"
        )
        await self.set_optional_relation(
            deal, models.AdvertisementOptionPriceModel, dto.option_price_id
        )
        await self.set_optional_relation(deal, models.CurrencyModel, dto.currency_id)
        await self.create_relation(deal, models.ProductModel, dto.product_id)
        await self.set_optional_relation(deal, models.TradeModel, dto.trade_id)
        await self.set_optional_relation(
            deal, models.ProductModel, dto.trade_product_id
        )
        self.session.add(deal)
        await self.session.flush()
        await self.create_many_to_many_relation(
            deal,
            models.deals_product_options,
            models.ProductOptionModel,
            dto.product_option_ids,
        )
        await self.create_many_to_many_relation(
            deal,
            models.trade_deals_product_options,
            models.ProductOptionModel,
            dto.trade_product_option_ids,
        )
        return entities.DealEntity.model_validate(deal)

    async def update_deal(
        self, id: int, dto: dtos.UpdateDealDTO
    ) -> entities.DealEntity:
        deal = await self.get_by_id(models.DealModel, id)

        if dto.status:
            deal.status = dto.status
        if dto.seller_condition:
            deal.seller_condition = dto.seller_condition
        if dto.buyer_condition:
            deal.buyer_condition = dto.buyer_condition

        await self.session.flush()
        return entities.DealEntity.model_validate(deal)

    async def get_deal(
        self, id: int, user_id: Optional[int] = None
    ) -> entities.DealEntity:
        if user_id:
            query = select(models.DealModel).where(
                or_(
                    models.DealModel.user_id == user_id,
                    models.DealModel.seller_id == user_id,
                    models.DealModel.agent_id == user_id,
                ),
            )
        else:
            query = select(models.DealModel).where(
                models.DealModel.id == id,
            )

        result = await self.session.execute(query)
        deal = result.scalar_one_or_none()

        if not deal:
            raise exceptions.ObjectNotFoundException("DealModel", [id])

        return entities.DealEntity.model_validate(deal)

    async def get_deals(self, dto: dtos.GetDealsDTO) -> List[entities.DealEntity]:
        query = select(models.DealModel).where(
            or_(
                models.DealModel.user_id == dto.user_id,
                models.DealModel.seller_id == dto.user_id,
                models.DealModel.agent_id == dto.user_id,
            ),
        )

        if dto.buyer_id:
            query = query.where(models.DealModel.user_id == dto.buyer_id)
        if dto.seller_id:
            query = query.where(models.DealModel.seller_id == dto.seller_id)
        if dto.agent_id:
            query = query.where(models.DealModel.agent_id == dto.agent_id)
        if dto.expires_at:
            query = query.where(models.DealModel.expires_at >= dto.expires_at)
        if dto.status:
            query = query.where(models.DealModel.status == dto.status)
        if dto.product_id:
            query = query.where(models.DealModel.product_id == dto.product_id)

        result = await self.session.execute(query)
        return [
            entities.DealEntity.model_validate(deal) for deal in result.scalars().all()
        ]
