from typing import List, Optional

from .base import BaseDTO


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