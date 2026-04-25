from fastapi import APIRouter, Depends

from domain.objects import schemas, entities
from api.dependencies import get_current_user_cached
from api.core.openapi import ENDPOINTS_METADATA


user_router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@user_router.get("/me", **ENDPOINTS_METADATA["get_me"], response_model=schemas.UserResponse)
async def get_me(user: entities.UserEntity = Depends(get_current_user_cached)) -> schemas.UserShortResponse:
    return user
