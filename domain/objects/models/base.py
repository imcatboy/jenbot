from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, JSON
from datetime import datetime
from typing import Any


class BaseModel(DeclarativeBase):
    fk_name: str


class MetadataModel:
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )


class EntityModel(BaseModel, MetadataModel):
    id: Mapped[int] = mapped_column(primary_key=True)


class ConfigModel(BaseModel):
    __tablename__ = "configs"
    fk_name = "config_id"

    key: Mapped[str] = mapped_column(String(255))
    value: Mapped[Any] = mapped_column(JSON, nullable=False)
