from pydantic import BaseModel, ValidationError, TypeAdapter
from aiogram.dispatcher.event.handler import HandlerObject
from typing import Any, Callable, Dict, Awaitable, Type
from aiogram.filters import CommandObject
from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.data import text


class CommandValidationMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        command: CommandObject | None = data.get("command")
        handler_object: HandlerObject | None = data.get("handler")

        if not handler_object or not command:
            return await handler(event, data)

        model: Type[BaseModel] | None = handler_object.flags.get("command_model")

        if not model:
            return await handler(event, data)

        raw_args = command.args.strip() if command.args else ""
        current_args_list = raw_args.split()

        fields = list(model.model_fields.items())
        payload = {}
        arg_index = 0

        for i, (name, field_info) in enumerate(fields):
            is_last = i == len(fields) - 1

            if is_last:
                remaining_text = " ".join(current_args_list[arg_index:])

                if remaining_text:
                    payload[name] = remaining_text
                elif field_info.is_required():
                    return await event.answer(
                        text.COMMAND_ARGUMENTS_ERROR.format(
                            text.get_command_usage(command, model)
                        )
                    )

                break

            if arg_index >= len(current_args_list):
                if field_info.is_required():
                    return await event.answer(
                        text.COMMAND_ARGUMENTS_ERROR.format(
                            text.get_command_usage(command, model)
                        )
                    )

                continue

            current_val = current_args_list[arg_index]

            if not field_info.is_required():
                try:
                    TypeAdapter(field_info.annotation).validate_python(current_val)
                    payload[name] = current_val
                    arg_index += 1
                except ValidationError:
                    continue
            else:
                payload[name] = current_val
                arg_index += 1

        try:
            validated_data = model.model_validate(payload)
            data["command_data"] = validated_data
        except ValidationError:
            return await event.answer(
                text.COMMAND_ARGUMENTS_VALIDATION_ERROR.format(
                    text.get_command_usage(command, model)
                )
            )

        return await handler(event, data)
