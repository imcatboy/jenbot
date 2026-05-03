from fastapi import APIRouter, Depends, status, Query
from typing import Optional

from domain.objects.types import (
    IDSet,
    Limit,
    NoZeroInt,
    Offset,
    SortType,
)
from domain.objects import schemas, dtos, entities
from domain.services import MarketplaceService
from api.dependencies.uow import get_marketplace_service
from api.dependencies.auth import get_current_user


marketplace_router = APIRouter(prefix="/advertisements", tags=["Marketplace"])


@marketplace_router.get("/{id}", response_model=schemas.AdvertisementResponse)
async def get_advertisement(
    id: int,
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> schemas.AdvertisementResponse:
    return await marketplace_service.get_advertisement(id, user.id)


@marketplace_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.AdvertisementResponse,
)
async def create_advertisement(
    data: schemas.CreateAdvertisementRequest,
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> schemas.AdvertisementResponse:
    dto = dtos.CreateAdvertisementDTO(
        user_id=user.id,
        **data.model_dump(),
    )
    return await marketplace_service.create_advertisement(dto)


@marketplace_router.put("/{id}", response_model=schemas.AdvertisementResponse)
async def update_advertisement(
    id: int,
    data: schemas.UpdateAdvertisementRequest,
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> schemas.AdvertisementResponse:
    dto = dtos.UpdateAdvertisementDTO(
        user_id=user.id,
        **data.model_dump(),
    )
    return await marketplace_service.update_advertisement(id, dto)


@marketplace_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_advertisement(
    id: int,
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> None:
    await marketplace_service.delete_advertisement(id, user.id)


@marketplace_router.get("/", response_model=schemas.CatalogResponse)
async def get_catalog(
    limit: Limit = Query(10, description="Limit"),
    offset: Offset = Query(0, description="Offset"),
    category_ids: Optional[IDSet] = Query(None, description="Category IDs"),
    product_ids: Optional[IDSet] = Query(None, description="Product IDs"),
    seller_ids: Optional[IDSet] = Query(None, description="Seller IDs"),
    product_option_ids: Optional[IDSet] = Query(None, description="Product Option IDs"),
    min_count: Optional[NoZeroInt] = Query(None, description="Min Count"),
    high_rating: Optional[bool] = Query(None, description="High Rating"),
    sort_type: SortType = Query(SortType.POPULARITY, description="Sort Type"),
    marketplace_service: MarketplaceService = Depends(get_marketplace_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> schemas.CatalogResponse:
    dto = dtos.GetCatalogDTO(
        limit=limit,
        offset=offset,
        category_ids=category_ids,
        product_ids=product_ids,
        seller_ids=seller_ids,
        product_option_ids=product_option_ids,
        min_count=min_count,
        high_rating=high_rating,
        sort_type=sort_type,
    )
    return await marketplace_service.get_catalog(dto)
