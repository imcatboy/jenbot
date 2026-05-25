from typing import Annotated, Dict, Type, get_args, get_origin, List
from aiogram.filters import CommandObject
from pydantic.fields import FieldInfo
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from html import escape

from domain.objects import entities, types


COMMAND_ARGUMENTS_ERROR = "⚠️ Ошибка! Команда требует аргументов.\n\n<code>{0}</code>"
COMMAND_ARGUMENTS_COUNT_ERROR = "❌ Неверное число аргументов.\n\n<code>{0}</code>"
COMMAND_ARGUMENTS_VALIDATION_ERROR = "🚫 Ошибка валидации!\n\n<code>{0}</code>"
USER_NOT_ALLOWED_TO_ACTION = "❌ Вы не имеете прав на выполнение этого действия."
VIOLATIONS_OTHER_USER_FORBIDDEN = "❌ Просмотр нарушений другого пользователя доступен только модераторам и администраторам."
BAN_USER_SUCCESS = "🔒 Пользователь <b>{0}</b> заблокирован до <b>{1}</b>\n\n<b>Причина</b>\n<blockquote>{2}</blockquote>."
BAN_USER_WITHOUT_EXPIRES_AT_SUCCESS = "🔒 Пользователь <b>{0}</b> заблокирован\n\n<b>Причина</b>\n<blockquote>{1}</blockquote>."
USER_NOT_FOUND = "❌ Пользователь {0} не найден."
UNBAN_USER_SUCCESS = "🔓 Пользователь {0} разблокирован."
MUTE_USER_SUCCESS = "🔇 Пользователь <b>{0}</b> замьючен до <b>{1}</b>\n\n<b>Причина</b>\n<blockquote>{2}</blockquote>."
MUTE_USER_WITHOUT_EXPIRES_AT_SUCCESS = (
    "🔇 Пользователь {0} замьючен\n\n<b>Причина</b>\n<blockquote>{1}</blockquote>."
)
UNMUTE_USER_SUCCESS = "💤 Пользователь {0} размьючен."
WARN_USER_SUCCESS = "⚠️ Пользователь <b>{0}</b> предупрежден до <b>{1}</b>\n\n<b>Причина</b>\n<blockquote>{2}</blockquote>."
WARN_USER_WITHOUT_EXPIRES_AT_SUCCESS = (
    "⚠️ Пользователь {0} предупрежден\n\n<b>Причина</b>\n<blockquote>{1}</blockquote>."
)
REPORT_ACCUSED_USER_ID_MESSAGE = (
    "🔍 Введите ID пользователя, которого вы хотите обвинить в нарушении."
)
CANNOT_USE_ACTION_ON_MODERATOR = (
    "❌ Вы не можете использовать это действие на модераторе."
)
STATE_VALIDATION_ERROR = "❌ Ошибка введённого значения, попробуйте ещё раз."
SET_SETTING_SUCCESS = "💬 Настройка <b>{0}</b> установлена."
UNWARN_USER_SUCCESS = "💤 Предупреждение стало неактивным."
OBJECT_NOT_FOUND = "❌ Запрашиваемый объект не найден."
OBJECT_ALREADY_EXISTS = "❌ Объект с такими данными уже существует."
GET_MY_ID_SUCCESS = "🪪 Ваш ID: {0}"
GET_USER_ID_SUCCESS = "🪪 ID пользователя {0}"
ADD_MODERATOR_SUCCESS = "👮 Пользователь {0} стал модератором."
REMOVE_MODERATOR_SUCCESS = "👤 Пользователь {0} стал обычным пользователем."
SUBSCRIPTION_ERROR = "❌ Вы не подписаны на каналы, необходимые для использования бота. Пожалуйста, подпишитесь на каналы и попробуйте снова."
REPORT_TYPE_MESSAGE = "📌 Выберите тип обращения."
REPORT_REASON_MESSAGE = "💬 Введите причину обращения (до 1024 символов)."
REPORT_ATTACHMENTS_MESSAGE = (
    "📎 Прикрепите фото или видео до 40 МБ одним сообщением (если есть)."
)
REPORT_ATTACHMENTS_ERROR = "❌ Пожалуйста, отправьте фото или видео."
REPORT_USERNAME_NOT_FOUND = "❌ Пользователь {0} не найден. Попробуйте ввести его ID."
REPORT_USERNAME_MESSAGE = "🔍 Я ранее не видел этого пользователя. Введите его username, если есть, иначе пропустите."
THROTTLE_ERROR = "⏳ Пожалуйста, не спамьте."
REPORT_SUCCESS = (
    "🔍 Отправлено успешно. В случае ответа вам будет отправлено уведомление."
)
REPORT_WITH_ATTACHMENTS_SUCCESS = "🔍 Отправлено успешно с {0} медиа. В случае ответа вам будет отправлено уведомление."
STATE_CANCELLED = "↩️ Действие отменено."
REPORT_ALREADY_PENDING = (
    "❌ Вы уже имеете незавершенное обращение. Пожалуйста, дождитесь его обработки."
)
USERNAME_OR_REPLY_TO_USER_REQUIRED = (
    "❌ Имя пользователя или ответ на сообщение является обязательным."
)
SET_REPUTATION_ROLE_MESSAGE = "💬 Выберите роль пользователя."
SET_REPUTATION_DESCRIPTION_MESSAGE = (
    "💬 Введите описание для репутации (до 255 символов)."
)
REPORT_COMMENT_MESSAGE = "💬 Введите комментарий к обращению (до 1024 символов)."
REPORT_STATUS_UPDATED = "🔍 Статус обращения успешно изменен."
REPORT_ACCUSED_DESCRIPTION_MESSAGE = "💬 Введите описание нарушения (до 255 символов)."
REPORT_ACCUSED_USER_UPDATED = "📌 Пользователь успешно отмечен как скам."
SET_REPUTATION_SUCCESS = "📌 Репутация пользователя успешно установлена."
ADD_BAN_WORD_SUCCESS = "📌 Слово <b>{0}</b> успешно добавлено в список запрещённых."
REMOVE_BAN_WORD_SUCCESS = "📌 Слово <b>{0}</b> успешно удалено из списка запрещённых."
BAN_WORD_ERROR = (
    "❌ <b>{0}</b> использовал запрещённое слово <tg-spoiler>{1}</tg-spoiler>."
)
VIOLATIONS_COUNT_OTHER_USER_FORBIDDEN = (
    "❌ Просмотр статистики нарушений только других модераторов и администраторов."
)
VIOLATIONS = {
    types.ViolationType.WARN: "⚠️ Предупреждение",
    types.ViolationType.MUTE: "🔇 Мьют",
    types.ViolationType.BAN: "🔒 Бан",
}
CHAT_ACTIONS = {
    types.ChatAction.UNMUTE: "💤 Размьют",
    types.ChatAction.UNWARN: "💤 Снятие предупреждения",
    types.ChatAction.UNBAN: "🔓 Снятие бана",
}
REPORT_TYPES = {
    types.ReportType.SCAM: "⚠️ Скам",
    types.ReportType.UNBAN: "💬 Снятие нарушения",
    types.ReportType.VIOLATION: "🚫 Нарушение",
    types.ReportType.FEEDBACK: "💬 Обратная связь",
    types.ReportType.OTHER: "🔍 Другое",
}
REPORT_STATUSES = {
    types.ReportStatus.PENDING: "🔎 Ожидает рассмотрения",
    types.ReportStatus.APPROVED: "✅ Принято",
    types.ReportStatus.REJECTED: "❌ Отклонено",
    types.ReportStatus.CANCELLED: "⚠️ Отменено",
}
REPUTATION_ROLES = {
    types.UserReputationRole.SCAMMER: "🚫 Скамер",
    types.UserReputationRole.GUARANTOR: "💵 Гарант",
    types.UserReputationRole.BIG_GUARANTOR: "💎 Большой гарант",
    types.UserReputationRole.SMALL_GUARANTOR: "🪙 Малый гарант",
    types.UserReputationRole.DEPOSITOR: "💰 Депозитчик",
    types.UserReputationRole.ADMIN: "👑 Админ",
}
HOMOGLYPHS = str.maketrans("ayBkKMnoPpCcTyXxeE", "ауВкКМноРрСсТуХхеЕ")


def _usage_label_for_field(name: str, field_info: FieldInfo) -> str:
    if field_info.description:
        return field_info.description

    ann = field_info.annotation
    nested = _description_from_annotation(ann)
    return nested if nested is not None else name


def _description_from_annotation(annotation: object) -> str | None:
    if annotation is None or annotation is type(None):
        return None

    origin = get_origin(annotation)

    if origin is Annotated:
        args = get_args(annotation)

        for meta in args[1:]:
            if isinstance(meta, FieldInfo) and meta.description:
                return meta.description

        if args:
            return _description_from_annotation(args[0])

        return None

    if origin is not None:
        for arg in get_args(annotation):
            if arg is type(None):
                continue

            found = _description_from_annotation(arg)

            if found is not None:
                return found

    return None


def format_user_handle(username: Optional[str], telegram_id: int) -> str:
    return f"@{username}" if username else f"<code>{telegram_id}</code>"


def get_command_usage(command: CommandObject, model: Type[BaseModel]) -> str:
    fields = []

    for name, field_info in model.model_fields.items():
        if field_info.is_required():
            fields.append(f"[{_usage_label_for_field(name, field_info)}]")
        else:
            fields.append(f"({_usage_label_for_field(name, field_info)})")

    return f"/{command.command} {' '.join(fields)}"


def get_ban_user_success_message(
    username: str, expires_at: Optional[datetime], reason: str
) -> str:
    if expires_at:
        return BAN_USER_SUCCESS.format(
            escape(username), expires_at.strftime("%d.%m.%Y %H:%M"), escape(reason)
        )
    else:
        return BAN_USER_WITHOUT_EXPIRES_AT_SUCCESS.format(
            escape(username), escape(reason)
        )


def get_mute_user_success_message(
    username: str, expires_at: Optional[datetime], reason: str
) -> str:
    if expires_at:
        return MUTE_USER_SUCCESS.format(
            escape(username), expires_at.strftime("%d.%m.%Y %H:%M"), escape(reason)
        )
    else:
        return MUTE_USER_WITHOUT_EXPIRES_AT_SUCCESS.format(
            escape(username), escape(reason)
        )


def get_warn_user_success_message(
    username: str, expires_at: Optional[datetime], reason: str
) -> str:
    if expires_at:
        return WARN_USER_SUCCESS.format(
            escape(username), expires_at.strftime("%d.%m.%Y %H:%M"), escape(reason)
        )
    else:
        return WARN_USER_WITHOUT_EXPIRES_AT_SUCCESS.format(
            escape(username), escape(reason)
        )


def get_violations_message(
    violations: List[entities.ChatViolationWithUserEntity],
) -> str:
    message = "🚨 <b>Нарушения</b>\n\n"
    active_violations = [violation for violation in violations if violation.is_active]
    inactive_violations = [
        violation for violation in violations if not violation.is_active
    ]

    if active_violations:
        message += "🟢 <b>Активные нарушения</b>\n"

    for violation in active_violations:
        message += (
            f"📌 #<code>{violation.id}</code> <b>{VIOLATIONS[violation.type]}</b>\n"
        )
        message += f"<blockquote>"
        message += f"{escape(violation.reason)}\n"
        message += f"Выдан {format_user_handle(violation.applied_by_user.username, violation.applied_by_user.telegram_id)}\n"
        message += f"От {violation.created_at.strftime('%d.%m.%Y %H:%M')}"

        if violation.expires_at:
            message += f"\nДо {violation.expires_at.strftime('%d.%m.%Y %H:%M')}"

        message += "</blockquote>\n\n"

    if inactive_violations:
        message += "🔴 <b>Неактивные нарушения</b>\n"

    for violation in inactive_violations:
        message += (
            f"📌 #<code>{violation.id}</code> <b>{VIOLATIONS[violation.type]}</b>\n"
        )
        message += f"<blockquote>"
        message += f"{escape(violation.reason)}\n"
        message += f"Выдан {format_user_handle(violation.applied_by_user.username, violation.applied_by_user.telegram_id)}\n"
        message += f"От {violation.created_at.strftime('%d.%m.%Y %H:%M')}"

        if violation.expires_at:
            message += f"\nДо {violation.expires_at.strftime('%d.%m.%Y %H:%M')}"

        message += "</blockquote>\n\n"

    if not violations:
        message += "<i>Нет нарушений</i>"

    return message


def get_audit_message(violation: entities.ChatViolationWithUserEntity) -> str:
    message = f"<b>{VIOLATIONS[violation.type]}</b>\n\n"
    message += f"Выдан: {format_user_handle(violation.applied_by_user.username, violation.applied_by_user.telegram_id)} (<code>{violation.applied_by_user.telegram_id}</code>)\n"
    message += f"В чате: <code>{violation.telegram_chat_id}</code>\n"
    message += f"Пользователь: {format_user_handle(violation.user.username, violation.user.telegram_id)} (<code>{violation.user.telegram_id}</code>)\n"
    message += f"От: {violation.created_at.strftime('%d.%m.%Y %H:%M')}"

    if violation.expires_at:
        message += f"\nДо: {violation.expires_at.strftime('%d.%m.%Y %H:%M')}"

    message += f"\n\n<blockquote>{escape(violation.reason)}</blockquote>"

    return message


def get_action_audit_message(
    action: types.ChatAction,
    user: entities.UserEntity,
    applied_by_user: entities.UserEntity,
    violation_id: Optional[int] = None,
) -> str:
    message = f"<b>{CHAT_ACTIONS[action]}</b>\n\n"
    message += f"Пользователь: {format_user_handle(user.username, user.telegram_id)} (<code>{user.telegram_id}</code>)\n"
    message += f"Выполнил: {format_user_handle(applied_by_user.username, applied_by_user.telegram_id)} (<code>{applied_by_user.telegram_id}</code>)\n"

    if violation_id:
        message += f"Нарушение: <code>{violation_id}</code>"

    return message


def get_moderators_message(moderators: List[entities.UserEntity]) -> str:
    message = "👮 <b>Модераторы</b>\n\n"
    for moderator in moderators:
        message += f"{format_user_handle(moderator.username, moderator.telegram_id)}\n"
    return message


def get_report_message(report: entities.ReportWithUserEntity) -> str:
    message = f"<b>{REPORT_TYPES[report.type]}</b>\n\n"
    message += f"Статус: <b>{REPORT_STATUSES[report.status]}</b>\n"
    message += f"Пользователь: {format_user_handle(report.user.username, report.user.telegram_id)} (<code>{report.user.telegram_id}</code>)\n"

    if report.accused_user:
        message += f"Обвиняемый: {format_user_handle(report.accused_user.username, report.accused_user.telegram_id)} (<code>{report.accused_user.telegram_id}</code>)\n"
    if report.applied_by_user:
        message += f"Изменил статус: {format_user_handle(report.applied_by_user.username, report.applied_by_user.telegram_id)} (<code>{report.applied_by_user.telegram_id}</code>)\n"

    message += f"Дата: {report.created_at.strftime('%d.%m.%Y %H:%M')}\n"

    if report.created_at != report.updated_at:
        message += f"Обновлено: {report.updated_at.strftime('%d.%m.%Y %H:%M')}\n"

    message += "\n<b>Причина:</b>\n"
    message += f"<blockquote>{escape(report.reason)}</blockquote>\n\n"

    if report.admin_comment:
        message += "<b>Комментарий:</b>\n"
        message += f"<blockquote>{escape(report.admin_comment)}</blockquote>\n\n"

    return message


def get_check_success_message(reputation: entities.ReputationUserWithUserEntity) -> str:
    message = f"<b>{REPUTATION_ROLES[reputation.role]}</b>\n\n"
    message += f"Пользователь: {format_user_handle(reputation.user.username, reputation.user.telegram_id)} (<code>{reputation.user.telegram_id}</code>)\n"
    message += f"От: {reputation.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    message += f"<blockquote>{escape(reputation.description)}</blockquote>\n"
    return message


def get_check_error_message(username: str) -> str:
    message = f"<b>👤 Пользователь</b>\n\n"
    message += f"<i>Пользователь <b>{escape(username)}</b> не имеет репутации.</i>"
    return message


def get_report_updated_message(report: entities.ReportWithUserEntity) -> str:
    message = f"#<code>{report.id}</code> <b>{REPORT_TYPES[report.type]}</b>\n\n"
    message += f"<blockquote>{escape(report.reason)}</blockquote>\n\n"
    message += f"<b>{REPORT_STATUSES[report.status]}</b>\n"

    if report.admin_comment:
        message += "<b>Ответ администратора</b>\n"
        message += f"<blockquote>{escape(report.admin_comment)}</blockquote>\n\n"

    return message


def get_violations_count_message(
    user: entities.UserEntity,
    violations_count: Dict[types.ViolationType, int],
    start_date: Optional[datetime],
) -> str:
    message = f"🔎 <b>Статистика нарушений {format_user_handle(user.username, user.telegram_id)}</b>\n\n"

    for violation_type, count in violations_count.items():
        message += f"<b>{VIOLATIONS[violation_type]}</b>: {count} шт.\n"

    if start_date:
        message += f"\nОт: {start_date.strftime('%d.%m.%Y %H:%M')}"
    
    return message
