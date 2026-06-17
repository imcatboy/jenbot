from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from domain.objects import entities
from domain.objects.types import ReportType, ReportStatus, UserReputationRole
from bot.data.callbacks import *


START_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji> Наш канал',
                url="https://t.me/larionnews",
            )
        ]
    ]
)


REPORT_TYPE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282953552405241953">🏷</tg-emoji> Снятие нарушения',
                callback_data=ReportCallback(type=ReportType.UNBAN).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5283215884712716244">�</tg-emoji> Нарушение',
                callback_data=ReportCallback(type=ReportType.VIOLATION).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Обратная связь',
                callback_data=ReportCallback(type=ReportType.FEEDBACK).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282953552405241953">🏷</tg-emoji> Другое',
                callback_data=ReportCallback(type=ReportType.OTHER).pack(),
            )
        ],
    ]
)


REVIEW_RATING_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji>',
                callback_data=ReviewRatingCallback(rating=1).pack(),
            ),
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji>',
                callback_data=ReviewRatingCallback(rating=2).pack(),
            ),
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji>',
                callback_data=ReviewRatingCallback(rating=3).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji>',
                callback_data=ReviewRatingCallback(rating=4).pack(),
            ),
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji><tg-emoji emoji-id="5282912415208480548">❤️</tg-emoji>',
                callback_data=ReviewRatingCallback(rating=5).pack(),
            ),
        ],
    ]
)


REPUTATION_ROLE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282962236829115303">⚠️</tg-emoji> Скамер',
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.SCAMMER
                ).pack(),
            ),
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Гарант',
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.GUARANTOR
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Большой гарант',
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.BIG_GUARANTOR
                ).pack(),
            ),
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Младший гарант',
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.SMALL_GUARANTOR
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Депозитчик',
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.DEPOSITOR
                ).pack(),
            ),
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5282858788246824770">✅</tg-emoji> Админ',
                callback_data=ReputationRoleCallback(
                    role=UserReputationRole.ADMIN
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text='<tg-emoji emoji-id="5280758334490713359">👤</tg-emoji> Чистый пользователь',
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
        text='<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Отмена',
        callback_data=CancelCallback(user_id=user_id).pack(),
    )
    return builder.as_markup()


def get_skip_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Отмена',
        callback_data=CancelCallback(user_id=user_id).pack(),
    )
    builder.button(
        text='<tg-emoji emoji-id="5282764234541801209">⬅️</tg-emoji> Пропустить',
        callback_data=SkipCallback(user_id=user_id).pack(),
    )
    return builder.adjust(2).as_markup()


def get_scam_report_keyboard(
    scam_report: entities.ScamReportWithRelationsEntity,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not scam_report.applied_by_user:
        builder.button(
            text='<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> Рассмотреть',
            callback_data=ScamReportAcceptCallback(id=scam_report.id).pack(),
        )
    else:
        if scam_report.status != ReportStatus.PENDING:
            builder.button(
                text='<tg-emoji emoji-id="5282953552405241953">🏷</tg-emoji> На рассмотрении',
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.PENDING
                ).pack(),
            )
        if scam_report.status != ReportStatus.APPROVED:
            builder.button(
                text='<tg-emoji emoji-id="5282782728670977815">✅</tg-emoji> Принять',
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.APPROVED
                ).pack(),
            )
        if scam_report.status != ReportStatus.REJECTED:
            builder.button(
                text='<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Отклонить',
                callback_data=ScamReportStatusCallback(
                    id=scam_report.id, status=ReportStatus.REJECTED
                ).pack(),
            )
        if scam_report.status != ReportStatus.CANCELLED:
            builder.button(
                text='<tg-emoji emoji-id="5283057370354719831">🛡</tg-emoji> Отменить',
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

    if (
        reputation_user.review_count > 0
        and reputation_user.role != UserReputationRole.SCAMMER
    ):
        builder.button(
            text=f'<tg-emoji emoji-id="5282973734456565994">💬</tg-emoji> Отзывы',
            callback_data=ReviewsCallback(
                reputation_user_id=reputation_user.id, offset=0, new_message=True
            ).pack(),
        )

    for scam_report in scam_reports:
        builder.button(
            text=f'<tg-emoji emoji-id="5280769308132155241">📌</tg-emoji> #{scam_report.id}',
            callback_data=CheckCallback(report_id=scam_report.id).pack(),
        )

    return builder.adjust(1, 2).as_markup()


def get_subscriptions_keyboard(subscriptions: List[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for subscription in subscriptions:
        builder.button(
            text="Подписаться", url=f"https://t.me/{subscription.replace('@', '')}"
        )

    return builder.as_markup()


def get_report_keyboard(report: entities.ReportWithUserEntity) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if report.status != ReportStatus.PENDING:
        builder.button(
            text='<tg-emoji emoji-id="5282953552405241953">🏷</tg-emoji> На рассмотрение',
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.PENDING
            ).pack(),
        )
    if report.status != ReportStatus.APPROVED:
        builder.button(
            text='<tg-emoji emoji-id="5282782728670977815">✅</tg-emoji> Принять',
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.APPROVED
            ).pack(),
        )
    if report.status != ReportStatus.REJECTED:
        builder.button(
            text='<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Отклонить',
            callback_data=ReportStatusCallback(
                id=report.id, status=ReportStatus.REJECTED
            ).pack(),
        )
    if report.status != ReportStatus.CANCELLED:
        builder.button(
            text='<tg-emoji emoji-id="5283057370354719831">🛡</tg-emoji> Отменить',
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
    external_deal: entities.ExternalDealWithUsersEntity,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='<tg-emoji emoji-id="5282782728670977815">✅</tg-emoji> Принять',
        callback_data=ExternalDealAcceptCallback(id=external_deal.id).pack(),
    )
    builder.button(
        text='<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Удалить',
        callback_data=ExternalDealDeleteCallback(id=external_deal.id).pack(),
    )
    return builder.adjust(2).as_markup()


def get_finish_external_deal_keyboard(
    external_deal: entities.ExternalDealWithUsersEntity,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='<tg-emoji emoji-id="5282782728670977815">✅</tg-emoji> Завершить',
        callback_data=FinishExternalDealCallback(id=external_deal.id).pack(),
    )
    builder.button(
        text='<tg-emoji emoji-id="5280622076653245714">❌</tg-emoji> Пожаловаться',
        callback_data=ComplainExternalDealCallback(id=external_deal.id).pack(),
    )
    return builder.adjust(2).as_markup()
