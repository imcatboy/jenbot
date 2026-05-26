from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatMemberUpdated
from aiogram import Router, F

from domain.services import UserService
from domain.objects.types import ChatEvent
from bot.actions import AuditActions


event_router = Router()


@event_router.chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER),
    F.new_chat_member.user.is_bot == False,
)
async def user_join_handler(
    event: ChatMemberUpdated,
    user_service: UserService,
    audit_actions: AuditActions,
) -> None:
    user_data = event.new_chat_member.user
    chat_id = event.chat.id
    user = await user_service.get_or_create(
        telegram_id=user_data.id,
        username=user_data.username,
    )
    await audit_actions.upload_event_audit(ChatEvent.JOIN, user, chat_id)


@event_router.chat_member(
    ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER),
    F.old_chat_member.user.is_bot == False,
)
async def user_leave_handler(
    event: ChatMemberUpdated,
    user_service: UserService,
    audit_actions: AuditActions,
) -> None:
    user_data = event.old_chat_member.user
    chat_id = event.chat.id
    user = await user_service.get_or_create(
        telegram_id=user_data.id,
        username=user_data.username,
    )
    await audit_actions.upload_event_audit(ChatEvent.LEAVE, user, chat_id)
