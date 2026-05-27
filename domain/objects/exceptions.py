from typing import Any, List, Optional

from domain.objects.types import ViolationType


class DomainException(Exception): ...


class ObjectNotFoundException(DomainException):

    def __init__(
        self, object_name: str, object_ids: Optional[List[int]] = None, **data: Any
    ):
        self.object_name = object_name
        self.object_ids = object_ids
        self.data = data

        if data:
            super().__init__(
                f"{object_name} with data {', '.join([f'{key}: {value}' for key, value in data.items()])} not found"
            )
        elif object_ids:
            super().__init__(
                f"{object_name} with ID {', '.join(map(str, object_ids))} not found"
            )
        else:
            super().__init__(f"{object_name} not found")


class ObjectAlreadyExistsException(DomainException):

    def __init__(self, object_name: str, **data: Any):
        self.object_name = object_name
        self.data = data
        super().__init__(
            f"{object_name} with data {', '.join([f'{key}: {value}' for key, value in data.items()])} already exists"
        )


class TooManyObjectsFoundException(DomainException):

    def __init__(self, object_name: str, **data: Any):
        self.object_name = object_name
        self.data = data
        super().__init__(
            f"{object_name} with data {', '.join([f'{key}: {value}' for key, value in data.items()])} has too many objects found"
        )


class ModerationException(DomainException):

    def __init__(self, user_id: int, violation_type: ViolationType):
        self.user_id = user_id
        self.violation_type = violation_type
        super().__init__(
            f"Bot cannot {violation_type.value.capitalize()} user {user_id}"
        )


class UserNotAllowedToActionException(DomainException):

    def __init__(self, user_id: int, telegram_chat_id: int, action: str):
        self.user_id = user_id
        self.telegram_chat_id = telegram_chat_id
        self.action = action
        super().__init__(
            f"User {user_id} is not allowed to {action} in chat {telegram_chat_id}"
        )


class UserNotFoundException(DomainException):

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User {username} not found")


class DuplicateIdsException(DomainException):

    def __init__(self, object_name: str, object_ids: List[int]):
        self.object_name = object_name
        self.object_ids = object_ids
        super().__init__(
            f"{object_name} with IDs {', '.join(map(str, object_ids))} has duplicate IDs"
        )


class MissingOptionException(DomainException):

    def __init__(self, product_id: int, option_ids: List[int]):
        self.product_id = product_id
        self.option_ids = option_ids
        super().__init__(
            f"Product {product_id} is missing options {', '.join(map(str, option_ids))}"
        )


class InvalidOptionRelationException(DomainException):

    def __init__(self, product_id: int, option_ids: List[int]):
        self.product_id = product_id
        self.option_ids = option_ids
        super().__init__(
            f"Product {product_id} has invalid option relation {', '.join(map(str, option_ids))}"
        )


class NotEnoughInventoryException(DomainException):

    def __init__(self, advertisement_option_id: int, count: int):
        self.advertisement_option_id = advertisement_option_id
        self.count = count
        super().__init__(
            f"Advertisement option {advertisement_option_id} has not enough inventory {count}"
        )


class InvalidDataException(DomainException):

    def __init__(self, **data: Any):
        self.data = data
        super().__init__(
            f"Invalid data {', '.join([f'{key}: {value}' for key, value in data.items()])}"
        )


class DealNotPendingException(DomainException):

    def __init__(self, deal_id: int):
        self.deal_id = deal_id
        super().__init__(f"Deal {deal_id} is not pending")


class DealSelfPurchaseException(DomainException):

    def __init__(self, advertisement_option_id: int):
        self.advertisement_option_id = advertisement_option_id
        super().__init__(
            f"User cannot purchase their own advertisement option {advertisement_option_id}"
        )


class ChatParticipantNotFoundException(DomainException):

    def __init__(self, chat_id: int, user_id: int):
        self.chat_id = chat_id
        self.user_id = user_id
        super().__init__(f"Chat participant {user_id} not found in chat {chat_id}")


class FileNotFoundException(DomainException):

    def __init__(self, *file_ids: int):
        self.file_ids = file_ids
        super().__init__(f"File {', '.join(map(str, file_ids))} not found")


class ChatNotFoundException(DomainException):

    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        super().__init__(f"Chat {chat_id} not found")
