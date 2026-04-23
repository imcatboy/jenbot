from typing import List

from domain.repositories import ModerationRepository, UserRepository
from domain.objects.types import ViolationType, UserRole
from domain.objects import dtos, entities, exceptions
from domain.services import ConfigService


class ModerationService:

    def __init__(
        self,
        moderation_repository: ModerationRepository,
        user_repository: UserRepository,
        config_service: ConfigService,
    ) -> None:
        self.moderation_repository = moderation_repository
        self.user_repository = user_repository
        self.config_service = config_service

    async def add_violation(
        self, dto: dtos.AddViolationDTO
    ) -> entities.ViolationEntity:
        return await self.moderation_repository.add_violation(dto)

    async def get_violations(self, user_id: int) -> List[entities.ViolationEntity]:
        return await self.moderation_repository.get_violations(user_id)

    async def warn_user(self, dto: dtos.WarnUserDTO) -> entities.ViolationEntity:
        user = await self.user_repository.get(dto.user_id)

        if user.role != UserRole.USER:
            raise exceptions.ModerationException(
                dto.user_id, dto.telegram_chat_id, ViolationType.WARN
            )

        violation_dto = dtos.AddViolationDTO(
            **dto.model_dump(), type=ViolationType.WARN
        )
        violation = await self.add_violation(violation_dto)
        return violation

    async def unwarn_user(self, violation_id: int) -> None:
        violation = await self.moderation_repository.get_violation(violation_id)

        if violation.type != ViolationType.WARN:
            raise exceptions.ObjectNotFoundException("violation", [violation_id])

        await self.moderation_repository.set_violation_active(violation_id, False)

    async def add_report(self, dto: dtos.AddReportDTO) -> entities.ReportEntity:
        return await self.moderation_repository.add_report(dto)

    async def get_reports(
        self, dto: dtos.GetReportsDTO
    ) -> List[entities.ReportEntity]:
        return await self.moderation_repository.get_reports(dto)

    async def get_report(self, report_id: int) -> entities.ReportWithUserEntity:
        return await self.moderation_repository.get_report(report_id)
    
    async def get_user_report(self, dto: dtos.GetUserReportDTO) -> entities.ReportWithUserEntity:
        return await self.moderation_repository.get_user_report(dto)

    async def update_report(
        self,
        report_id: int,
        dto: dtos.UpdateReportDTO,
    ) -> None:
        return await self.moderation_repository.update_report(report_id, dto)

    async def get_violations_to_actualize(self) -> List[entities.ViolationWithUserEntity]:
        return await self.moderation_repository.get_violations_to_actualize()
    
    async def set_violations_active(self, ids: List[int], is_active: bool) -> None:
        return await self.moderation_repository.set_violations_active(ids, is_active)
    
    async def add_ban_word(self, word: str) -> None:
        words: List[str] = await self.config_service.get("ban_words", [])

        if word in words:
            raise exceptions.ObjectAlreadyExistsException("ban_word", [word])
        
        words.append(word)
        await self.config_service.set("ban_words", words)
    
    async def remove_ban_word(self, word: str) -> None:
        words: List[str] = await self.config_service.get("ban_words", [])

        if word not in words:
            raise exceptions.ObjectNotFoundException("ban_word", [word])
        
        words.remove(word)
        await self.config_service.set("ban_words", words)
    
    async def set_violations_inactive(self, user_id: int, violation_type: ViolationType) -> None:
        return await self.moderation_repository.set_violations_inactive(user_id, violation_type)