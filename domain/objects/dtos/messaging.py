from typing import Optional

from .base import BaseDTO


class CreateFileDTO(BaseDTO):
    name: str
    display_name: str
    extension: str
    message_id: Optional[int] = None
    product_id: Optional[int] = None
    uploaded_by_user_id: int