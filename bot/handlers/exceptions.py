import logging

from aiogram.types import ErrorEvent, Message
from aiogram import Router
from html import escape

from domain.objects import exceptions
from bot.data import text


logger = logging.getLogger(__name__)
exception_router = Router()


@exception_router.errors()
async def exception_handler(event: ErrorEvent):
    message: Message | None = None

    if event.update.message:
        message = event.update.message
    elif event.update.callback_query:
        message = event.update.callback_query.message

    match event.exception:
        case exceptions.UserNotFoundException():
            await message.answer(
                text.USER_NOT_FOUND.format(escape(event.exception.username))
            )
        case exceptions.UserNotAllowedToActionException():
            await message.answer(text.USER_NOT_ALLOWED_TO_ACTION)
        case exceptions.ObjectNotFoundException():
            await message.answer(text.OBJECT_NOT_FOUND)
        case exceptions.ObjectAlreadyExistsException():
            await message.answer(text.OBJECT_ALREADY_EXISTS)
        case exceptions.ModerationException():
            await message.answer(text.CANNOT_USE_ACTION_ON_MODERATOR)

    logger.exception(
        f"Unhandled exception: {event.exception}", exc_info=event.exception
    )
    return True
