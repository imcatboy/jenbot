from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from fastapi.responses import FileResponse

from domain.objects.types import Name, ID, Reason, UserRole, Limit, Offset
from api.dependencies import get_product_service, Authorize, get_product_image
from domain.objects import schemas, dtos, entities
from api.core.openapi import ENDPOINTS_METADATA
from domain.services import ProductService
from api.core.container import AppContainer
from api.core.settings import Settings


product_router = APIRouter(
    prefix="/products",
    tags=["Product"],
)


@product_router.post(
    "/types",
    **ENDPOINTS_METADATA["create_product_type"],
    response_model=schemas.ProductTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_type(
    data: schemas.CreateProductTypeRequest,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize()),
) -> schemas.ProductTypeResponse:
    dto = dtos.CreateProductTypeDTO.model_validate(data)
    return await product_service.create_product_type(dto)


@product_router.post(
    "/categories",
    **ENDPOINTS_METADATA["create_category"],
    response_model=schemas.CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: schemas.CreateCategoryRequest,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize()),
) -> schemas.CategoryResponse:
    dto = dtos.CreateCategoryDTO(**data.model_dump(), author_id=user.id)
    return await product_service.create_category(dto)


@product_router.put(
    "/categories/{id}",
    **ENDPOINTS_METADATA["update_category"],
    response_model=schemas.CategoryResponse,
)
async def update_category(
    id: ID,
    data: schemas.UpdateCategoryRequest,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize([UserRole.ADMIN])),
) -> schemas.CategoryResponse:
    return await product_service.update_category(id, **data.model_dump())


@product_router.delete(
    "/categories/{id}",
    **ENDPOINTS_METADATA["delete_category"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    id: ID,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize([UserRole.ADMIN])),
) -> None:
    await product_service.delete_category(id)


@product_router.get(
    "/categories/{id}",
    **ENDPOINTS_METADATA["get_category"],
    response_model=schemas.CategoryResponse,
)
async def get_category(
    id: ID,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize()),
) -> schemas.CategoryResponse:
    return await product_service.get_category(id)


@product_router.get(
    "/categories",
    **ENDPOINTS_METADATA["get_categories"],
    response_model=schemas.CategoriesResponse,
)
async def get_categories(
    limit: Limit = Query(10, description="Limit"),
    offset: Offset = Query(0, description="Offset"),
    name: Optional[Name] = Query(None, description="Name of the category"),
    parent_category_id: Optional[ID] = Query(None, description="Parent category ID"),
    search: Optional[Reason] = Query(None, description="Search"),
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize()),
) -> schemas.CategoriesResponse:
    dto = dtos.GetCategoriesDTO(
        limit=limit,
        offset=offset,
        name=name,
        parent_category_id=parent_category_id,
        search=search,
    )
    return await product_service.get_categories(dto)


@product_router.post(
    "/",
    **ENDPOINTS_METADATA["create_product"],
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: schemas.CreateProductRequest,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize()),
) -> schemas.ProductResponse:
    dto = dtos.CreateProductDTO(**data.model_dump(), author_id=user.id)
    return await product_service.create_product(dto)


@product_router.put(
    "/{id}",
    **ENDPOINTS_METADATA["update_product"],
    response_model=schemas.ProductResponse,
)
async def update_product(
    id: int,
    data: schemas.UpdateProductRequest,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize([UserRole.ADMIN])),
) -> schemas.ProductResponse:
    dto = dtos.UpdateProductDTO.model_validate(data)
    return await product_service.update_product(id, dto)


@product_router.delete(
    "/{id}",
    **ENDPOINTS_METADATA["delete_product"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    id: int,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize([UserRole.ADMIN])),
) -> None:
    await product_service.delete_product(id)


@product_router.get(
    "/{id}", **ENDPOINTS_METADATA["get_product"], response_model=schemas.ProductResponse
)
async def get_product(
    id: ID,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize()),
) -> schemas.ProductResponse:
    return await product_service.get_product(id)


@product_router.get(
    "/", **ENDPOINTS_METADATA["get_products"], response_model=schemas.ProductsResponse
)
async def get_products(
    category_id: ID = Query(description="Category ID"),
    name: Optional[Name] = Query(None, description="Name of the product"),
    limit: Limit = Query(10, description="Limit"),
    offset: Offset = Query(0, description="Offset"),
    search: Optional[Reason] = Query(None, description="Search"),
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize()),
) -> schemas.ProductsResponse:
    dto = dtos.GetProductsDTO(
        limit=limit, offset=offset, category_id=category_id, name=name, search=search
    )
    return await product_service.get_products(dto)


@product_router.post(
    "/attachments",
    **ENDPOINTS_METADATA["upload_product_attachment"],
    response_model=schemas.MediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_product_attachment(
    file: entities.FileEntity = Depends(get_product_image),
) -> schemas.MediaResponse:
    return file


@product_router.get(
    "/{product_id}/attachments/{file_id}",
    **ENDPOINTS_METADATA["get_product_attachment"],
    response_class=FileResponse,
)
@inject
async def get_product_attachment(
    product_id: ID,
    file_id: ID,
    product_service: ProductService = Depends(get_product_service),
    user: entities.UserEntity = Depends(Authorize()),
    settings: Settings = Depends(Provide[AppContainer.settings]),
) -> FileResponse:
    file = await product_service.get_attachment(product_id, file_id)
    return FileResponse(
        path=settings.PRODUCT_IMAGE_STORAGE_PATH + "/" + f"{file.name}.{file.extension}"
    )
