from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import Table, and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from objects.models import BaseModel
from .validation import EntityValidator
from objects import exceptions


T = TypeVar("T", bound=BaseModel)


class BaseRepository:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.validator = EntityValidator(session)


    async def create_relation(
        self,
        entity: BaseModel,
        relation_model: Type[BaseModel],
        relation_id: int,
        relation_name: Optional[str] = None,
    ) -> None:
        if relation_name is None:
            relation_name = relation_model.fk_name

        await self.validator.validate_exists(relation_model, relation_id)
        setattr(entity, relation_name, relation_id)


    async def update_relation(
        self,
        entity: BaseModel,
        relation_model: Type[BaseModel],
        relation_id: int,
        relation_name: Optional[str] = None,
    ) -> None:
        if relation_id:
            await self.create_relation(
                entity, relation_model, relation_id, relation_name
            )


    async def set_optional_relation(
        self,
        entity: BaseModel,
        relation_model: Type[BaseModel],
        relation_id: Optional[int],
        relation_name: Optional[str] = None,
    ) -> None:
        if relation_id == 0:
            setattr(entity, relation_name, None)
        elif relation_id:
            await self.create_relation(
                entity, relation_model, relation_id, relation_name
            )


    async def update_many_to_many_relation(
        self,
        parent: BaseModel,
        association_table: Table,
        related_model: Type[BaseModel],
        new_related_ids: Optional[List[int]] = None,
        parent_id_column: Optional[str] = None,
        related_id_column: Optional[str] = None,
    ) -> None:
        if new_related_ids is None:
            return

        result = await self.session.execute(
            select(
                getattr(association_table.c, related_id_column or related_model.fk_name)
            ).where(
                getattr(association_table.c, parent_id_column or parent.fk_name)
                == parent.id
            )
        )
        existing_related_ids = set(result.scalars().all())
        new_related_ids_set = set(new_related_ids)
        ids_to_remove = existing_related_ids - new_related_ids_set
        ids_to_add = new_related_ids_set - existing_related_ids
        await self.validator.validate_ids_exist(related_model, ids_to_add)

        if ids_to_remove:
            await self.session.execute(
                association_table.delete().where(
                    and_(
                        getattr(association_table.c, parent_id_column or parent.fk_name)
                        == parent.id,
                        getattr(
                            association_table.c,
                            related_id_column or related_model.fk_name,
                        ).in_(ids_to_remove),
                    )
                )
            )

        if ids_to_add:
            await self.session.execute(
                association_table.insert().values(
                    [
                        {
                            parent_id_column or parent.fk_name: parent.id,
                            related_id_column or related_model.fk_name: related_id,
                        }
                        for related_id in ids_to_add
                    ]
                )
            )


    async def create_many_to_many_relation(
        self,
        parent: BaseModel,
        association_table: Table,
        related_model: Type[BaseModel],
        related_ids: List[int],
        parent_id_column: Optional[str] = None,
        related_id_column: Optional[str] = None,
    ) -> None:
        if not related_ids:
            return

        await self.validator.validate_ids_exist(related_model, related_ids)
        await self.session.execute(
            association_table.insert().values(
                [
                    {
                        parent_id_column or parent.fk_name: parent.id,
                        related_id_column or related_model.fk_name: related_id,
                    }
                    for related_id in related_ids
                ]
            )
        )


    async def create_many_to_one_relation(
        self,
        parent: BaseModel,
        child_model: Type[BaseModel],
        related_ids: List[int],
        foreign_key_column: Optional[str] = None,
    ) -> None:
        if not related_ids:
            return

        await self.validator.validate_ids_exist(child_model, related_ids)
        result = await self.session.execute(
            select(child_model).where(child_model.id.in_(related_ids))
        )
        objects = result.scalars().all()

        for obj in objects:
            setattr(obj, foreign_key_column or parent.fk_name, parent.id)


    async def update_many_to_one_relation(
        self,
        parent: BaseModel,
        child_model: Type[BaseModel],
        new_related_ids: Optional[List[int]] = None,
        foreign_key_column: Optional[str] = None,
    ) -> None:
        if new_related_ids is None:
            return

        result = await self.session.execute(
            select(child_model.id).where(
                getattr(child_model, foreign_key_column or parent.fk_name) == parent.id
            )
        )

        current_child_ids = set(result.scalars().all())
        new_child_ids_set = set(new_related_ids)
        ids_to_remove = current_child_ids - new_child_ids_set
        ids_to_add = new_child_ids_set - current_child_ids
        await self.validator.validate_ids_exist(child_model, ids_to_add)

        if ids_to_remove:
            await self.session.execute(
                update(child_model)
                .where(
                    and_(
                        child_model.id.in_(ids_to_remove),
                        getattr(child_model, foreign_key_column or parent.fk_name)
                        == parent.id,
                    )
                )
                .values({foreign_key_column or parent.fk_name: None})
            )

        if ids_to_add:
            await self.session.execute(
                update(child_model)
                .where(child_model.id.in_(ids_to_add))
                .values({foreign_key_column or parent.fk_name: parent.id})
            )


    async def get_by_id(
        self, model: Type[T], id: int, options: Optional[List[Any]] = None
    ) -> T:
        query = select(model).where(model.id == id)

        if options:
            query = query.options(*options)

        result = await self.session.execute(query)
        object = result.unique().scalar_one_or_none()

        if not object:
            raise exceptions.ObjectNotFoundException(model.__name__, [id])

        return object


    async def get_one_by_data(
        self, model: Type[T], options: Optional[List[Any]] = None, **data: Any
    ) -> T:
        query = select(model).filter_by(**data)

        if options:
            query = query.options(*options)

        result = await self.session.execute(query)
        objects = result.scalars().all()

        if not objects:
            raise exceptions.ObjectNotFoundException(model.__name__, **data)

        if len(objects) > 1:
            raise exceptions.TooManyObjectsFoundException(model.__name__, **data)

        return objects[0]


    async def get_one_by_data_or_none(
        self, model: Type[T], options: Optional[List[Any]] = None, **data: Any
    ) -> T | None:
        query = select(model).filter_by(**data)

        if options:
            query = query.options(*options)

        result = await self.session.execute(query)
        objects = result.scalars().all()

        if not objects:
            return None

        if len(objects) > 1:
            raise exceptions.TooManyObjectsFoundException(model.__name__, **data)

        return objects[0]


    async def get_all_by_data(
        self, model: Type[T], options: Optional[List[Any]] = None, **data: Any
    ) -> List[T]:
        query = select(model).filter_by(**data)

        if options:
            query = query.options(*options)

        result = await self.session.execute(query)
        return result.scalars().all()


    async def update_many(self, model: Type[T], ids: List[int], **data: Any) -> None:
        await self.session.execute(
            update(model).where(model.id.in_(ids)).values(**data)
        )