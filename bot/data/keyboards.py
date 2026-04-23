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
                text="⚠️ Скам", callback_data=ReportCallback(type=ReportType.SCAM).pack()
            )
        ],
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


REPORT_ATTACHMENTS_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
            InlineKeyboardButton(text="➡️ Пропустить", callback_data="skip"),
        ]
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
                text="🪙 Малый гарант",
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
    ]
)


CANCEL_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]]
)


def get_subscriptions_keyboard(subscriptions: List[int]) -> InlineKeyboardMarkup:
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

    if report.report_type == ReportType.SCAM and report.accused_user:
        builder.button(
            text=f"📌 Отметить как скам",
            callback_data=ReportAccusedUserCallback(id=report.accused_user.id).pack(),
        )

    return builder.adjust(3).as_markup()


def get_check_keyboard(reports: List[entities.ReportEntity]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for index, report in enumerate(reports):
        builder.button(
            text=f"📌 Репорт №{index + 1}",
            callback_data=CheckCallback(report_id=report.id).pack(),
        )

    return builder.adjust(3).as_markup()
