from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ChatType
from typing import Optional
from aiogram import Router
from html import escape

from bot.data.keyboards import get_violations_keyboard
from domain.services import ModerationService, ConfigService
from bot.actions import UserActions, ModerationActions, AuditActions
from domain.objects import dtos, entities
from bot.filters import GroupsFilter, UsersFilter
from domain.objects.types import UserRole, ChatAction
from domain.services import UserService
from bot.data import text, callbacks


moderation_router = Router()


@moderation_router.message(
    GroupsFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
    Command("ban", "b", ignore_case=True),
    flags={
        "command_model": dtos.BanCommandDTO,
        "user_role": [UserRole.ADMIN, UserRole.MODERATOR],
    },
)
async def ban_handler(
    message: Message,
    command_data: dtos.BanCommandDTO,
    user: entities.UserEntity,
    user_actions: UserActions,
    moderation_actions: ModerationActions,
    audit_actions: AuditActions,
    reply_to_user: Optional[entities.UserEntity] = None,
):
    if command_data.username:
        purpose_user = await user_actions.get_telegram_user(
            command_data.username, message.chat.id
        )
    elif reply_to_user:
        purpose_user = reply_to_user
    else:
        return await message.answer(text.USERNAME_OR_REPLY_TO_USER_REQUIRED)

    dto = dtos.BanUserDTO(
        user_id=purpose_user.id,
        reason=command_data.reason,
        applied_by_user_id=user.id,
        telegram_chat_id=message.chat.id,
        expires_at=command_data.expires_at,
    )
    violation = await moderation_actions.ban_user(dto)
    await audit_actions.upload_audit(violation.id, message.reply_to_message)
    await message.answer(
        text.get_ban_user_success_message(
            text.format_user_handle(purpose_user.username, purpose_user.telegram_id),
            command_data.expires_at,
            escape(command_data.reason),
        )
    )


@moderation_router.message(
    GroupsFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
    Command("globalban", "gb", ignore_case=True),
    flags={
        "command_model": dtos.BanCommandDTO,
        "user_role": [UserRole.ADMIN, UserRole.MODERATOR],
    },
)
async def globalban_handler(
    message: Message,
    command_data: dtos.BanCommandDTO,
    user: entities.UserEntity,
    user_actions: UserActions,
    moderation_actions: ModerationActions,
    audit_actions: AuditActions,
):
    if command_data.username:
        purpose_user = await user_actions.get_telegram_user(
            command_data.username, message.chat.id
        )
    else:
        return await message.answer(text.USERNAME_OR_REPLY_TO_USER_REQUIRED)

    dto = dtos.GlobalBanUserDTO(
        user_id=purpose_user.id,
        reason=command_data.reason,
        applied_by_user_id=user.id,
        expires_at=command_data.expires_at,
    )
    violation = await moderation_actions.global_ban_user(dto)
    await audit_actions.upload_audit(violation.id, message.reply_to_message)
    await message.answer(
        text.get_ban_user_success_message(
            text.format_user_handle(purpose_user.username, purpose_user.telegram_id),
            command_data.expires_at,
            escape(command_data.reason),
        )
    )


@moderation_router.message(
    GroupsFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
    Command("preventivelyban", "pb", ignore_case=True),
    flags={
        "command_model": dtos.PreventivelyBanCommandDTO,
        "user_role": [UserRole.ADMIN, UserRole.MODERATOR],
    },
)
async def preventivelyban_handler(
    message: Message,
    command_data: dtos.PreventivelyBanCommandDTO,
    user: entities.UserEntity,
    moderation_actions: ModerationActions,
    audit_actions: AuditActions,
):
    dto = dtos.GlobalBanUserDTO(
        user_id=command_data.id,
        reason=command_data.reason,
        applied_by_user_id=user.id,
        expires_at=command_data.expires_at,
    )
    violation = await moderation_actions.preventively_ban_user(dto)
    await audit_actions.upload_audit(violation.id)
    await message.answer(
        text.get_ban_user_success_message(
            str(command_data.id),
            command_data.expires_at,
            escape(command_data.reason),
        )
    )


@moderation_router.message(
    GroupsFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
    Command("unban", "ub", ignore_case=True),
    flags={
        "user_role": [UserRole.ADMIN, UserRole.MODERATOR],
        "command_model": dtos.UnbanCommandDTO,
    },
)
async def unban_handler(
    message: Message,
    command_data: dtos.UnbanCommandDTO,
    user: entities.UserEntity,
    user_actions: UserActions,
    moderation_actions: ModerationActions,
    audit_actions: AuditActions,
    reply_to_user: Optional[entities.UserEntity] = None,
):
    if command_data.username:
        purpose_user = await user_actions.get_telegram_user(
            command_data.username, message.chat.id
        )
    elif reply_to_user:
        purpose_user = reply_to_user
    else:
        return await message.answer(text.USERNAME_OR_REPLY_TO_USER_REQUIRED)

    await moderation_actions.unban_user(purpose_user.id, message.chat.id)
    await audit_actions.upload_action_audit(ChatAction.UNBAN, purpose_user, user)
    await message.answer(
        text.UNBAN_USER_SUCCESS.format(
            text.format_user_handle(purpose_user.username, purpose_user.telegram_id)
        )
    )


@moderation_router.message(
    GroupsFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
    Command("mute", "m", ignore_case=True),
    flags={
        "user_role": [UserRole.ADMIN, UserRole.MODERATOR],
        "command_model": dtos.MuteCommandDTO,
    },
)
async def mute_handler(
    message: Message,
    command_data: dtos.MuteCommandDTO,
    user: entities.UserEntity,
    user_actions: UserActions,
    moderation_actions: ModerationActions,
    audit_actions: AuditActions,
    reply_to_user: Optional[entities.UserEntity] = None,
):
    if command_data.username:
        purpose_user = await user_actions.get_telegram_user(
            command_data.username, message.chat.id
        )
    elif reply_to_user:
        purpose_user = reply_to_user
    else:
        return await message.answer(text.USERNAME_OR_REPLY_TO_USER_REQUIRED)

    dto = dtos.MuteUserDTO(
        user_id=purpose_user.id,
        reason=command_data.reason,
        applied_by_user_id=user.id,
        telegram_chat_id=message.chat.id,
        expires_at=command_data.expires_at,
    )
    violation = await moderation_actions.mute_user(dto)
    await audit_actions.upload_audit(violation.id, message.reply_to_message)
    await message.answer(
        text.get_mute_user_success_message(
            text.format_user_handle(purpose_user.username, purpose_user.telegram_id),
            command_data.expires_at,
            escape(command_data.reason),
        )
    )


@moderation_router.message(
    GroupsFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
    Command("unmute", "um", ignore_case=True),
    flags={
        "user_role": [UserRole.ADMIN, UserRole.MODERATOR],
        "command_model": dtos.UnmuteCommandDTO,
    },
)
async def unmute_handler(
    message: Message,
    command_data: dtos.UnmuteCommandDTO,
    user_actions: UserActions,
    moderation_actions: ModerationActions,
    user: entities.UserEntity,
    audit_actions: AuditActions,
    reply_to_user: Optional[entities.UserEntity] = None,
):
    if command_data.username:
        purpose_user = await user_actions.get_telegram_user(
            command_data.username, message.chat.id
        )
    elif reply_to_user:
        purpose_user = reply_to_user
    else:
        return await message.answer(text.USERNAME_OR_REPLY_TO_USER_REQUIRED)

    await moderation_actions.unmute_user(purpose_user.id, message.chat.id)
    await audit_actions.upload_action_audit(ChatAction.UNMUTE, purpose_user, user)
    await message.answer(
        text.UNMUTE_USER_SUCCESS.format(
            text.format_user_handle(purpose_user.username, purpose_user.telegram_id)
        )
    )


@moderation_router.message(
    GroupsFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
    Command("warn", "w", ignore_case=True),
    flags={
        "user_role": [UserRole.ADMIN, UserRole.MODERATOR],
        "command_model": dtos.WarnCommandDTO,
    },
)
async def warn_handler(
    message: Message,
    command_data: dtos.WarnCommandDTO,
    user: entities.UserEntity,
    user_actions: UserActions,
    moderation_service: ModerationService,
    audit_actions: AuditActions,
    reply_to_user: Optional[entities.UserEntity] = None,
):
    if command_data.username:
        purpose_user = await user_actions.get_telegram_user(
            command_data.username, message.chat.id
        )
    elif reply_to_user:
        purpose_user = reply_to_user
    else:
        return await message.answer(text.USERNAME_OR_REPLY_TO_USER_REQUIRED)

    dto = dtos.WarnUserDTO(
        user_id=purpose_user.id,
        reason=command_data.reason,
        applied_by_user_id=user.id,
        telegram_chat_id=message.chat.id,
        expires_at=command_data.expires_at,
    )
    violation = await moderation_service.warn_user(dto)
    await audit_actions.upload_audit(violation.id, message.reply_to_message)
    await message.answer(
        text.get_warn_user_success_message(
            text.format_user_handle(purpose_user.username, purpose_user.telegram_id),
            command_data.expires_at,
            escape(command_data.reason),
        )
    )


@moderation_router.message(
    GroupsFilter([ChatType.GROUP, ChatType.SUPERGROUP]),
    Command("unwarn", "uw", ignore_case=True),
    flags={
        "user_role": [UserRole.ADMIN, UserRole.MODERATOR],
        "command_model": dtos.UnwarnCommandDTO,
    },
)
async def unwarn_handler(
    message: Message,
    command_data: dtos.UnwarnCommandDTO,
    moderation_service: ModerationService,
    audit_actions: AuditActions,
):
    await moderation_service.unwarn_user(command_data.id)
    violation = await moderation_service.get_violation(command_data.id)
    await audit_actions.upload_action_audit(
        ChatAction.UNWARN, violation.user, violation.applied_by_user, command_data.id
    )
    await message.answer(text.UNWARN_USER_SUCCESS)


@moderation_router.message(
    Command("violations", "v", ignore_case=True),
    flags={
        "command_model": dtos.ViolationsCommandDTO,
    },
)
async def violations_handler(
    message: Message,
    command_data: dtos.ViolationsCommandDTO,
    user: entities.UserEntity,
    user_actions: UserActions,
    moderation_service: ModerationService,
):
    if command_data.username:
        if user.role == UserRole.USER:
            return await message.answer(text.VIOLATIONS_OTHER_USER_FORBIDDEN)

        purpose_user = await user_actions.get_telegram_user(
            command_data.username, message.chat.id
        )
    else:
        purpose_user = user

    dto = dtos.GetViolationsDTO(
        user_id=purpose_user.id,
        limit=6,
        offset=0,
    )
    violations = await moderation_service.get_violations(dto)
    has_more = len(violations) == dto.limit
    await message.answer(
        text.get_violations_message(violations),
        reply_markup=get_violations_keyboard(
            0, dto.limit - 1, purpose_user.id, has_more
        ),
    )


@moderation_router.callback_query(
    callbacks.ViolationsCallback.filter(),
    UsersFilter([UserRole.ADMIN, UserRole.MODERATOR]),
)
async def violations_callback(
    callback: CallbackQuery,
    callback_data: callbacks.ViolationsCallback,
    moderation_service: ModerationService,
):
    dto = dtos.GetViolationsDTO(
        user_id=callback_data.user_id,
        limit=6,
        offset=callback_data.offset,
    )
    violations = await moderation_service.get_violations(dto)
    has_more = len(violations) == dto.limit
    await callback.message.edit_text(
        text.get_violations_message(violations),
        reply_markup=get_violations_keyboard(
            callback_data.offset, dto.limit - 1, callback_data.user_id, has_more
        ),
    )


@moderation_router.message(
    Command("getid", "gid", ignore_case=True),
)
async def getid_handler(
    message: Message,
):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.answer(text.GET_MY_ID_SUCCESS.format(message.from_user.id))

    await message.answer(
        text.GET_USER_ID_SUCCESS.format(
            text.format_user_handle(
                message.reply_to_message.from_user.username,
                message.reply_to_message.from_user.id,
            )
        )
    )


@moderation_router.message(
    Command("addmoderator", "am", ignore_case=True),
    flags={
        "user_role": [UserRole.ADMIN],
        "command_model": dtos.AddModeratorCommandDTO,
    },
)
async def addmoderator_handler(
    message: Message,
    command_data: dtos.AddModeratorCommandDTO,
    user_actions: UserActions,
    user_service: UserService,
):
    user = await user_actions.get_telegram_user(command_data.username, message.chat.id)
    await user_service.update_role(user.id, UserRole.MODERATOR)
    await message.answer(
        text.ADD_MODERATOR_SUCCESS.format(
            text.format_user_handle(user.username, user.telegram_id)
        )
    )


@moderation_router.message(
    Command("removemoderator", "rm", ignore_case=True),
    flags={
        "user_role": [UserRole.ADMIN],
        "command_model": dtos.RemoveModeratorCommandDTO,
    },
)
async def removemoderator_handler(
    message: Message,
    command_data: dtos.RemoveModeratorCommandDTO,
    user_service: UserService,
    user_actions: UserActions,
):
    user = await user_actions.get_telegram_user(command_data.username, message.chat.id)
    await user_service.update_role(user.id, UserRole.USER)
    await message.answer(
        text.REMOVE_MODERATOR_SUCCESS.format(
            text.format_user_handle(user.username, user.telegram_id)
        )
    )


@moderation_router.message(Command("rules", "r", ignore_case=True))
async def rules_handler(
    message: Message,
    config_service: ConfigService,
):
    rules = await config_service.get("rules", "Правила не установлены")
    await message.answer(rules)


@moderation_router.message(Command("moderators", "mod", ignore_case=True))
async def moderators_handler(
    message: Message,
    user_service: UserService,
):
    moderators = await user_service.get_by_role(UserRole.MODERATOR)
    await message.answer(text.get_moderators_message(moderators))
