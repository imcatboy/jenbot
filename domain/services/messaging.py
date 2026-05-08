from typing import List

from domain.repositories import MessagingRepository, MediaRepository
from domain.objects import entities, dtos, exceptions


class MessagingService:

    def __init__(
        self,
        messaging_repository: MessagingRepository,
        media_repository: MediaRepository,
    ) -> None:
        self.messaging_repository = messaging_repository
        self.media_repository = media_repository

    async def create_chat(self, dto: dtos.CreateChatDTO) -> entities.ChatEntity:
        return await self.messaging_repository.create_chat(dto)

    async def create_message(
        self, dto: dtos.CreateMessageDTO
    ) -> entities.MessageEntity:
        if not await self.is_chat_participant(dto.chat_id, dto.user_id):
            raise exceptions.ChatParticipantNotFoundException(dto.chat_id, dto.user_id)

        if not await self.media_repository.is_user_unlinked_files(
            dto.user_id, dto.file_ids
        ):
            raise exceptions.FileNotFoundException(*dto.file_ids)

        return await self.messaging_repository.create_message(dto)

    async def get_chats(self, dto: dtos.GetChatsDTO) -> List[entities.ChatEntity]:
        return await self.messaging_repository.get_chats(dto)

    async def get_messages(
        self, dto: dtos.GetMessagesDTO
    ) -> List[entities.MessageEntity]:
        if not await self.is_chat_participant(dto.chat_id, dto.user_id):
            raise exceptions.ChatParticipantNotFoundException(dto.chat_id, dto.user_id)

        return await self.messaging_repository.get_messages(dto)

    async def is_chat_participant(self, chat_id: int, user_id: int) -> bool:
        return await self.messaging_repository.is_chat_participant(chat_id, user_id)

    async def get_chat_participants(
        self, chat_id: int
    ) -> List[entities.ChatParticipantEntity]:
        return await self.messaging_repository.get_chat_participants(chat_id)

    async def read_chat(self, chat_id: int, user_id: int, message_id: int) -> None:
        participant = await self.messaging_repository.get_chat_participant(
            chat_id, user_id
        )

        if (
            participant.last_read_message_id
            and participant.last_read_message_id >= message_id
        ):
            raise exceptions.InvalidDataException(
                message_id=message_id,
                last_read_message_id=participant.last_read_message_id,
            )

        return await self.messaging_repository.read_chat(chat_id, user_id, message_id)

    async def is_message_participant(self, message_id: int, user_id: int) -> bool:
        return await self.messaging_repository.is_message_participant(
            message_id, user_id
        )

    async def get_attachment(
        self, user_id: int, message_id: int, file_id: int
    ) -> entities.FileEntity:
        if not await self.is_message_participant(message_id, user_id):
            raise exceptions.FileNotFoundException(file_id)

        return await self.media_repository.get_message_file(message_id, file_id)
