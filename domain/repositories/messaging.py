from typing import List
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.objects import models, dtos, entities
from .base import BaseRepository


class MessagingRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_chat(self, dto: dtos.CreateChatDTO) -> entities.ChatEntity:
        chat = models.ChatModel(
            name=dto.name,
        )
        await self.validator.validate_ids_exist(models.UserModel, dto.participant_ids)
        await self.create_relation(chat, models.UserModel, dto.author_id, "author_id")
        await self.create_relation(chat, models.DealModel, dto.deal_id)

        for participant_id in dto.participant_ids:
            participant = models.ChatParticipantModel(
                user_id=participant_id,
            )
            chat.participants.append(participant)

        self.session.add(chat)
        await self.session.flush()
        return entities.ChatEntity.model_validate(chat)

    async def create_message(
        self, dto: dtos.CreateMessageDTO
    ) -> entities.MessageEntity:
        message = models.MessageModel(
            body=dto.body,
        )
        await self.create_relation(message, models.UserModel, dto.user_id)
        await self.create_relation(message, models.ChatModel, dto.chat_id)
        self.session.add(message)
        await self.session.flush()
        await self.create_many_to_one_relation(message, models.FileModel, dto.file_ids)
        return entities.MessageEntity.model_validate(message)

    async def get_chats(self, dto: dtos.GetChatsDTO) -> List[entities.ChatEntity]:
        last_message_subquery = (
            select(
                models.MessageModel.chat_id,
                func.max(models.MessageModel.created_at).label("last_message_at"),
            )
            .group_by(models.MessageModel.chat_id)
            .subquery()
        )
        query = (
            select(models.ChatModel)
            .join(
                models.ChatParticipantModel,
                models.ChatParticipantModel.chat_id == models.ChatModel.id,
            )
            .outerjoin(
                last_message_subquery,
                last_message_subquery.c.chat_id == models.ChatModel.id,
            )
            .filter(models.ChatParticipantModel.user_id == dto.user_id)
            .order_by(
                last_message_subquery.c.last_message_at.desc().nulls_last(),
                models.ChatModel.created_at.desc(),
            )
            .limit(dto.limit)
            .offset(dto.offset)
        )

        if dto.search:
            query = query.filter(models.ChatModel.name.ilike(f"%{dto.search}%"))

        chats = await self.session.execute(query)
        return [
            entities.ChatEntity.model_validate(chat) for chat in chats.scalars().all()
        ]

    async def get_messages(
        self, dto: dtos.GetMessagesDTO
    ) -> List[entities.MessageEntity]:
        query = (
            select(models.MessageModel)
            .where(models.MessageModel.chat_id == dto.chat_id)
            .limit(dto.limit)
            .offset(dto.offset)
            .order_by(models.MessageModel.created_at.desc())
        )

        if dto.search:
            query = query.filter(models.MessageModel.body.ilike(f"%{dto.search}%"))

        messages = await self.session.execute(query)
        return [
            entities.MessageEntity.model_validate(message)
            for message in messages.scalars().all()
        ]

    async def is_chat_participant(self, chat_id: int, user_id: int) -> bool:
        query = (
            select(models.ChatParticipantModel.id)
            .where(
                and_(
                    models.ChatParticipantModel.chat_id == chat_id,
                    models.ChatParticipantModel.user_id == user_id,
                )
            )
            .exists()
            .select()
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def is_message_participant(self, message_id: int, user_id: int) -> bool:
        query = (
            select(models.MessageModel.id)
            .join(
                models.ChatParticipantModel,
                models.ChatParticipantModel.chat_id == models.MessageModel.chat_id,
            )
            .where(
                and_(
                    models.MessageModel.id == message_id,
                    models.ChatParticipantModel.user_id == user_id,
                ),
            )
            .exists()
            .select()
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_chat_participants(
        self, chat_id: int
    ) -> List[entities.ChatParticipantEntity]:
        query = select(models.ChatParticipantModel).where(
            models.ChatParticipantModel.chat_id == chat_id,
        )
        participants = await self.session.execute(query)
        return [
            entities.ChatParticipantEntity.model_validate(participant)
            for participant in participants.scalars().all()
        ]

    async def read_chat(self, chat_id: int, user_id: int, message_id: int) -> None:
        participant = await self.get_one_by_data(
            models.ChatParticipantModel,
            chat_id=chat_id,
            user_id=user_id,
        )
        await self.update_relation(
            participant,
            models.MessageModel,
            message_id,
            "last_read_message_id",
        )

    async def get_chat_participant(
        self, chat_id: int, user_id: int
    ) -> entities.ChatParticipantEntity:
        participant = await self.get_one_by_data(
            models.ChatParticipantModel,
            chat_id=chat_id,
            user_id=user_id,
        )
        return entities.ChatParticipantEntity.model_validate(participant)
