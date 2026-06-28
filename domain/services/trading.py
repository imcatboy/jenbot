from datetime import datetime, timedelta
from typing import List, Optional
from domain.repositories import (
    TradingRepository,
    MarketplaceRepository,
    MessagingRepository,
    UserRepository,
)
from domain.objects import entities, dtos, exceptions, types, UserReputationRole
from domain.services import UserService


class TradingService:

    def __init__(
        self,
        trading_repository: TradingRepository,
        marketplace_repository: MarketplaceRepository,
        messaging_repository: MessagingRepository,
        user_repository: UserRepository,
        user_service: UserService,
    ) -> None:
        self.trading_repository = trading_repository
        self.marketplace_repository = marketplace_repository
        self.messaging_repository = messaging_repository
        self.user_repository = user_repository
        self.user_service = user_service

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
        elif deal.seller_id == user_id:
            await self.trading_repository.update_deal(
                id, dtos.UpdateDealDTO(seller_condition=condition)
            )
        else:
            raise exceptions.UserIsNotParticipantException(user_id)

        await self.change_status(id)

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

    async def create_scam_report(
        self, dto: dtos.CreateScamReportDTO
    ) -> entities.ScamReportEntity:
        scam_report_count = await self.trading_repository.get_scam_report_count(
            dto.user_id, types.ReportStatus.PENDING
        )

        if scam_report_count >= 3:
            raise exceptions.TooManyObjectsFoundException(
                "ScamReport", user_id=dto.user_id, status=types.ReportStatus.PENDING
            )

        return await self.trading_repository.create_scam_report(dto)

    async def update_scam_report(
        self, id: int, dto: dtos.UpdateScamReportDTO
    ) -> entities.ScamReportEntity:
        scam_report = await self.trading_repository.update_scam_report(id, dto)

        if dto.status == types.ReportStatus.APPROVED:
            await self.trading_repository.add_scam_report_count(scam_report.user_id)

        return scam_report

    async def get_scam_report(self, id: int) -> entities.ScamReportWithRelationsEntity:
        return await self.trading_repository.get_scam_report(id)

    async def get_scam_reports(
        self, reputation_user_id: int
    ) -> List[entities.ScamReportEntity]:
        return await self.trading_repository.get_scam_reports(reputation_user_id)

    async def get_user_scam_report_count(
        self, user_id: int, status: types.ReportStatus
    ) -> int:
        return await self.trading_repository.get_scam_report_count(user_id, status)

    async def review_exists(
        self, author_id: int, subject_user_id: int, subject_reputation_user_id: int
    ) -> bool:
        return await self.trading_repository.review_exists(
            author_id, subject_user_id, subject_reputation_user_id
        )

    async def get_reviews(
        self, dto: dtos.GetReviewsDTO
    ) -> List[entities.ReviewWithAuthorEntity]:
        return await self.trading_repository.get_reviews(dto)

    async def get_my_reviews(
        self, dto: dtos.GetMyReviewsDTO
    ) -> List[entities.ReviewWithSubjectEntity]:
        return await self.trading_repository.get_my_reviews(dto)

    async def get_review(self, id: int) -> entities.ReviewWithRelationsEntity:
        return await self.trading_repository.get_review(id)

    async def delete_my_review(self, id: int, user_id: int) -> None:
        await self.trading_repository.delete_my_review(id, user_id)

    async def delete_review(self, id: int) -> None:
        return await self.trading_repository.delete_review(id)

    async def create_review(self, dto: dtos.CreateReviewDTO) -> entities.ReviewEntity:
        reputation_user = await self.user_repository.get_reputation_user_by_user_id(
            dto.subject_user_id
        )

        if dto.subject_user_id == dto.author_id:
            raise exceptions.UserIsSelfException(dto.author_id, dto.subject_user_id)

        if reputation_user.role == UserReputationRole.SCAMMER:
            raise exceptions.UserIsScammerException(dto.subject_user_id)

        insert_review_dto = dtos.InsertReviewDTO(
            **dto.model_dump(),
            subject_reputation_user_id=reputation_user.id,
        )
        review = await self.trading_repository.create_review(insert_review_dto)
        await self.trading_repository.add_review_count(reputation_user.id)
        return review

    async def create_external_deal(
        self, dto: dtos.CreateExternalDealDTO
    ) -> entities.ExternalDealEntity:
        reputation_user = await self.user_service.get_warranty_reputation_user(
            [dto.agent_id] if dto.agent_id else [dto.seller_id, dto.buyer_id]
        )

        if reputation_user.role == UserReputationRole.DEPOSITOR and dto.agent_id:
            raise exceptions.UserIsNotGuarantorException(dto.agent_id)

        if dto.created_by_user_id not in [dto.seller_id, dto.buyer_id, dto.agent_id]:
            raise exceptions.UserIsNotParticipantException(dto.created_by_user_id)

        if (
            dto.seller_id == dto.buyer_id
            or dto.buyer_id == dto.agent_id
            or dto.agent_id == dto.seller_id
        ):
            raise exceptions.UserIsSelfException(
                dto.seller_id, dto.buyer_id, dto.agent_id
            )

        try:
            seller = await self.user_repository.get_reputation_user_by_user_id(
                dto.seller_id
            )

            if seller.role == UserReputationRole.SCAMMER:
                raise exceptions.UserIsScammerException(dto.seller_id)
        except exceptions.ObjectNotFoundException:
            pass

        try:
            buyer = await self.user_repository.get_reputation_user_by_user_id(
                dto.buyer_id
            )

            if buyer.role == UserReputationRole.SCAMMER:
                raise exceptions.UserIsScammerException(dto.buyer_id)
        except exceptions.ObjectNotFoundException:
            pass

        insert_external_deal_dto = dtos.InsertExternalDealDTO(
            **dto.model_dump(),
            refund_amount=min(dto.deal_amount, reputation_user.amount),
            warranty_reputation_user_id=reputation_user.id,
        )
        return await self.trading_repository.create_external_deal(
            insert_external_deal_dto
        )

    async def get_external_deal(
        self, id: int
    ) -> entities.ExternalDealWithRelationsEntity:
        return await self.trading_repository.get_external_deal(id)

    async def start_external_deal(
        self, id: int, user_id: int
    ) -> entities.ExternalDealEntity:
        external_deal = await self.trading_repository.get_external_deal(id)
        reputation_user = await self.user_repository.get_reputation_user_by_user_id(
            user_id
        )

        if external_deal.status != types.DealStatus.DRAFT:
            raise exceptions.DealNotDraftException(external_deal.id)

        if external_deal.warranty_reputation_user_id != reputation_user.id:
            raise exceptions.UserIsNotGuarantorException(user_id)

        if external_deal.agent_id:
            agent = await self.user_repository.get_reputation_user_by_user_id(
                external_deal.agent_id
            )

            if agent.role == UserReputationRole.SCAMMER:
                raise exceptions.UserIsScammerException(external_deal.agent_id)

            if not agent or agent.role not in [
                UserReputationRole.SMALL_GUARANTOR,
                UserReputationRole.GUARANTOR,
                UserReputationRole.BIG_GUARANTOR,
            ]:
                raise exceptions.UserIsNotGuarantorException(external_deal.agent_id)
        else:
            try:
                seller = await self.user_repository.get_reputation_user_by_user_id(
                    external_deal.seller_id
                )

                if seller.role == UserReputationRole.SCAMMER:
                    raise exceptions.UserIsScammerException(external_deal.seller_id)
            except exceptions.ObjectNotFoundException:
                pass

            try:
                buyer = await self.user_repository.get_reputation_user_by_user_id(
                    external_deal.buyer_id
                )

                if buyer.role == UserReputationRole.SCAMMER:
                    raise exceptions.UserIsScammerException(external_deal.buyer_id)
            except exceptions.ObjectNotFoundException:
                pass

        used_amount = await self.trading_repository.get_external_deal_amount(
            external_deal.warranty_reputation_user_id
        )

        if (
            used_amount + external_deal.refund_amount
            > external_deal.warranty_reputation_user.amount
        ):
            raise exceptions.NotEnoughAmountException(
                external_deal.warranty_reputation_user_id, external_deal.refund_amount
            )

        return await self.trading_repository.update_external_deal(
            external_deal.id,
            dtos.UpdateExternalDealDTO(status=types.DealStatus.PENDING),
        )

    async def change_external_deal_condition(
        self, id: int, user_id: int, condition: types.DealCondition
    ) -> None:
        deal = await self.trading_repository.get_external_deal(id)

        if (
            deal.seller_id != user_id
            and deal.buyer_id != user_id
            and deal.agent_id != user_id
        ):
            raise exceptions.UserIsNotParticipantException(user_id)

        if deal.status != types.DealStatus.PENDING:
            raise exceptions.DealNotPendingException(
                deal_id=id,
            )

        if deal.seller_id == user_id:
            await self.trading_repository.update_external_deal(
                id, dtos.UpdateExternalDealDTO(seller_condition=condition)
            )
        elif deal.buyer_id == user_id:
            await self.trading_repository.update_external_deal(
                id, dtos.UpdateExternalDealDTO(buyer_condition=condition)
            )
        else:
            raise exceptions.UserIsNotParticipantException(user_id)

        await self.change_external_deal_status(id)

    async def change_external_deal_status(self, id: int) -> None:
        deal = await self.trading_repository.get_external_deal(id)

        if deal.status != types.DealStatus.PENDING:
            raise exceptions.DealNotPendingException(
                deal_id=id,
            )

        if deal.expires_at < datetime.now():
            await self.trading_repository.update_external_deal(
                id, dtos.UpdateExternalDealDTO(status=types.DealStatus.EXPIRED)
            )
            return

        if (
            deal.seller_condition == types.DealCondition.COMPLAINT
            or deal.buyer_condition == types.DealCondition.COMPLAINT
        ):
            await self.trading_repository.update_external_deal(
                id, dtos.UpdateExternalDealDTO(status=types.DealStatus.REJECTED)
            )
        elif (
            deal.seller_condition == types.DealCondition.ACCEPTED
            and deal.buyer_condition == types.DealCondition.ACCEPTED
        ):
            await self.trading_repository.update_external_deal(
                id, dtos.UpdateExternalDealDTO(status=types.DealStatus.COMPLETED)
            )

            await self.user_repository.add_external_deal_count(
                deal.warranty_reputation_user_id
            )
        elif (
            deal.seller_condition == types.DealCondition.CANCELLED
            and deal.buyer_condition == types.DealCondition.CANCELLED
        ):
            await self.trading_repository.update_external_deal(
                id, dtos.UpdateExternalDealDTO(status=types.DealStatus.CANCELLED)
            )

    async def delete_external_deal(self, id: int, user_id: int) -> None:
        reputation_user = await self.user_repository.get_reputation_user_by_user_id(
            user_id
        )
        deal = await self.trading_repository.get_external_deal(id)

        if deal.status != types.DealStatus.DRAFT:
            raise exceptions.DealNotDraftException(deal.id)

        if deal.warranty_reputation_user_id != reputation_user.id:
            raise exceptions.UserIsNotGuarantorException(user_id)

        await self.trading_repository.delete_external_deal(id)

    async def expire_external_deals(
        self,
    ) -> List[entities.ExternalDealWithRelationsEntity]:
        expired_deals = await self.trading_repository.get_expired_external_deals()

        if not expired_deals:
            return []

        expired_ids = [deal.id for deal in expired_deals]
        await self.trading_repository.expire_external_deals()
        return await self.trading_repository.get_external_deals_by_ids(expired_ids)

    async def resolve_external_deal(self, id: int, status: types.DealStatus) -> None:
        if status not in [types.DealStatus.COMPLETED, types.DealStatus.CANCELLED]:
            raise exceptions.InvalidDataException(status=status)

        deal = await self.trading_repository.get_external_deal(id)

        if deal.status not in [types.DealStatus.EXPIRED, types.DealStatus.REJECTED]:
            raise exceptions.ExternalDealNotBlockedException(deal.id)

        await self.trading_repository.update_external_deal(
            id, dtos.UpdateExternalDealDTO(status=status)
        )

        if status == types.DealStatus.COMPLETED:
            await self.user_repository.add_external_deal_count(
                deal.warranty_reputation_user_id
            )

    async def create_or_update_external_deal_notification(
        self, dto: dtos.CreateExternalDealNotificationDTO
    ) -> entities.ExternalDealNotificationEntity:
        try:
            notification = await self.trading_repository.get_external_deal_notification(
                dto.external_deal_id, dto.user_id
            )
        except exceptions.ObjectNotFoundException:
            return await self.trading_repository.create_external_deal_notification(dto)

        return await self.trading_repository.update_external_deal_notification(
            notification.id,
            dtos.UpdateExternalDealNotificationDTO(
                telegram_message_id=dto.telegram_message_id,
                telegram_chat_id=dto.telegram_chat_id,
            ),
        )

    async def get_external_deal_notification(
        self, external_deal_id: int, user_id: int
    ) -> entities.ExternalDealNotificationEntity:
        return await self.trading_repository.get_external_deal_notification(
            external_deal_id, user_id
        )

    async def get_external_deal_amount(self, reputation_id: int) -> float:
        return await self.trading_repository.get_external_deal_amount(reputation_id)

    async def get_expired_external_deals(
        self,
    ) -> List[entities.ExternalDealWithRelationsEntity]:
        return await self.trading_repository.get_expired_external_deals()
