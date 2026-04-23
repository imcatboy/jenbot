from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import update
from typing import List

from objects.types import ViolationType
from .relations import get_report_relations, get_violation_relations
from objects import models, dtos, entities, exceptions
from .base import BaseRepository


class ModerationRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def add_violation(
        self, dto: dtos.AddViolationDTO
    ) -> entities.ViolationEntity:
        violation = models.ChatViolationModel(**dto.model_dump())
        await self.create_relation(violation, models.UserModel, dto.user_id)
        await self.create_relation(
            violation, models.UserModel, dto.applied_by_user_id, "applied_by_user_id"
        )
        self.session.add(violation)
        await self.session.flush()
        return entities.ViolationEntity.model_validate(violation)

    async def get_violations(
        self, user_id: int
    ) -> List[entities.ViolationWithUserEntity]:
        violations = await self.get_all_by_data(
            models.ChatViolationModel,
            options=get_violation_relations(),
            user_id=user_id,
        )
        return [
            entities.ViolationWithUserEntity.model_validate(violation)
            for violation in violations
        ]

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

    async def get_violation(self, violation_id: int) -> entities.ViolationEntity:
        violation = await self.get_by_id(models.ChatViolationModel, violation_id)
        return entities.ViolationEntity.model_validate(violation)

    async def set_violations_inactive(self, user_id: int, type: ViolationType) -> None:
        await self.session.execute(
            update(models.ChatViolationModel)
            .where(
                models.ChatViolationModel.user_id == user_id,
                models.ChatViolationModel.type == type,
            )
            .values(is_active=False)
        )

    async def add_report(self, dto: dtos.AddReportDTO) -> entities.ReportEntity:
        report = models.ReportModel(**dto.model_dump())
        await self.create_relation(report, models.UserModel, dto.user_id)
        await self.set_optional_relation(
            report, models.UserModel, dto.accused_user_id, "accused_user_id"
        )
        self.session.add(report)
        await self.session.flush()
        return entities.ReportEntity.model_validate(report)

    async def get_reports(
        self, dto: dtos.GetReportsDTO
    ) -> List[entities.ReportEntity]:
        query = select(models.ReportModel)
        
        if dto.user_id:
            query = query.where(models.ReportModel.user_id == dto.user_id)
        if dto.status:
            query = query.where(models.ReportModel.status == dto.status)
        if dto.report_type:
            query = query.where(models.ReportModel.report_type == dto.report_type)
        if dto.accused_user_id:
            query = query.where(models.ReportModel.accused_user_id == dto.accused_user_id)
        
        reports = await self.session.execute(query)
        return [entities.ReportEntity.model_validate(report) for report in reports.scalars().all()]

    async def get_report(self, report_id: int) -> entities.ReportWithUserEntity:
        report = await self.get_by_id(
            models.ReportModel, report_id, get_report_relations()
        )
        return entities.ReportWithUserEntity.model_validate(report)

    async def get_user_report(self, dto: dtos.GetUserReportDTO) -> entities.ReportEntity:
        query = select(models.ReportModel)
        query = query.where(
            models.ReportModel.id == dto.report_id,
            models.ReportModel.status == dto.status,
            models.ReportModel.report_type == dto.report_type,
        )
        report = await self.session.execute(query)
        report = report.scalar_one_or_none()

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

    async def get_violations_to_actualize(self) -> List[entities.ViolationWithUserEntity]:
        violations = await self.get_all_by_data(
            models.ChatViolationModel,
            is_active=True,
            options=get_violation_relations(),
        )
        return [entities.ViolationWithUserEntity.model_validate(violation) for violation in violations]