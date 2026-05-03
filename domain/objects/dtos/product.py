from typing import List, Optional

from .base import BaseDTO, GetDTO
from domain.objects import entities


class CreateProductDTO(BaseDTO):
    name: str
    category_id: int
    product_type_ids: List[int]
    image_ids: List[int]


class UpdateProductDTO(BaseDTO):
    name: Optional[str] = None
    image_ids: Optional[List[int]] = None
    category_id: Optional[int] = None
    product_type_ids: Optional[List[int]] = None


class CreateProductTypeDTO(BaseDTO):
    name: str
    can_many: bool
    options: List[str]


class GetCategoriesDTO(GetDTO):
    name: Optional[str] = None
    parent_category_id: Optional[int] = None


class GetProductsDTO(GetDTO):
    category_id: int
    name: Optional[str] = None


class ProductsDTO(BaseDTO):
    items: List[entities.ProductEntity]
    has_more: bool


class CategoriesDTO(BaseDTO):
    items: List[entities.CategoryEntity]
    has_more: bool
