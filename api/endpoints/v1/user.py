from fastapi import APIRouter, Depends, Path

from api.dependencies import get_current_user_cached, get_user_service
from api.core.openapi import ENDPOINTS_METADATA
from domain.objects import schemas, entities
from domain.services import UserService


user_router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@user_router.get(
    "/me", **ENDPOINTS_METADATA["get_me"], response_model=schemas.UserResponse
)
async def get_me(
    user: entities.UserEntity = Depends(get_current_user_cached),
    user_service: UserService = Depends(get_user_service),
) -> schemas.UserResponse:
    return await user_service.get_or_create_marketplace_user(user.id)


@user_router.get(
    "/{user_id}/profile", **ENDPOINTS_METADATA["get_user_profile"], response_model=schemas.ProfileResponse
)
async def get_user_profile(
    user_id: int = Path(..., description="User ID"),
    user_service: UserService = Depends(get_user_service),
    user: entities.UserEntity = Depends(get_current_user_cached),
) -> schemas.ProfileResponse:
    return await user_service.get_profile(user_id)