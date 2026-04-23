from sqlalchemy.orm import joinedload
from typing import List, Any

from objects import models


def get_report_relations() -> List[Any]:
    return [
        joinedload(models.ReportModel.user),
        joinedload(models.ReportModel.accused_user),
        joinedload(models.ReportModel.applied_by_user),
    ]

def get_user_reputation_relations() -> List[Any]:
    return [
        joinedload(models.UserReputationModel.user),
        joinedload(models.UserReputationModel.added_by_user),
    ]

def get_violation_relations() -> List[Any]:
    return [
        joinedload(models.ChatViolationModel.user),
        joinedload(models.ChatViolationModel.applied_by_user),
    ]