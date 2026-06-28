from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from domain.objects.types import (
    DealCondition,
    ReportType,
    ReportStatus,
    UserReputationRole,
    DealStatus,
)
from domain.objects import entities
from bot.data.callbacks import *


START_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Моя репутация",
                icon_custom_emoji_id="5283081795833731867",
                callback_data="my_reputation",
            ),
            InlineKeyboardButton(
                text="Подать жалобу",
                icon_custom_emoji_id="5282962236829115303",
                callback_data="create_scam_report",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Проверить",
                icon_custom_emoji_id="5282953552405241953",
                callback_data="check_user",
            ),
            InlineKeyboardButton(
                text="Оставленные отзывы",
                icon_custom_emoji_id="5282912415208480548",
                callback_data=MyReviewsCallback(offset=0).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Наш канал",
                icon_custom_emoji_id="5282912415208480548",
                url="https://t.me/larionnews",
            )
        ],
    ]
)


REPORT_TYPE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Снятие нарушения",
                icon_custom_emoji_id="5282764234541801209",
                callback_data=ReportCallback(type=ReportType.UNBAN).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Нарушение",
                icon_custom_emoji_id="5283215884712716244",
                callback_data=ReportCallback(type=ReportType.VIOLATION).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Обратная связь",
                icon_custom_emoji_id="5282973734456565994",
                callback_data=ReportCallback(type=ReportType.FEEDBACK).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Другое",
                icon_custom_emoji_id="5282953552405241953",
                callback_data=ReportCallback(type=ReportType.OTHER).pack(),
            )
        ],
    ]
)


REVIEW_RATING_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⭐",
                callback_data=ReviewRatingCallback(rating=1).pack(),
            ),
            InlineKeyboardButton(
                text="⭐⭐",
                callback_data=ReviewRatingCallback(rating=2).pack(),
            ),
            InlineKeyboardButton(
                text="⭐⭐⭐",
                callback_data=ReviewRatingCallback(rating=3).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="⭐⭐⭐⭐",
                callback_data=ReviewRatingCallback(rating=4).pack(),
            ),
            InlineKeyboardButton(
                text="⭐⭐⭐⭐⭐",
                callback_data=ReviewRatingCallback(rating=5).pack(),
            ),
        ],
    ]
)


def get_cancel_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отмена",
        icon_custom_emoji_id="5280622076653245714",
        callback_data=CancelCallback(user_id=user_id).pack(),
    )
    return builder.as_markup()


def get_attachments_keyboard(
    user_id: int,
    count: int,
    allow_skip: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if count > 0:
        builder.button(
            text="Посмотреть",
            icon_custom_emoji_id="5282953552405241953",
            callback_data=AttachmentsPreviewCallback(user_id=user_id).pack(),
        )
        builder.button(
            text="Готово",
            icon_custom_emoji_id="5282782728670977815",
            callback_data=AttachmentsDoneCallback(user_id=user_id).pack(),
        )
        builder.button(
            text="Очистить",
            icon_custom_emoji_id="5280799020715907724",
            callback_data=AttachmentsClearCallback(user_id=user_id).pack(),
        )

    if count == 0 and allow_skip:
        builder.button(
            text="Пропустить",
            icon_custom_emoji_id="5282959170222466892",
            callback_data=SkipCallback(user_id=user_id).pack(),
        )

    builder.button(
        text="Отмена",
        icon_custom_emoji_id="5280622076653245714",
        callback_data=CancelCallback(user_id=user_id).pack(),
    )

    if count > 0:
        return builder.adjust(2, 2).as_markup()

    if count == 0 and allow_skip:
        return builder.adjust(2).as_markup()

    return builder.as_markup()


def get_skip_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отмена",
        icon_custom_emoji_id="5280622076653245714",
        callback_data=CancelCallback(user_id=user_id).pack(),
    )
    builder.button(
        text="Пропустить",
        icon_custom_emoji_id="5282959170222466892",
        callback_data=SkipCallback(user_id=user_id).pack(),
    )
    return builder.adjust(2).as_markup()


def get_scam_report_keyboard(
    scam_report: entities.ScamReportWithRelationsEntity,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not scam_report.applied_by_user:
        builder.button(
            text="Рассмотреть",
            icon_custom_emoji_id="5280769308132155241",
            callback_data=ScamReportAcceptCallback(id=scam_report.id).pack(),
        )
    else:
        if scam_report.status != ReportStatus.PENDING:
            builder.button(
                text="На рассмотрении",
                icon_custom_emoji_id="5282953552405241953",
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.PENDING
                ).pack(),
            )
        if scam_report.status != ReportStatus.APPROVED:
            builder.button(
                text="Принять",
                icon_custom_emoji_id="5282782728670977815",
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.APPROVED
                ).pack(),
            )
        if scam_report.status != ReportStatus.REJECTED:
            builder.button(
                text="Отклонить",
                icon_custom_emoji_id="5280622076653245714",
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.REJECTED
                ).pack(),
            )
        if scam_report.status != ReportStatus.CANCELLED:
            builder.button(
                text="Отменить",
                icon_custom_emoji_id="5280799020715907724",
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.CANCELLED
                ).pack(),
            )

    return builder.adjust(3).as_markup()


def get_check_keyboard(
    bot_username: str,
    reputation_user: entities.ReputationUserWithRelationsEntity,
    scam_reports: List[entities.ScamReportEntity],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if reputation_user.role == UserReputationRole.SCAMMER:
        builder.button(
            text="Оспорить",
            icon_custom_emoji_id="5282764234541801209",
            callback_data="dispute_report",
        )

    builder.button(
        text="Пожаловаться",
        icon_custom_emoji_id="5283215884712716244",
        callback_data="create_scam_report",
    )

    if (
        reputation_user.review_count > 0
        and reputation_user.role != UserReputationRole.SCAMMER
    ):
        builder.button(
            text=f"Отзывы",
            icon_custom_emoji_id="5282912415208480548",
            callback_data=ReviewsCallback(
                reputation_user_id=reputation_user.id, offset=0, new_message=True
            ).pack(),
        )

    user = reputation_user.users[0] if reputation_user.users else None

    if reputation_user.role != UserReputationRole.SCAMMER and user:
        builder.button(
            text="Оставить отзыв",
            icon_custom_emoji_id="5282912415208480548",
            callback_data=ReviewCallback(user_id=user.id).pack(),
        )

    if user:
        builder.button(
            text="Ссылка на карточку",
            icon_custom_emoji_id="5282953552405241953",
            url=f"https://t.me/{bot_username}?start=check_{user.telegram_id}",
        )

    for scam_report in scam_reports:
        builder.button(
            text=f"Репорт #{scam_report.id}",
            icon_custom_emoji_id="5280769308132155241",
            callback_data=CheckCallback(report_id=scam_report.id).pack(),
        )

    return builder.adjust(2).as_markup()


def get_subscriptions_keyboard(subscriptions: List[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for subscription in subscriptions:
        builder.button(
            text="Подписаться", url=f"https://t.me/{subscription.replace('@', '')}"
        )

    return builder.as_markup()


def get_my_reviews_keyboard(
    offset: int,
    limit: int,
    reviews: List[entities.ReviewWithSubjectEntity],
    has_more: bool,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if offset > 0:
        builder.button(
            text="⬅️ Назад",
            callback_data=MyReviewsCallback(offset=max(0, offset - limit)).pack(),
        )

    if has_more:
        builder.button(
            text="➡️ Вперед",
            callback_data=MyReviewsCallback(offset=offset + limit).pack(),
        )

    for index, review in enumerate(reviews):
        builder.button(
            text=f"{index + 1}. Удалить отзыв",
            icon_custom_emoji_id="5280622076653245714",
            callback_data=ReviewDeleteCallback(
                id=review.id, offset=offset, accepted=False
            ).pack(),
        )

    return builder.adjust(2).as_markup()


def get_review_delete_keyboard(
    id: int,
    telegram_id: int,
    offset: int,
    message_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да, удалить отзыв",
        icon_custom_emoji_id="5280622076653245714",
        callback_data=ReviewDeleteCallback(
            id=id, offset=offset, accepted=True, message_id=message_id
        ).pack(),
    )
    builder.button(
        text="Отменить",
        icon_custom_emoji_id="5282782728670977815",
        callback_data=CancelCallback(user_id=telegram_id).pack(),
    )
    return builder.adjust(2).as_markup()


def get_review_admin_keyboard(
    review: entities.ReviewWithRelationsEntity,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отозвать отзыв",
        icon_custom_emoji_id="5280622076653245714",
        callback_data=ReviewDeleteAdminCallback(id=review.id).pack(),
    )
    return builder.as_markup()


def get_report_keyboard(report: entities.ReportWithUserEntity) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if report.status != ReportStatus.PENDING:
        builder.button(
            text="На рассмотрение",
            icon_custom_emoji_id="5282953552405241953",
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.PENDING
            ).pack(),
        )
    if report.status != ReportStatus.APPROVED:
        builder.button(
            text="Принять",
            icon_custom_emoji_id="5282782728670977815",
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.APPROVED
            ).pack(),
        )
    if report.status != ReportStatus.REJECTED:
        builder.button(
            text="Отклонить",
            icon_custom_emoji_id="5280622076653245714",
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.REJECTED
            ).pack(),
        )
    if report.status != ReportStatus.CANCELLED:
        builder.button(
            text="Отменить",
            icon_custom_emoji_id="5280799020715907724",
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.CANCELLED
            ).pack(),
        )

    return builder.adjust(3).as_markup()


def get_reputation_user_keyboard(
    reputation_users: List[entities.ReputationUserWithRelationsEntity],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for reputation_user in reputation_users:
        if not reputation_user.users:
            continue

        primary_user = reputation_user.users[0]

        if primary_user.usernames and primary_user.usernames[0].username:
            text = f"@{primary_user.usernames[0].username}"
        else:
            text = f"ID: {primary_user.telegram_id}"

        builder.button(
            text=text,
            callback_data=ReputationUserCallback(id=reputation_user.id).pack(),
        )

    return builder.as_markup()


def get_violations_keyboard(
    offset: int, limit: int, user_id: int, has_more: bool
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if offset > 0:
        builder.button(
            text="⬅️ Назад",
            callback_data=ViolationsCallback(
                user_id=user_id, offset=max(0, offset - limit)
            ).pack(),
        )

    if has_more:
        builder.button(
            text="➡️ Вперед",
            callback_data=ViolationsCallback(
                user_id=user_id, offset=offset + limit
            ).pack(),
        )

    return builder.adjust(2).as_markup()


def get_reviews_keyboard(
    offset: int, limit: int, reputation_user_id: int, has_more: bool
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if offset > 0:
        builder.button(
            text="⬅️ Назад",
            callback_data=ReviewsCallback(
                reputation_user_id=reputation_user_id,
                offset=max(0, offset - limit),
                new_message=False,
            ).pack(),
        )

    if has_more:
        builder.button(
            text="➡️ Вперед",
            callback_data=ReviewsCallback(
                reputation_user_id=reputation_user_id,
                offset=offset + limit,
                new_message=False,
            ).pack(),
        )

    return builder.adjust(2).as_markup()


def get_external_deal_accept_keyboard(
    external_deal: entities.ExternalDealWithRelationsEntity,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Начать сделку",
        icon_custom_emoji_id="5282782728670977815",
        callback_data=ChangeExternalDealDraftCallback(
            id=external_deal.id, is_accepted=True
        ).pack(),
    )
    builder.button(
        text="Удалить",
        icon_custom_emoji_id="5280622076653245714",
        callback_data=ChangeExternalDealDraftCallback(
            id=external_deal.id, is_accepted=False
        ).pack(),
    )
    return builder.adjust(2).as_markup()


def get_change_external_deal_status_keyboard(
    external_deal: entities.ExternalDealWithRelationsEntity,
    is_seller: bool,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    condition = (
        external_deal.seller_condition if is_seller else external_deal.buyer_condition
    )

    if condition not in [DealCondition.COMPLAINT, DealCondition.ACCEPTED]:
        builder.button(
            text="Завершить сделку",
            icon_custom_emoji_id="5282782728670977815",
            callback_data=ChangeExternalDealStatusCallback(
                id=external_deal.id, condition=DealCondition.ACCEPTED
            ).pack(),
        )

    if condition not in [DealCondition.COMPLAINT, DealCondition.CANCELLED]:
        builder.button(
            text="Отменить сделку",
            icon_custom_emoji_id="5280622076653245714",
            callback_data=ChangeExternalDealStatusCallback(
                id=external_deal.id, condition=DealCondition.CANCELLED
            ).pack(),
        )

    if not condition:
        builder.button(
            text="Подать жалобу",
            icon_custom_emoji_id="5283215884712716244",
            callback_data=ChangeExternalDealStatusCallback(
                id=external_deal.id, condition=DealCondition.COMPLAINT
            ).pack(),
        )

    return builder.adjust(3).as_markup()


def get_reputation_request_keyboard(
    reputation_request: entities.ReputationRequestWithUserEntity,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Одобрить",
        icon_custom_emoji_id="5282782728670977815",
        callback_data=ReputationRequestCallback(
            id=reputation_request.id, is_accepted=True
        ).pack(),
    )
    builder.button(
        text="Отклонить",
        icon_custom_emoji_id="5280622076653245714",
        callback_data=ReputationRequestCallback(
            id=reputation_request.id, is_accepted=False
        ).pack(),
    )
    return builder.adjust(2).as_markup()


def get_external_deal_first_role_keyboard(
    with_agent: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Продавец",
        icon_custom_emoji_id="5283081795833731867",
        callback_data=ExternalDealFirstRoleCallback(is_seller=True).pack(),
    )
    builder.button(
        text="Покупатель",
        icon_custom_emoji_id="5283081795833731867",
        callback_data=ExternalDealFirstRoleCallback(is_buyer=True).pack(),
    )

    if with_agent:
        builder.button(
            text="Посредник",
            icon_custom_emoji_id="5283081795833731867",
            callback_data=ExternalDealFirstRoleCallback(is_agent=True).pack(),
        )

    return builder.adjust(3).as_markup()


def get_resolve_external_deal_keyboard(
    external_deal: entities.ExternalDealWithRelationsEntity,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Завершить сделку",
        icon_custom_emoji_id="5282782728670977815",
        callback_data=ResolveExternalDealCallback(
            id=external_deal.id, status=DealStatus.COMPLETED
        ).pack(),
    )
    builder.button(
        text="Отменить сделку",
        icon_custom_emoji_id="5280622076653245714",
        callback_data=ResolveExternalDealCallback(
            id=external_deal.id, status=DealStatus.CANCELLED
        ).pack(),
    )
    return builder.adjust(2).as_markup()
