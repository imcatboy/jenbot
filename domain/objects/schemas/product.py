from typing import List, Optional, Set

from domain.objects.types import Name, ID, IDSet
from .base import BaseRequest, BaseResponse


class CreateProductTypeRequest(BaseRequest):
    name: Name
    can_many: bool
    options: Set[Name]


class CreateProductRequest(BaseRequest):
    name: Name
    image_ids: IDSet
    category_id: ID
    product_type_ids: Optional[IDSet] = None


class UpdateProductRequest(BaseRequest):
    name: Optional[Name] = None
    image_ids: Optional[IDSet] = None
    category_id: Optional[ID] = None
    product_type_ids: Optional[IDSet] = None


class CreateCategoryRequest(BaseRequest):
    name: Name
    parent_category_id: Optional[ID] = None


class UpdateCategoryRequest(BaseRequest):
    name: Optional[Name] = None
    parent_category_id: Optional[ID] = None


class CategoryResponse(BaseResponse):
    id: int
    name: str
    parent_category_id: Optional[int] = None
    is_draft: bool


class ProductImageResponse(BaseResponse):
    id: int
    name: str
    display_name: str
    extension: str


class ProductResponse(BaseResponse):
    id: int
    name: str
    is_draft: bool
    category_id: int


class ProductsResponse(BaseResponse):
    items: List[ProductResponse]
    has_more: bool


class CategoriesResponse(BaseResponse):
    items: List[CategoryResponse]
    has_more: bool
