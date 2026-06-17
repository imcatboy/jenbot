from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from domain.objects import entities
from domain.objects.types import ReportType, ReportStatus, UserReputationRole
from bot.data.callbacks import *


REPORT_TYPE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💬 Снятие нарушения",
                callback_data=ReportCallback(type=ReportType.UNBAN).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="🚫 Нарушение",
                callback_data=ReportCallback(type=ReportType.VIOLATION).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Обратная связь",
                callback_data=ReportCallback(type=ReportType.FEEDBACK).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="🔍 Другое",
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


REPUTATION_ROLE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚫 Скамер",
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.SCAMMER
                ).pack(),
            ),
            InlineKeyboardButton(
                text="💵 Гарант",
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.GUARANTOR
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="💎 Большой гарант",
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.BIG_GUARANTOR
                ).pack(),
            ),
            InlineKeyboardButton(
                text="🪙 Младший гарант",
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.SMALL_GUARANTOR
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="💰 Депозитчик",
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.DEPOSITOR
                ).pack(),
            ),
            InlineKeyboardButton(
                text="👑 Админ",
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.ADMIN
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="👤 Чистый пользователь",
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.CLEAN_USER
                ).pack(),
            )
        ],
    ]
)


def get_cancel_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Отмена",
        callback_data=CancelCallback(user_id=user_id).pack(),
    )
    return builder.as_markup()


def get_skip_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Отмена",
        callback_data=CancelCallback(user_id=user_id).pack(),
    )
    builder.button(
        text="➡️ Пропустить",
        callback_data=SkipCallback(user_id=user_id).pack(),
    )
    return builder.adjust(2).as_markup()


def get_scam_report_keyboard(
    scam_report: entities.ScamReportWithRelationsEntity,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not scam_report.applied_by_user:
        builder.button(
            text="📌 Рассмотреть",
            callback_data=ScamReportAcceptCallback(id=scam_report.id).pack(),
        )
    else:
        if scam_report.status != ReportStatus.PENDING:
            builder.button(
                text="🔎 На рассмотрении",
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.PENDING
                ).pack(),
            )
        if scam_report.status != ReportStatus.APPROVED:
            builder.button(
                text="✅ Принять",
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.APPROVED
                ).pack(),
            )
        if scam_report.status != ReportStatus.REJECTED:
            builder.button(
                text="❌ Отклонить",
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.REJECTED
                ).pack(),
            )
        if scam_report.status != ReportStatus.CANCELLED:
            builder.button(
                text="⚠️ Отменить",
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.CANCELLED
                ).pack(),
            )

    return builder.adjust(3).as_markup()


def get_check_keyboard(
    reputation_user: entities.ReputationUserWithRelationsEntity,
    scam_reports: List[entities.ScamReportEntity],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"👤 Ссылка на профиль",
        url=f"tg://user?id={reputation_user.telegram_id}",
    )

    for scam_report in scam_reports:
        builder.button(
            text=f"📌 #{scam_report.id}",
            callback_data=CheckCallback(id=scam_report.id).pack(),
        )

    return builder.adjust(1, 2).as_markup()


def get_subscriptions_keyboard(subscriptions: List[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for subscription in subscriptions:
        builder.button(text="Подписаться", url=f"https://t.me/{subscription}")

    return builder.as_markup()


def get_report_keyboard(report: entities.ReportWithUserEntity) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if report.status != ReportStatus.PENDING:
        builder.button(
            text="🔎 На рассмотрение",
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.PENDING
            ).pack(),
        )
    if report.status != ReportStatus.APPROVED:
        builder.button(
            text="✅ Принять",
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.APPROVED
            ).pack(),
        )
    if report.status != ReportStatus.REJECTED:
        builder.button(
            text="❌ Отклонить",
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.REJECTED
            ).pack(),
        )
    if report.status != ReportStatus.CANCELLED:
        builder.button(
            text="⚠️ Отменить",
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
