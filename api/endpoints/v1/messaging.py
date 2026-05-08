from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from typing import List, Optional

from domain.objects import schemas, entities, dtos
from domain.services import MessagingService
from domain.objects.types import Limit, Offset, ID
from api.dependencies.uow import get_messaging_service
from api.dependencies import get_message_file
from api.dependencies.auth import get_current_user
from api.core.openapi import ENDPOINTS_METADATA
from api.core.container import AppContainer
from api.core.settings import Settings


messaging_router = APIRouter(prefix="/chats", tags=["Messaging"])


@messaging_router.get(
    "/", **ENDPOINTS_METADATA["get_chats"], response_model=List[schemas.ChatResponse]
)
async def get_chats(
    limit: Limit = Query(10, ge=1, le=20, description="Limit of chats to return"),
    offset: Offset = Query(0, ge=0, description="Offset of chats to return"),
    search: Optional[str] = Query(
        None, min_length=3, max_length=100, description="Search for chat name"
    ),
    messaging_service: MessagingService = Depends(get_messaging_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> List[schemas.ChatResponse]:
    dto = dtos.GetChatsDTO(
        user_id=user.id,
        limit=limit,
        offset=offset,
        search=search,
    )
    return await messaging_service.get_chats(dto)


@messaging_router.get(
    "/{chat_id}/messages",
    **ENDPOINTS_METADATA["get_messages"],
    response_model=List[schemas.MessageResponse],
)
async def get_messages(
    chat_id: ID,
    limit: Limit = Query(10, ge=1, le=20, description="Limit of messages to return"),
    offset: Offset = Query(0, ge=0, description="Offset of messages to return"),
    search: Optional[str] = Query(
        None, min_length=3, max_length=100, description="Search for message body"
    ),
    messaging_service: MessagingService = Depends(get_messaging_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> List[schemas.MessageResponse]:
    dto = dtos.GetMessagesDTO(
        user_id=user.id,
        chat_id=chat_id,
        limit=limit,
        offset=offset,
        search=search,
    )
    return await messaging_service.get_messages(dto)


@messaging_router.post(
    "/{chat_id}/messages",
    **ENDPOINTS_METADATA["create_message"],
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    chat_id: ID,
    data: schemas.CreateMessageRequest,
    messaging_service: MessagingService = Depends(get_messaging_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> schemas.MessageResponse:
    dto = dtos.CreateMessageDTO(
        user_id=user.id,
        chat_id=chat_id,
        **data.model_dump(),
    )
    return await messaging_service.create_message(dto)


@messaging_router.patch(
    "/{chat_id}/messages/{message_id}/read",
    **ENDPOINTS_METADATA["read_messages"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def read_chat(
    chat_id: ID,
    message_id: ID,
    messaging_service: MessagingService = Depends(get_messaging_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> None:
    return await messaging_service.read_chat(chat_id, user.id, message_id)


@messaging_router.post(
    "/attachments",
    **ENDPOINTS_METADATA["upload_message_attachment"],
    response_model=schemas.MediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_message_attachment(
    file: entities.FileEntity = Depends(get_message_file),
) -> schemas.MediaResponse:
    return file


@messaging_router.get(
    "/{message_id}/attachments/{file_id}",
    **ENDPOINTS_METADATA["get_message_attachment"],
    response_class=FileResponse,
)
@inject
async def get_message_attachment(
    message_id: ID,
    file_id: ID,
    messaging_service: MessagingService = Depends(get_messaging_service),
    user: entities.UserEntity = Depends(get_current_user),
    settings: Settings = Depends(Provide[AppContainer.settings]),
) -> FileResponse:
    file = await messaging_service.get_attachment(user.id, message_id, file_id)
    return FileResponse(
        path=settings.MESSAGE_FILE_STORAGE_PATH + "/" + f"{file.name}.{file.extension}"
    )
