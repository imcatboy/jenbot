from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any


class BaseEntity(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConfigEntity(BaseEntity):
    key: str
    value: Any