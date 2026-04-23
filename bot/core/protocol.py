from aiogram.client.default import Default
from typing import Protocol, Union, Optional
from datetime import datetime, timedelta
from aiogram.types import *


class BotProtocol(Protocol):

    async def ban_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: int,
        until_date: Optional[Union[datetime, timedelta, int]] = None,
        revoke_messages: Optional[bool] = None,
        request_timeout: Optional[int] = None,
    ) -> bool: ...

    async def unban_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: int,
        only_if_banned: Optional[bool] = None,
        request_timeout: Optional[int] = None,
    ) -> bool: ...

    async def restrict_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: int,
        permissions: ChatPermissions,
        use_independent_chat_permissions: Optional[bool] = None,
        until_date: Optional[Union[datetime, timedelta, int]] = None,
        request_timeout: Optional[int] = None,
    ) -> bool: ...

    async def get_chat(
        self,
        chat_id: Union[int, str],
        request_timeout: Optional[int] = None,
    ) -> ChatFullInfo: ...

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        parse_mode: Optional[Union[str, Default]] = Default("parse_mode"),
        entities: Optional[list[MessageEntity]] = None,
        link_preview_options: Optional[Union[LinkPreviewOptions, Default]] = Default(
            "link_preview"
        ),
        disable_notification: Optional[bool] = None,
        protect_content: Optional[Union[bool, Default]] = Default("protect_content"),
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        reply_parameters: Optional[ReplyParameters] = None,
        reply_markup: Optional[
            Union[
                InlineKeyboardMarkup,
                ReplyKeyboardMarkup,
                ReplyKeyboardRemove,
                ForceReply,
            ]
        ] = None,
        allow_sending_without_reply: Optional[bool] = None,
        disable_web_page_preview: Optional[Union[bool, Default]] = Default(
            "link_preview_is_disabled"
        ),
        reply_to_message_id: Optional[int] = None,
        request_timeout: Optional[int] = None,
    ) -> Message: ...

    async def get_file(
        self,
        file_id: str,
        request_timeout: Optional[int] = None,
    ) -> File: ...

    async def send_media_group(
        self,
        chat_id: Union[int, str],
        media: list[
            Union[InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo]
        ],
        business_connection_id: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[Union[bool, Default]] = Default("protect_content"),
        allow_paid_broadcast: Optional[bool] = None,
        message_effect_id: Optional[str] = None,
        reply_parameters: Optional[ReplyParameters] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        request_timeout: Optional[int] = None,
    ) -> list[Message]: ...
