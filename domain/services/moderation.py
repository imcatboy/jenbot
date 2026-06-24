from typing import Dict, List, Optional

from domain.objects.types import ViolationType, UserRole, UserReputationRole
from domain.repositories import ModerationRepository, UserRepository
from domain.objects import dtos, entities, exceptions
from domain.services import ConfigService
from domain.cache import ModerationCache


class ModerationService:

    def __init__(
        self,
        moderation_repository: ModerationRepository,
        user_repository: UserRepository,
        config_service: ConfigService,
        moderation_cache: ModerationCache,
    ) -> None:
        self.moderation_repository = moderation_repository
        self.user_repository = user_repository
        self.config_service = config_service
        self.moderation_cache = moderation_cache

    async def add_violation(
        self, dto: dtos.AddViolationDTO
    ) -> entities.ChatViolationEntity:
        return await self.moderation_repository.add_violation(dto)

    async def get_violations(
        self, dto: dtos.GetViolationsDTO
    ) -> List[entities.ChatViolationWithUserEntity]:
        return await self.moderation_repository.get_violations(dto)

    async def get_violations_count(
        self, dto: dtos.GetViolationsDTO
    ) -> Dict[ViolationType, int]:
        return await self.moderation_repository.get_violations_count(dto)

    async def get_violation(
        self, violation_id: int
    ) -> entities.ChatViolationWithUserEntity:
        return await self.moderation_repository.get_violation(violation_id)

    async def warn_user(self, dto: dtos.WarnUserDTO) -> entities.ChatViolationEntity:
        user = await self.user_repository.get(dto.user_id)

        if user.role != UserRole.USER:
            raise exceptions.ModerationException(dto.user_id, ViolationType.WARN)

        violation_dto = dtos.AddViolationDTO(
            **dto.model_dump(), type=ViolationType.WARN
        )
        return await self.add_violation(violation_dto)

    async def unwarn_user(self, violation_id: int) -> None:
        violation = await self.moderation_repository.get_violation(violation_id)

        if violation.type != ViolationType.WARN:
            raise exceptions.ObjectNotFoundException("violation", [violation_id])

        await self.moderation_repository.delete_violation(violation_id)

    async def add_report(self, dto: dtos.AddReportDTO) -> entities.ReportEntity:
        return await self.moderation_repository.add_report(dto)

    async def get_reports(self, dto: dtos.GetReportsDTO) -> List[entities.ReportEntity]:
        return await self.moderation_repository.get_reports(dto)

    async def get_report(self, report_id: int) -> entities.ReportWithUserEntity:
        return await self.moderation_repository.get_report(report_id)

    async def get_user_report(
        self, dto: dtos.GetUserReportDTO
    ) -> entities.ReportWithUserEntity:
        return await self.moderation_repository.get_user_report(dto)

    async def update_report(
        self,
        report_id: int,
        dto: dtos.UpdateReportDTO,
    ) -> None:
        return await self.moderation_repository.update_report(report_id, dto)

    async def get_violations_to_actualize(
        self,
    ) -> List[entities.ChatViolationWithUserEntity]:
        return await self.moderation_repository.get_violations_to_actualize()

    async def set_violations_active(self, ids: List[int], is_active: bool) -> None:
        return await self.moderation_repository.set_violations_active(ids, is_active)

    async def add_ban_word(self, word: str) -> None:
        words: List[str] = await self.config_service.get("ban_words", [])

        if word in words:
            raise exceptions.ObjectAlreadyExistsException("ban_word", word=word)

        words.append(word)
        await self.config_service.set("ban_words", words)

    async def remove_ban_word(self, word: str) -> None:
        words: List[str] = await self.config_service.get("ban_words", [])

        if word not in words:
            raise exceptions.ObjectNotFoundException("ban_word", word=word)

        words.remove(word)
        await self.config_service.set("ban_words", words)

    async def set_violations_inactive(
        self, user_id: int, violation_type: ViolationType
    ) -> None:
        return await self.moderation_repository.set_violations_inactive(
            user_id, violation_type
        )

    async def add_tracker(
        self, dto: dtos.AddTrackerDTO
    ) -> entities.TrackerWithUserEntity:
        tracker = await self.moderation_repository.add_tracker(dto)
        trackers = await self.moderation_repository.get_trackers(dto.tracked_user_id)
        await self.moderation_cache.set_trackers(dto.tracked_user_id, trackers)
        return tracker

    async def get_trackers(
        self, tracked_user_id: int
    ) -> List[entities.TrackerWithUserEntity]:
        trackers = await self.moderation_cache.get_trackers(tracked_user_id)

        if trackers:
            return trackers

        trackers = await self.moderation_repository.get_trackers(tracked_user_id)
        await self.moderation_cache.set_trackers(tracked_user_id, trackers)
        return trackers

    async def set_tracker_message(self, tracker_id: int, message_id: int) -> None:
        await self.moderation_cache.set_tracker_message(tracker_id, message_id)

    async def get_tracker_message(self, tracker_id: int) -> int | None:
        return await self.moderation_cache.get_tracker_message(tracker_id)

    async def disable_tracker(
        self, tracked_user_id: int, tracking_user_id: int
    ) -> None:
        await self.moderation_repository.disable_tracker(
            tracked_user_id, tracking_user_id
        )
        await self.moderation_cache.invalidate_trackers(tracked_user_id)

    async def create_reputation_request(
        self, user_id: int, about: Optional[str] = None
    ) -> entities.ReputationRequestEntity:
        if await self.has_active_reputation_request(user_id):
            raise exceptions.ReputationRequestAlreadyExistsException(user_id)

        return await self.moderation_repository.create_reputation_request(
            user_id, about
        )

    async def update_reputation_request(
        self, id: int, applied_by_user_id: int, accepted: bool
    ) -> None:
        reputation_request = await self.moderation_repository.get_reputation_request(id)

        if not reputation_request.is_active:
            raise exceptions.ObjectNotFoundException("reputation_request", [id])

        if not accepted:
            return await self.moderation_repository.update_reputation_request(
                id, applied_by_user_id
            )

        try:
            reputation_user = await self.user_repository.get_reputation_user_by_user_id(
                reputation_request.user_id
            )
            dto = dtos.UpdateReputationUserDTO(
                about=reputation_request.about,
                version=reputation_user.version,
                added_by_user_id=applied_by_user_id,
            )
            await self.user_repository.update_reputation_user(reputation_user.id, dto)
        except exceptions.ObjectNotFoundException:
            dto = dtos.CreateReputationUserDTO(
                user_ids=[reputation_request.user_id],
                about=reputation_request.about,
                role=UserReputationRole.CLEAN_USER,
                added_by_user_id=applied_by_user_id,
            )
            await self.user_repository.create_reputation_user(dto)

        return await self.moderation_repository.update_reputation_request(
            id, applied_by_user_id
        )

    async def get_reputation_request(
        self, id: int
    ) -> entities.ReputationRequestWithUserEntity:
        return await self.moderation_repository.get_reputation_request(id)

    async def has_active_reputation_request(self, user_id: int) -> bool:
        return await self.moderation_repository.has_active_reputation_request(user_id)

    async def get_applied_scam_reports_count(
        self, dto: dtos.GetAppliedScamReportsCountDTO
    ) -> int:
        return await self.moderation_repository.get_applied_scam_reports_count(dto)
