from typing import List, Optional, Set

from domain.objects.types import Name, ID, ImageURL
from .base import BaseRequest


class CreateProductTypeRequest(BaseRequest):
    name: Name
    can_many: bool
    options: Set[Name]


class CreateProductRequest(BaseRequest):
    name: Name
    image_urls: List[ImageURL]
    category_id: ID
    product_types: Optional[List[CreateProductTypeRequest]] = None
    product_types_ids: Optional[Set[ID]] = None