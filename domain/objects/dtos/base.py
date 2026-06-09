from pydantic import BaseModel, ConfigDict
from typing import Optional


class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GetDTO(BaseDTO):
    limit: int
    offset: int
    search: Optional[str] = None


class EntityDTO(BaseDTO):
    id: Optional[int] = None
