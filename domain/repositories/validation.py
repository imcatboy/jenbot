from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Type
from sqlalchemy import select

from domain.objects import exceptions, BaseModel


class EntityValidator:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def validate_exists(self, model: Type[BaseModel], entity_id: int) -> None:
        entity = await self.session.get(model, entity_id)

        if not entity:
            raise exceptions.ObjectNotFoundException(model.__name__, [entity_id])

    async def validate_ids_exist(self, model: Type[BaseModel], ids: List[int]) -> None:
        if not ids:
            return
        
        ids = list(set(ids))

        existing_objects = await self.session.execute(
            select(model.id).where(model.id.in_(ids))
        )
        existing_ids = set(existing_objects.scalars().all())
        missing_ids = set(ids) - existing_ids

        if missing_ids:
            raise exceptions.ObjectNotFoundException(model.__name__, missing_ids)

    async def validate_data_not_exists(
        self, model: Type[BaseModel], **data: Any
    ) -> None:
        if not data:
            return

        result = await self.session.execute(select(model.id).filter_by(**data))
        objects = result.scalars().all()

        if objects:
            raise exceptions.ObjectAlreadyExistsException(model.__name__, **data)

    async def validate_data_exists(self, model: Type[BaseModel], **data: Any) -> None:
        if not data:
            return

        result = await self.session.execute(select(model.id).filter_by(**data))
        objects = result.scalars().all()

        if not objects:
            raise exceptions.ObjectNotFoundException(model.__name__, **data)

    async def validate_data_one_exists(
        self, model: Type[BaseModel], **data: Any
    ) -> None:
        if not data:
            return

        result = await self.session.execute(select(model.id).filter_by(**data))
        objects = result.scalars().all()

        if not objects:
            raise exceptions.ObjectNotFoundException(model.__name__, **data)

        if len(objects) > 1:
            raise exceptions.TooManyObjectsFoundException(model.__name__, **data)
