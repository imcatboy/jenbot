from datetime import datetime
from sqlalchemy import or_, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from domain.objects import exceptions, models, entities, dtos, types
from .relations import (
    get_scam_report_relations,
    get_review_author_relations,
    get_external_deal_with_relations_relations,
    get_review_subject_relations,
    get_review_relations,
)
from .base import BaseRepository


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

    async def get_scam_report(self, id: int) -> entities.ScamReportWithRelationsEntity:
        scam_report = await self.get_by_id(
            models.ScamReportModel, id, get_scam_report_relations()
        )
        return entities.ScamReportWithRelationsEntity.model_validate(scam_report)

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

    async def get_scam_report_count(
        self, user_id: int, status: types.ReportStatus
    ) -> int:
        result = await self.session.execute(
            select(func.count(models.ScamReportModel.id)).where(
                models.ScamReportModel.user_id == user_id,
                models.ScamReportModel.status == status,
            )
        )
        return result.scalar_one_or_none() or 0

    async def create_review(self, dto: dtos.InsertReviewDTO) -> entities.ReviewEntity:
        await self.validator.validate_data_not_exists(
            models.ReviewModel,
            author_id=dto.author_id,
            subject_user_id=dto.subject_user_id,
        )
        await self.validator.validate_data_not_exists(
            models.ReviewModel,
            author_id=dto.author_id,
            subject_reputation_user_id=dto.subject_reputation_user_id,
        )
        review = models.ReviewModel(**dto.model_dump())
        await self.create_relation(review, models.UserModel, dto.author_id)
        await self.create_relation(review, models.UserModel, dto.subject_user_id)
        await self.create_relation(
            review, models.ReputationUserModel, dto.subject_reputation_user_id
        )
        self.session.add(review)
        await self.session.flush()
        return entities.ReviewEntity.model_validate(review)

    async def delete_my_review(self, id: int, user_id: int) -> None:
        review = await self.get_one_by_data(
            models.ReviewModel, id=id, author_id=user_id
        )
        await self.session.delete(review)

    async def delete_review(self, id: int) -> None:
        review = await self.get_by_id(models.ReviewModel, id)
        await self.session.delete(review)

    async def review_exists(
        self, author_id: int, subject_user_id: int, subject_reputation_user_id: int
    ) -> bool:
        result = await self.session.execute(
            select(models.ReviewModel.id)
            .where(
                models.ReviewModel.author_id == author_id,
                models.ReviewModel.subject_user_id == subject_user_id,
                models.ReviewModel.subject_reputation_user_id
                == subject_reputation_user_id,
            )
            .exists()
            .select()
        )
        return result.scalar()

    async def get_review(self, id: int) -> entities.ReviewWithRelationsEntity:
        review = await self.get_by_id(models.ReviewModel, id, get_review_relations())
        return entities.ReviewWithRelationsEntity.model_validate(review)

    async def get_reviews(
        self, dto: dtos.GetReviewsDTO
    ) -> List[entities.ReviewWithAuthorEntity]:
        result = await self.session.execute(
            select(models.ReviewModel)
            .where(
                models.ReviewModel.subject_reputation_user_id == dto.reputation_user_id
            )
            .options(*get_review_author_relations())
            .order_by(models.ReviewModel.created_at.desc())
            .offset(dto.offset)
            .limit(dto.limit)
        )
        return [
            entities.ReviewWithAuthorEntity.model_validate(review)
            for review in result.scalars().all()
        ]

    async def get_my_reviews(
        self, dto: dtos.GetMyReviewsDTO
    ) -> List[entities.ReviewWithSubjectEntity]:
        result = await self.session.execute(
            select(models.ReviewModel)
            .options(*get_review_subject_relations())
            .where(models.ReviewModel.author_id == dto.user_id)
            .order_by(models.ReviewModel.created_at.desc())
            .offset(dto.offset)
            .limit(dto.limit)
        )
        return [
            entities.ReviewWithSubjectEntity.model_validate(review)
            for review in result.scalars().all()
        ]

    async def add_review_count(self, reputation_user_id: int) -> None:
        await self.session.execute(
            update(models.ReputationUserModel)
            .where(models.ReputationUserModel.id == reputation_user_id)
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
        self, dto: dtos.InsertExternalDealDTO
    ) -> entities.ExternalDealEntity:
        external_deal = models.ExternalDealModel(**dto.model_dump())
        await self.create_relation(external_deal, models.UserModel, dto.seller_id)
        await self.create_relation(external_deal, models.UserModel, dto.buyer_id)
        await self.set_optional_relation(external_deal, models.UserModel, dto.agent_id)
        await self.create_relation(
            external_deal, models.ReputationUserModel, dto.warranty_reputation_user_id
        )
        await self.create_relation(
            external_deal, models.UserModel, dto.created_by_user_id
        )
        self.session.add(external_deal)
        await self.session.flush()
        return entities.ExternalDealEntity.model_validate(external_deal)

    async def update_external_deal(
        self, id: int, dto: dtos.UpdateExternalDealDTO
    ) -> entities.ExternalDealEntity:
        external_deal = await self.get_by_id(models.ExternalDealModel, id)

        if dto.status is not None:
            external_deal.status = dto.status
        if dto.seller_condition is not None:
            external_deal.seller_condition = dto.seller_condition
        if dto.buyer_condition is not None:
            external_deal.buyer_condition = dto.buyer_condition

        await self.session.flush()
        return entities.ExternalDealEntity.model_validate(external_deal)

    async def get_external_deal(
        self, id: int
    ) -> entities.ExternalDealWithRelationsEntity:
        external_deal = await self.get_by_id(
            models.ExternalDealModel, id, get_external_deal_with_relations_relations()
        )
        return entities.ExternalDealWithRelationsEntity.model_validate(external_deal)

    async def get_external_deal_by_user_id(
        self, id: int, user_id: int
    ) -> entities.ExternalDealWithRelationsEntity:
        result = await self.session.execute(
            select(models.ExternalDealModel)
            .where(
                models.ExternalDealModel.id == id,
                or_(
                    models.ExternalDealModel.seller_id == user_id,
                    models.ExternalDealModel.buyer_id == user_id,
                    models.ExternalDealModel.agent_id == user_id,
                ),
            )
            .options(*get_external_deal_with_relations_relations())
        )
        external_deal = result.scalar_one_or_none()

        if not external_deal:
            raise exceptions.ObjectNotFoundException("ExternalDealModel", [id])

        return entities.ExternalDealWithRelationsEntity.model_validate(external_deal)

    async def get_external_deal_amount(self, reputation_id: int) -> float:
        result = await self.session.execute(
            select(func.sum(models.ExternalDealModel.refund_amount)).where(
                models.ExternalDealModel.warranty_reputation_user_id == reputation_id,
                models.ExternalDealModel.status.in_(
                    [
                        types.DealStatus.PENDING,
                        types.DealStatus.EXPIRED,
                        types.DealStatus.REJECTED,
                    ]
                ),
            )
        )
        value = result.scalar_one_or_none()
        return float(value) if value is not None else 0.0

    async def delete_external_deal(self, id: int) -> None:
        deal = await self.get_by_id(models.ExternalDealModel, id)
        await self.session.delete(deal)

    async def expire_external_deals(self) -> None:
        await self.session.execute(
            update(models.ExternalDealModel)
            .where(
                models.ExternalDealModel.expires_at < datetime.now(),
                models.ExternalDealModel.status == types.DealStatus.PENDING,
            )
            .values(status=types.DealStatus.EXPIRED)
        )

    async def create_external_deal_notification(
        self, dto: dtos.CreateExternalDealNotificationDTO
    ) -> entities.ExternalDealNotificationEntity:
        external_deal_notification = models.ExternalDealNotificationModel(
            **dto.model_dump()
        )
        await self.create_relation(
            external_deal_notification, models.ExternalDealModel, dto.external_deal_id
        )
        await self.create_relation(
            external_deal_notification, models.UserModel, dto.user_id
        )
        self.session.add(external_deal_notification)
        await self.session.flush()
        return entities.ExternalDealNotificationEntity.model_validate(
            external_deal_notification
        )

    async def update_external_deal_notification(
        self, id: int, dto: dtos.UpdateExternalDealNotificationDTO
    ) -> entities.ExternalDealNotificationEntity:
        external_deal_notification = await self.get_by_id(
            models.ExternalDealNotificationModel, id
        )

        if dto.telegram_message_id is not None:
            external_deal_notification.telegram_message_id = dto.telegram_message_id
        if dto.telegram_chat_id is not None:
            external_deal_notification.telegram_chat_id = dto.telegram_chat_id

        await self.session.flush()
        return entities.ExternalDealNotificationEntity.model_validate(
            external_deal_notification
        )

    async def get_external_deal_notification(
        self, external_deal_id: int, user_id: int
    ) -> entities.ExternalDealNotificationEntity:
        external_deal_notification = await self.get_one_by_data(
            models.ExternalDealNotificationModel,
            external_deal_id=external_deal_id,
            user_id=user_id,
        )
        return entities.ExternalDealNotificationEntity.model_validate(
            external_deal_notification
        )

    async def get_expired_external_deals(
        self,
    ) -> List[entities.ExternalDealWithRelationsEntity]:
        result = await self.session.execute(
            select(models.ExternalDealModel)
            .where(
                models.ExternalDealModel.expires_at < datetime.now(),
                models.ExternalDealModel.status == types.DealStatus.PENDING,
            )
            .options(*get_external_deal_with_relations_relations())
        )
        return [
            entities.ExternalDealWithRelationsEntity.model_validate(external_deal)
            for external_deal in result.scalars().all()
        ]

    async def get_external_deals_by_ids(
        self, ids: List[int]
    ) -> List[entities.ExternalDealWithRelationsEntity]:
        if not ids:
            return []

        result = await self.session.execute(
            select(models.ExternalDealModel)
            .where(models.ExternalDealModel.id.in_(ids))
            .options(*get_external_deal_with_relations_relations())
        )
        return [
            entities.ExternalDealWithRelationsEntity.model_validate(external_deal)
            for external_deal in result.scalars().all()
        ]
