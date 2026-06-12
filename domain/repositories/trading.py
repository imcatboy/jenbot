from sqlalchemy import or_, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from .base import BaseRepository
from domain.objects import exceptions, models, entities, dtos, types


class TradingRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_deal(self, dto: dtos.CreateDealDTO) -> entities.DealEntity:
        deal = models.DealModel(
            **dto.model_dump(
                exclude={
                    "product_option_ids",
                    "trade_product_option_ids",
                    "option_price_id",
                }
            )
        )
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
                models.DealModel.id == id,
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

    async def create_scam_report(
        self, dto: dtos.CreateScamReportDTO
    ) -> entities.ScamReportEntity:
        scam_report = models.ScamReportModel(**dto.model_dump())
        await self.create_relation(scam_report, models.UserModel, dto.user_id)
        self.session.add(scam_report)
        await self.session.flush()
        return entities.ScamReportEntity.model_validate(scam_report)

    async def update_scam_report(
        self, id: int, dto: dtos.UpdateScamReportDTO
    ) -> entities.ScamReportEntity:
        scam_report = await self.get_by_id(models.ScamReportModel, id)

        if dto.status is not None:
            scam_report.status = dto.status
        if dto.comment is not None:
            scam_report.comment = dto.comment

        await self.set_optional_relation(
            scam_report, models.UserModel, dto.applied_by_user_id, "applied_by_user_id"
        )
        await self.set_optional_relation(
            scam_report,
            models.ReputationUserModel,
            dto.accused_reputation_user_id,
            "accused_reputation_user_id",
        )
        await self.session.flush()
        return entities.ScamReportEntity.model_validate(scam_report)

    async def get_scam_report(self, id: int) -> entities.ScamReportEntity:
        scam_report = await self.get_by_id(models.ScamReportModel, id)
        return entities.ScamReportEntity.model_validate(scam_report)

    async def get_scam_reports(
        self, reputation_user_id: int
    ) -> List[entities.ScamReportEntity]:
        result = await self.session.execute(
            select(models.ScamReportModel)
            .where(
                models.ScamReportModel.accused_reputation_user_id == reputation_user_id,
                models.ScamReportModel.status == types.ReportStatus.APPROVED,
            )
            .order_by(models.ScamReportModel.created_at.desc())
        )
        return [
            entities.ScamReportEntity.model_validate(scam_report)
            for scam_report in result.scalars().all()
        ]

    async def create_review(self, dto: dtos.InsertReviewDTO) -> entities.ReviewEntity:
        review = models.ReviewModel(**dto.model_dump())
        await self.create_relation(review, models.UserModel, dto.author_id)
        await self.create_relation(review, models.UserModel, dto.subject_user_id)
        await self.create_relation(
            review, models.ReputationUserModel, dto.subject_reputation_user_id
        )
        await self.set_optional_relation(review, models.DealModel, dto.deal_id)
        await self.set_optional_relation(
            review, models.ExternalDealModel, dto.external_deal_id
        )
        self.session.add(review)
        await self.session.flush()
        return entities.ReviewEntity.model_validate(review)

    async def add_review_count(self, user_id: int) -> None:
        await self.session.execute(
            update(models.ReputationUserModel)
            .where(models.ReputationUserModel.users.any(models.UserModel.id == user_id))
            .values(review_count=models.ReputationUserModel.review_count + 1)
        )

    async def add_scam_report_count(self, user_id: int) -> None:
        await self.session.execute(
            update(models.ReputationUserModel)
            .where(models.ReputationUserModel.users.any(models.UserModel.id == user_id))
            .values(
                applied_report_count=models.ReputationUserModel.applied_report_count + 1
            )
        )

    async def create_external_deal(
        self, dto: dtos.CreateExternalDealDTO
    ) -> entities.ExternalDealEntity:
        external_deal = models.ExternalDealModel(**dto.model_dump())
        await self.create_relation(external_deal, models.UserModel, dto.seller_id)
        await self.create_relation(external_deal, models.UserModel, dto.buyer_id)
        await self.set_optional_relation(external_deal, models.UserModel, dto.agent_id)
        self.session.add(external_deal)
        await self.session.flush()
        return entities.ExternalDealEntity.model_validate(external_deal)

    async def update_external_deal(
        self, id: int, status: types.DealStatus
    ) -> entities.ExternalDealEntity:
        external_deal = await self.get_by_id(models.ExternalDealModel, id)
        external_deal.status = status
        await self.session.flush()
        return entities.ExternalDealEntity.model_validate(external_deal)

    async def get_external_deal_amount(self, reputation_id: int) -> float:
        result = await self.session.scalar(
            select(func.sum(models.ExternalDealModel.amount))
            .join(
                models.UserModel,
                or_(
                    models.ExternalDealModel.seller_id == models.UserModel.id,
                    models.ExternalDealModel.buyer_id == models.UserModel.id,
                    models.ExternalDealModel.agent_id == models.UserModel.id,
                ),
            )
            .where(
                models.UserModel.reputation_user_id == reputation_id,
                models.ExternalDealModel.status.in_(
                    [
                        types.DealStatus.PENDING,
                        types.DealStatus.EXPIRED,
                        types.DealStatus.REJECTED,
                    ]
                ),
            )
        )
        return result.scalar_one_or_none() or 0.0

    async def get_external_deal(self, id: int) -> entities.ExternalDealEntity:
        external_deal = await self.get_by_id(models.ExternalDealModel, id)
        return entities.ExternalDealEntity.model_validate(external_deal)

    async def delete_external_deal(self, id: int) -> None:
        deal = await self.get_by_id(models.ExternalDealModel, id)
        await self.session.delete(deal)

    async def get_reviews(self, user_id: int) -> List[entities.ReviewEntity]:
        reviews = await self.get_all_by_data(models.ReviewModel, user_id=user_id)
        return [entities.ReviewEntity.model_validate(review) for review in reviews]
