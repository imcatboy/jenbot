from fastapi import APIRouter, Depends, Path, Query, status
from typing import List

from api.dependencies import Authorize, get_user_service
from domain.objects import schemas, entities, dtos
from api.core.openapi import ENDPOINTS_METADATA
from domain.objects.types import UserRole
from domain.services import UserService

reputation_router = APIRouter(
    prefix="/reputation",
    tags=["Reputation"],
)


@reputation_router.post(
    "/",
    **ENDPOINTS_METADATA["create_reputation_user"],
    response_model=schemas.ReputationUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reputation_user(
    data: schemas.CreateReputationUserRequest,
    user: entities.UserEntity = Depends(
        Authorize([UserRole.ADMIN, UserRole.MODERATOR])
    ),
    user_service: UserService = Depends(get_user_service),
) -> schemas.ReputationUserResponse:
    dto = dtos.CreateReputationUserDTO(**data.model_dump(), added_by_user_id=user.id)
    return await user_service.create_reputation_user(dto)


@reputation_router.put(
    "/{reputation_user_id}",
    **ENDPOINTS_METADATA["update_reputation_user"],
    response_model=schemas.ReputationUserResponse,
)
async def update_reputation_user(
    data: schemas.UpdateReputationUserRequest,
    reputation_user_id: int = Path(description="Reputation User ID"),
    user: entities.UserEntity = Depends(
        Authorize([UserRole.ADMIN, UserRole.MODERATOR])
    ),
    user_service: UserService = Depends(get_user_service),
) -> schemas.ReputationUserResponse:
    dto = dtos.UpdateReputationUserDTO(**data.model_dump(), added_by_user_id=user.id)
    return await user_service.update_reputation_user(reputation_user_id, dto)


@reputation_router.get(
    "/{reputation_user_id}",
    **ENDPOINTS_METADATA["get_reputation_user"],
    response_model=schemas.ReputationUserWithRelationsResponse,
)
async def get_reputation_user(
    reputation_user_id: int = Path(description="Reputation User ID"),
    user: entities.UserEntity = Depends(
        Authorize([UserRole.ADMIN, UserRole.MODERATOR])
    ),
    user_service: UserService = Depends(get_user_service),
) -> schemas.ReputationUserWithRelationsResponse:
    return await user_service.get_reputation_user(reputation_user_id)


@reputation_router.get(
    "/",
    **ENDPOINTS_METADATA["get_reputation_users"],
    response_model=List[schemas.ReputationUserWithUsersResponse],
)
async def get_reputation_users(
    search: str = Query(description="Search"),
    user: entities.UserEntity = Depends(
        Authorize([UserRole.ADMIN, UserRole.MODERATOR])
    ),
    user_service: UserService = Depends(get_user_service),
) -> List[schemas.ReputationUserWithUsersResponse]:
    return await user_service.get_reputation_users(search)
