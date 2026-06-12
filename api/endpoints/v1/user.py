from fastapi import APIRouter, Depends, Path, Query, status
from dependency_injector.wiring import Provide, inject
from fastapi.responses import FileResponse
from typing import List

from api.dependencies import Authorize, get_user_service
from domain.objects import schemas, entities, dtos
from api.core.container import AppContainer
from api.core.settings import Settings
from api.core.openapi import ENDPOINTS_METADATA
from api.dependencies.media import get_avatar
from domain.objects.types import Limit, Offset, UserRole
from domain.services import UserService


user_router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@user_router.get(
    "/me",
    **ENDPOINTS_METADATA["get_me"],
    response_model=schemas.UserWithMarketplaceUserResponse,
)
async def get_me(
    user: entities.UserEntity = Depends(Authorize()),
    user_service: UserService = Depends(get_user_service),
) -> schemas.UserWithMarketplaceUserResponse:
    return await user_service.get_or_create_marketplace_user(user.id)


@user_router.put(
    "/me",
    **ENDPOINTS_METADATA["update_me"],
    response_model=schemas.MarketplaceUserResponse,
)
async def update_me(
    data: schemas.UpdateMarketplaceUserRequest,
    user: entities.UserEntity = Depends(Authorize()),
    user_service: UserService = Depends(get_user_service),
) -> schemas.MarketplaceUserResponse:
    dto = dtos.UpdateMarketplaceUserDTO.model_validate(data)
    return await user_service.update_marketplace_user(user.id, dto)


@user_router.get(
    "/{user_id}/profile",
    **ENDPOINTS_METADATA["get_user_profile"],
    response_model=schemas.ProfileResponse,
)
async def get_user_profile(
    user_id: int = Path(description="User ID"),
    user_service: UserService = Depends(get_user_service),
    user: entities.UserEntity = Depends(Authorize()),
) -> schemas.ProfileResponse:
    return await user_service.get_profile(user_id)


@user_router.post(
    "/me/avatar",
    **ENDPOINTS_METADATA["upload_avatar"],
    response_model=schemas.MediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_avatar(
    file: entities.FileEntity = Depends(get_avatar),
) -> schemas.MediaResponse:
    return file


@user_router.get(
    "/{user_id}/avatar", **ENDPOINTS_METADATA["get_avatar"], response_class=FileResponse
)
@inject
async def get_avatar(
    user_id: int = Path(description="User ID"),
    user: entities.UserEntity = Depends(Authorize()),
    user_service: UserService = Depends(get_user_service),
    settings: Settings = Depends(Provide[AppContainer.settings]),
) -> FileResponse:
    avatar = await user_service.get_avatar(user_id)
    return FileResponse(
        path=settings.AVATAR_STORAGE_PATH + "/" + f"{avatar.name}.{avatar.extension}"
    )


@user_router.post(
    "/",
    **ENDPOINTS_METADATA["create_user"],
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: schemas.CreateUserRequest,
    user: entities.UserEntity = Depends(
        Authorize([UserRole.ADMIN, UserRole.MODERATOR])
    ),
    user_service: UserService = Depends(get_user_service),
) -> schemas.UserResponse:
    return await user_service.create(data.telegram_id, data.usernames)


@user_router.put(
    "/{user_id}",
    **ENDPOINTS_METADATA["update_user"],
    response_model=schemas.UserResponse,
)
async def update_user(
    data: schemas.UpdateUserRequest,
    user_id: int = Path(description="User ID"),
    user: entities.UserEntity = Depends(
        Authorize([UserRole.ADMIN, UserRole.MODERATOR])
    ),
    user_service: UserService = Depends(get_user_service),
) -> schemas.UserResponse:
    return await user_service.update(user_id, data.telegram_id, data.usernames)


@user_router.get(
    "/",
    **ENDPOINTS_METADATA["get_users"],
    response_model=List[schemas.UserResponse],
)
async def get_users(
    limit: Limit = Query(10, ge=1, le=20, description="Limit"),
    offset: Offset = Query(0, ge=0, description="Offset"),
    search: str = Query(min_length=3, max_length=100, description="Search"),
    user: entities.UserEntity = Depends(
        Authorize([UserRole.ADMIN, UserRole.MODERATOR])
    ),
    user_service: UserService = Depends(get_user_service),
) -> List[schemas.UserResponse]:
    dto = dtos.GetDTO(limit=limit, offset=offset, search=search)
    return await user_service.get_many(dto)


@user_router.get(
    "/{user_id}",
    **ENDPOINTS_METADATA["get_user"],
    response_model=schemas.UserResponse,
)
async def get_user(
    user_id: int = Path(description="User ID"),
    user: entities.UserEntity = Depends(
        Authorize([UserRole.ADMIN, UserRole.MODERATOR])
    ),
    user_service: UserService = Depends(get_user_service),
) -> schemas.UserResponse:
    return await user_service.get_by_id(user_id)
