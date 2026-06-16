from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar

from sqlalchemy import Table, and_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.objects.dtos import EntityDTO
from domain.objects.models import BaseModel, EntityModel
from .validation import EntityValidator
from domain.objects import exceptions


T = TypeVar("T", bound=EntityModel)
R = TypeVar("R", bound=EntityDTO)


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
        parent: EntityModel,
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
        parent: EntityModel,
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
        parent: EntityModel,
        child_model: Type[BaseModel],
        related_ids: List[int],
        foreign_key_column: Optional[str] = None,
    ) -> None:
        if not related_ids:
            return

        await self.validator.validate_ids_exist(child_model, related_ids)
        await self.session.execute(
            update(child_model)
            .where(child_model.id.in_(related_ids))
            .values({foreign_key_column or parent.fk_name: parent.id})
        )

    async def update_many_to_one_relation(
        self,
        parent: EntityModel,
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

    async def set_many_to_one_relation(
        self,
        parent: EntityModel,
        child_model: Type[BaseModel],
        value_column: str,
        values: Optional[List[Any]] = None,
        foreign_key_column: Optional[str] = None,
    ) -> None:
        if values is None:
            return

        values = set(values)

        fk_column = foreign_key_column or parent.fk_name

        if not values:
            await self.session.execute(
                delete(child_model).where(getattr(child_model, fk_column) == parent.id)
            )
            return

        result = await self.session.execute(
            select(child_model).where(getattr(child_model, fk_column) == parent.id)
        )
        current_objects = result.scalars().all()
        current_values = set(
            getattr(object, value_column) for object in current_objects
        )

        to_remove = [
            object
            for object in current_objects
            if getattr(object, value_column) not in values
        ]
        to_add = values - current_values

        if to_remove:
            await self.session.execute(
                delete(child_model).where(
                    and_(
                        getattr(child_model, fk_column) == parent.id,
                        getattr(child_model, value_column).in_(
                            [getattr(object, value_column) for object in to_remove]
                        ),
                    )
                )
            )

        for value in to_add:
            object = child_model(**{value_column: value, fk_column: parent.id})
            self.session.add(object)

        await self.session.flush()

    async def sync_many_to_one_relation(
        self,
        parent: EntityModel,
        child_model: Type[EntityModel],
        values: Optional[List[EntityDTO]] = None,
        foreign_key_column: Optional[str] = None,
    ) -> None:
        if values is None:
            return

        fk_column = foreign_key_column or parent.fk_name

        if not values:
            await self.session.execute(
                delete(child_model).where(getattr(child_model, fk_column) == parent.id)
            )
            return

        result = await self.session.execute(
            select(child_model).where(getattr(child_model, fk_column) == parent.id)
        )
        current_objects = {object.id: object for object in result.scalars().all()}
        incoming_with_id: Dict[int, dict[str, Any]] = {}
        objects_to_add: List[child_model] = []

        for item in values:
            item_data = item.model_dump(exclude_unset=True)
            item_data[fk_column] = parent.id

            if item.id is not None:
                incoming_with_id[item.id] = item_data
            else:
                objects_to_add.append(child_model(**item_data))

        ids_to_remove = set(current_objects.keys()) - set(incoming_with_id.keys())

        if ids_to_remove:
            await self.session.execute(
                delete(child_model).where(
                    and_(
                        getattr(child_model, fk_column) == parent.id,
                        child_model.id.in_(ids_to_remove),
                    )
                )
            )

        for object_id, incoming_data in incoming_with_id.items():
            object = current_objects.get(object_id)

            if not object:
                raise exceptions.ObjectNotFoundException(
                    child_model.__name__, id=object_id
                )

            for key, value in incoming_data.items():
                setattr(object, key, value)

        if objects_to_add:
            self.session.add_all(objects_to_add)

        await self.session.flush()

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

    async def get_all_by_id(
        self, model: Type[T], ids: List[int], options: Optional[List[Any]] = None
    ) -> List[T]:
        if not ids:
            return []

        ids = list(set(ids))
        query = select(model).where(model.id.in_(ids))

        if options:
            query = query.options(*options)

        result = await self.session.execute(query)
        objects = result.scalars().all()

        if len(objects) == len(ids):
            return objects

        missing_ids = set(ids) - set(object.id for object in objects)
        raise exceptions.ObjectNotFoundException(model.__name__, missing_ids)

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

    async def delete_many(self, model: Type[T], ids: List[int]) -> None:
        if not ids:
            return

        ids = list(set(ids))
        await self.session.execute(delete(model).where(model.id.in_(ids)))

    def sync_children(
        self,
        collection: List[T],
        dtos: List[R],
        create: Callable[[R], T],
        update: Callable[[T, R], None],
    ) -> List[T]:
        existing_by_id: Dict[int, T] = {
            object.id: object for object in collection if object.id is not None
        }

        result: List[T] = []

        for dto in dtos:
            if dto.id is None or dto.id not in existing_by_id:
                result.append(create(dto))
            else:
                obj = existing_by_id[dto.id]
                update(obj, dto)
                result.append(obj)

        collection[:] = result
        return result
