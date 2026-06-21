from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy import update
from typing import Dict, List, Optional

from domain.objects.types import ViolationType
from .relations import (
    get_report_relations,
    get_violation_relations,
    get_tracker_relations,
    get_reputation_request_relations,
)
from domain.objects import models, dtos, entities, exceptions
from .base import BaseRepository


class ModerationRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def add_violation(
        self, dto: dtos.AddViolationDTO
    ) -> entities.ChatViolationEntity:
        violation = models.ChatViolationModel(**dto.model_dump())
        await self.create_relation(violation, models.UserModel, dto.user_id)
        await self.create_relation(
            violation, models.UserModel, dto.applied_by_user_id, "applied_by_user_id"
        )
        self.session.add(violation)
        await self.session.flush()
        return entities.ChatViolationEntity.model_validate(violation)

    async def get_violations(
        self, dto: dtos.GetViolationsDTO
    ) -> List[entities.ChatViolationWithUserEntity]:
        query = (
            select(models.ChatViolationModel)
            .order_by(
                models.ChatViolationModel.is_active.desc(),
                models.ChatViolationModel.created_at.desc(),
            )
            .options(*get_violation_relations())
            .limit(dto.limit)
            .offset(dto.offset)
        )

        if dto.user_id is not None:
            query = query.where(models.ChatViolationModel.user_id == dto.user_id)
        if dto.applied_by_user_id is not None:
            query = query.where(
                models.ChatViolationModel.applied_by_user_id == dto.applied_by_user_id
            )
        if dto.start_date is not None:
            query = query.where(models.ChatViolationModel.created_at >= dto.start_date)
        if dto.end_date is not None:
            query = query.where(models.ChatViolationModel.created_at <= dto.end_date)
        if dto.is_active is not None:
            query = query.where(models.ChatViolationModel.is_active == dto.is_active)

        result = await self.session.execute(query)
        return [
            entities.ChatViolationWithUserEntity.model_validate(violation)
            for violation in result.scalars().all()
        ]

    async def get_violations_count(
        self, dto: dtos.GetViolationsDTO
    ) -> Dict[ViolationType, int]:
        query = select(
            models.ChatViolationModel.type, func.count(models.ChatViolationModel.id)
        )
        query = query.group_by(models.ChatViolationModel.type)

        if dto.user_id is not None:
            query = query.where(models.ChatViolationModel.user_id == dto.user_id)
        if dto.applied_by_user_id is not None:
            query = query.where(
                models.ChatViolationModel.applied_by_user_id == dto.applied_by_user_id
            )
        if dto.start_date is not None:
            query = query.where(models.ChatViolationModel.created_at >= dto.start_date)
        if dto.end_date is not None:
            query = query.where(models.ChatViolationModel.created_at <= dto.end_date)
        if dto.is_active is not None:
            query = query.where(models.ChatViolationModel.is_active == dto.is_active)

        result = await self.session.execute(query)
        return dict(result.all())

    async def get_applied_scam_reports_count(
        self, dto: dtos.GetAppliedScamReportsCountDTO
    ) -> int:
        query = select(func.count(models.ScamReportModel.id))

        if dto.applied_by_user_id is not None:
            query = query.where(
                models.ScamReportModel.applied_by_user_id == dto.applied_by_user_id
            )
        if dto.start_date is not None:
            query = query.where(models.ScamReportModel.created_at >= dto.start_date)
        if dto.end_date is not None:
            query = query.where(models.ScamReportModel.created_at <= dto.end_date)
        if dto.status is not None:
            query = query.where(models.ScamReportModel.status == dto.status)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def set_violation_active(self, violation_id: int, is_active: bool) -> None:
        violation = await self.get_by_id(models.ChatViolationModel, violation_id)
        violation.is_active = is_active

    async def set_violations_active(self, ids: List[int], is_active: bool) -> None:
        await self.session.execute(
            update(models.ChatViolationModel)
            .where(models.ChatViolationModel.id.in_(ids))
            .values(is_active=is_active)
        )
        await self.session.flush()

    async def get_violation(
        self, violation_id: int
    ) -> entities.ChatViolationWithUserEntity:
        violation = await self.get_by_id(
            models.ChatViolationModel, violation_id, get_violation_relations()
        )
        return entities.ChatViolationWithUserEntity.model_validate(violation)

    async def set_violations_inactive(self, user_id: int, type: ViolationType) -> None:
        await self.session.execute(
            update(models.ChatViolationModel)
            .where(
                models.ChatViolationModel.user_id == user_id,
                models.ChatViolationModel.type == type,
            )
            .values(is_active=False)
        )

    async def delete_violation(self, violation_id: int) -> None:
        violation = await self.get_by_id(models.ChatViolationModel, violation_id)
        await self.session.delete(violation)

    async def add_report(self, dto: dtos.AddReportDTO) -> entities.ReportEntity:
        report = models.ReportModel(**dto.model_dump())
        await self.create_relation(report, models.UserModel, dto.user_id)
        await self.set_optional_relation(
            report, models.UserModel, dto.accused_user_id, "accused_user_id"
        )
        self.session.add(report)
        await self.session.flush()
        return entities.ReportEntity.model_validate(report)

    async def get_reports(self, dto: dtos.GetReportsDTO) -> List[entities.ReportEntity]:
        query = select(models.ReportModel)

        if dto.user_id:
            query = query.where(models.ReportModel.user_id == dto.user_id)
        if dto.status:
            query = query.where(models.ReportModel.status == dto.status)
        if dto.type:
            query = query.where(models.ReportModel.type == dto.type)
        if dto.accused_user_id:
            query = query.where(
                models.ReportModel.accused_user_id == dto.accused_user_id
            )

        reports = await self.session.execute(query)
        return [
            entities.ReportEntity.model_validate(report)
            for report in reports.scalars().all()
        ]

    async def get_report(self, report_id: int) -> entities.ReportWithUserEntity:
        report = await self.get_by_id(
            models.ReportModel, report_id, get_report_relations()
        )
        return entities.ReportWithUserEntity.model_validate(report)

    async def get_user_report(
        self, dto: dtos.GetUserReportDTO
    ) -> entities.ReportEntity:
        query = select(models.ReportModel)
        query = query.where(
            models.ReportModel.id == dto.report_id,
            models.ReportModel.status == dto.status,
            models.ReportModel.type == dto.type,
        )
        result = await self.session.execute(query)
        report = result.scalar_one_or_none()

        if not report:
            raise exceptions.ObjectNotFoundException("report", [dto.report_id])

        return entities.ReportEntity.model_validate(report)

    async def update_report(
        self,
        report_id: int,
        dto: dtos.UpdateReportDTO,
    ) -> None:
        await self.session.execute(
            update(models.ReportModel)
            .where(models.ReportModel.id == report_id)
            .values(
                status=dto.status,
                admin_comment=dto.admin_comment,
                applied_by_user_id=dto.applied_by_user_id,
            )
        )

    async def get_violations_to_actualize(
        self,
    ) -> List[entities.ChatViolationWithUserEntity]:
        violations = await self.get_all_by_data(
            models.ChatViolationModel,
            is_active=True,
            options=get_violation_relations(),
        )
        return [
            entities.ChatViolationWithUserEntity.model_validate(violation)
            for violation in violations
        ]

    async def add_tracker(
        self, dto: dtos.AddTrackerDTO
    ) -> entities.TrackerWithUserEntity:
        await self.validator.validate_data_not_exists(
            models.TrackerModel,
            tracked_user_id=dto.tracked_user_id,
            tracking_user_id=dto.tracking_user_id,
            is_active=True,
        )
        tracker = models.TrackerModel(**dto.model_dump())
        await self.create_relation(
            tracker, models.UserModel, dto.tracked_user_id, "tracked_user_id"
        )
        await self.create_relation(
            tracker, models.UserModel, dto.tracking_user_id, "tracking_user_id"
        )
        self.session.add(tracker)
        await self.session.flush()
        tracker = await self.get_by_id(
            models.TrackerModel, tracker.id, get_tracker_relations()
        )
        return entities.TrackerWithUserEntity.model_validate(tracker)

    async def disable_tracker(
        self, tracked_user_id: int, tracking_user_id: int
    ) -> None:
        await self.session.execute(
            update(models.TrackerModel)
            .where(
                models.TrackerModel.tracked_user_id == tracked_user_id,
                models.TrackerModel.tracking_user_id == tracking_user_id,
            )
            .values(is_active=False)
        )
        await self.session.flush()

    async def get_trackers(self, user_id: int) -> List[entities.TrackerWithUserEntity]:
        trackers = await self.get_all_by_data(
            models.TrackerModel,
            tracked_user_id=user_id,
            is_active=True,
            options=get_tracker_relations(),
        )
        return [
            entities.TrackerWithUserEntity.model_validate(tracker)
            for tracker in trackers
        ]

    async def create_reputation_request(
        self, user_id: int, about: Optional[str] = None
    ) -> entities.ReputationRequestEntity:
        reputation_request = models.ReputationRequestModel(
            about=about,
        )
        await self.create_relation(reputation_request, models.UserModel, user_id)
        self.session.add(reputation_request)
        await self.session.flush()
        return entities.ReputationRequestEntity.model_validate(reputation_request)

    async def update_reputation_request(self, id: int, applied_by_user_id: int) -> None:
        reputation_request = await self.get_by_id(models.ReputationRequestModel, id)
        await self.set_optional_relation(
            reputation_request,
            models.UserModel,
            applied_by_user_id,
            "applied_by_user_id",
        )
        reputation_request.is_active = False
        await self.session.flush()

    async def has_active_reputation_request(self, user_id: int) -> bool:
        result = await self.session.execute(
            select(models.ReputationRequestModel.id)
            .where(
                models.ReputationRequestModel.user_id == user_id,
                models.ReputationRequestModel.is_active == True,
            )
            .exists()
            .select()
        )
        return result.scalar() or False

    async def get_reputation_request(
        self, id: int
    ) -> entities.ReputationRequestWithUserEntity:
        reputation_request = await self.get_by_id(
            models.ReputationRequestModel,
            id,
            options=get_reputation_request_relations(),
        )
        return entities.ReputationRequestWithUserEntity.model_validate(
            reputation_request
        )
