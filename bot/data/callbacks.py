from aiogram.filters.callback_data import CallbackData

from domain.objects.types import ReportType, ReportStatus, UserReputationRole


class ReportCallback(CallbackData, prefix="report"):
    type: ReportType


class ReportStatusCallback(CallbackData, prefix="report_status"):
    id: int
    status: ReportStatus


class ReportAccusedUserCallback(CallbackData, prefix="report_accussed_user"):
    id: int


class ReputationRoleCallback(CallbackData, prefix="reputation_role"):
    role: UserReputationRole


class CheckCallback(CallbackData, prefix="check"):
    report_id: int