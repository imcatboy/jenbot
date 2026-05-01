from sqlalchemy.orm import joinedload, selectinload
from typing import List, Any

from domain.objects import models


def get_report_relations() -> List[Any]:
    return [
        joinedload(models.ReportModel.user),
        joinedload(models.ReportModel.accused_user),
        joinedload(models.ReportModel.applied_by_user),
    ]


def get_user_reputation_relations() -> List[Any]:
    return [
        joinedload(models.ReputationUserModel.user),
        joinedload(models.ReputationUserModel.added_by_user),
    ]


def get_violation_relations() -> List[Any]:
    return [
        joinedload(models.ChatViolationModel.user),
        joinedload(models.ChatViolationModel.applied_by_user),
    ]


def get_profile_relations() -> List[Any]:
    return [
        joinedload(models.UserModel.marketplace_user),
        joinedload(models.UserModel.reputation_user),
        selectinload(models.UserModel.violations),
    ]


def get_product_relations() -> List[Any]:
    return [
        joinedload(models.ProductModel.category),
        selectinload(models.ProductModel.product_types).selectinload(
            models.ProductTypeModel.options
        ),
    ]
