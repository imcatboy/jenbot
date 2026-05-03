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
        joinedload(models.ProductModel.category).joinedload(
            models.CategoryModel.parent_category
        ),
        selectinload(models.ProductModel.product_types).selectinload(
            models.ProductTypeModel.options
        ),
        selectinload(models.ProductModel.images),
    ]


def get_advertisement_relations() -> List[Any]:
    return [
        selectinload(models.AdvertisementModel.options).options(
            selectinload(models.AdvertisementOptionModel.prices),
            selectinload(models.AdvertisementOptionModel.trades).selectinload(
                models.TradeModel.product_options
            ),
            selectinload(models.AdvertisementOptionModel.product_options),
        ),
    ]


def get_full_advertisement_relations() -> List[Any]:
    return [
        selectinload(models.AdvertisementModel.options).options(
            selectinload(models.AdvertisementOptionModel.prices).joinedload(
                models.AdvertisementOptionPriceModel.currency
            ),
            selectinload(models.AdvertisementOptionModel.trades).options(
                selectinload(models.TradeModel.product_options),
                joinedload(models.TradeModel.product).selectinload(
                    models.ProductModel.product_types
                ),
            ),
            selectinload(models.AdvertisementOptionModel.product_options),
        ),
        joinedload(models.AdvertisementModel.product).options(
            joinedload(models.ProductModel.category).joinedload(
                models.CategoryModel.parent_category
            ),
            selectinload(models.ProductModel.product_types).selectinload(
                models.ProductTypeModel.options
            ),
            selectinload(models.ProductModel.images),
        ),
        joinedload(models.AdvertisementModel.user).joinedload(
            models.UserModel.marketplace_user
        ),
    ]


def get_advertisement_option_relations() -> List[Any]:
    return [
        selectinload(models.AdvertisementOptionModel.advertisement).options(
            joinedload(models.AdvertisementModel.product).joinedload(
                models.ProductModel.category).joinedload(
                models.CategoryModel.parent_category
            ),
            joinedload(models.AdvertisementModel.user).joinedload(
                models.UserModel.marketplace_user
            ),
        ),
        selectinload(models.AdvertisementOptionModel.prices).joinedload(
            models.AdvertisementOptionPriceModel.currency
        ),
        selectinload(models.AdvertisementOptionModel.trades),
        selectinload(models.AdvertisementOptionModel.product_options),
    ]
