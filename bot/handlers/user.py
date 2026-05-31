from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram import Router, Bot

from domain.services import UserService, ModerationService
from domain.objects.types import ReportStatus, ReportType
from bot.actions import UserActions, MediaActions
from bot.data import text, keyboards, callbacks
from domain.objects import dtos, exceptions


user_router = Router()


@user_router.message(Command("check"), flags={"command_model": dtos.CheckCommandDTO})
async def check_handler(
    message: Message,
    command_data: dtos.CheckCommandDTO,
    user_actions: UserActions,
    media_actions: MediaActions,
    user_service: UserService,
    moderation_service: ModerationService,
):
    try:
        user = await user_actions.get_telegram_user(command_data.username)
        reputation = await user_service.get_user_reputation(user.id)
        reports = await moderation_service.get_reports(
            dtos.GetReportsDTO(
                accused_user_id=user.id,
                status=ReportStatus.APPROVED,
                type=ReportType.SCAM,
            )
        )
    except (exceptions.UserNotFoundException, exceptions.ObjectNotFoundException):
        image = await media_actions.get_telegram_file("user")
        await message.answer_photo(
            image, text.get_check_error_message(str(command_data.username))
        )
        return

    image = await media_actions.get_telegram_file(reputation.role.value)
    await message.answer_photo(
        image,
        text.get_check_success_message(reputation),
        reply_markup=keyboards.get_check_keyboard(reports),
    )


@user_router.callback_query(callbacks.CheckCallback.filter())
async def check_callback_handler(
    callback: CallbackQuery,
    callback_data: callbacks.CheckCallback,
    moderation_service: ModerationService,
    bot: Bot,
):
    report = await moderation_service.get_user_report(
        dtos.GetUserReportDTO(
            report_id=callback_data.report_id,
            status=ReportStatus.APPROVED,
            type=ReportType.SCAM,
        )
    )

    if report.attachments:
        attachments = []
        has_caption = False

        for attachment in report.attachments:
            try:
                file = await bot.get_file(attachment)

                if "photo" in file.file_path:
                    attachments.append(
                        InputMediaPhoto(
                            media=file.file_id,
                            caption=report.reason if not has_caption else None,
                        )
                    )
                elif "video" in file.file_path:
                    attachments.append(
                        InputMediaVideo(
                            media=file.file_id,
                            caption=report.reason if not has_caption else None,
                        )
                    )

                has_caption = True
            except TelegramAPIError:
                continue

        if attachments:
            await callback.message.answer_media_group(attachments)
            return

    await callback.message.answer(report.reason)
