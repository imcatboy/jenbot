import logging

from aiogram.types import ErrorEvent, Message
from aiogram import Router

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
            await message.answer(text.USER_NOT_FOUND.format(event.exception.username))
            return True
        case exceptions.UserNotAllowedToActionException():
            await message.answer(text.USER_NOT_ALLOWED_TO_ACTION)
            return True
        case exceptions.ObjectNotFoundException():
            await message.answer(text.OBJECT_NOT_FOUND)
            return True
        case exceptions.ObjectAlreadyExistsException():
            await message.answer(text.OBJECT_ALREADY_EXISTS)
            return True
        case exceptions.ModerationException():
            await message.answer(text.CANNOT_USE_ACTION_ON_USER)
            return True
        case exceptions.ChatNotFoundException():
            await message.answer(text.CHAT_NOT_FOUND)
            return True
        case exceptions.UserIsScammerException():
            await message.answer(text.USER_IS_SCAMMER)
            return True
        case exceptions.UserIsNotGuarantorException():
            await message.answer(text.USER_IS_NOT_GUARANTOR)
            return True
        case exceptions.NotEnoughAmountException():
            await message.answer(text.NOT_ENOUGH_AMOUNT)
            return True
        case exceptions.DealNotDraftException():
            await message.answer(text.DEAL_NOT_DRAFT)
            return True

    logger.exception(
        f"Unhandled exception: {event.exception}", exc_info=event.exception
    )
    await message.answer(text.UNKNOWN_ERROR)
    return True
