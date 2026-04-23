from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any


class BaseEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class EntityWithId(BaseEntity):
    id: int


class MetadataEntity(BaseEntity):
    created_at: datetime
    updated_at: datetime


class EntityWithMetadata(EntityWithId):
    created_at: datetime
    updated_at: datetime


class ConfigEntity(BaseEntity):
    key: str
    value: Any
