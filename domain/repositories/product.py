from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from domain.objects import exceptions, models, entities, dtos
from .relations import get_product_relations
from .base import BaseRepository


class ProductRepository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, dto: dtos.CreateProductDTO) -> entities.ProductEntity:
        product = models.ProductModel(
            **dto.model_dump(exclude={"product_type_ids", "image_ids"})
        )
        await self.create_relation(product, models.CategoryModel, dto.category_id)
        await self.set_optional_relation(
            product, models.UserModel, dto.author_id, "author_id"
        )
        self.session.add(product)
        await self.session.flush()
        await self.create_many_to_many_relation(
            product,
            models.product_types_products,
            models.ProductTypeModel,
            dto.product_type_ids,
        )
        await self.create_many_to_one_relation(product, models.FileModel, dto.image_ids)
        return entities.ProductEntity.model_validate(product)

    async def update(
        self, id: int, dto: dtos.UpdateProductDTO
    ) -> entities.ProductEntity:
        product = await self.get_by_id(models.ProductModel, id)

        if dto.name:
            product.name = dto.name

        await self.update_relation(product, models.CategoryModel, dto.category_id)
        await self.update_many_to_many_relation(
            product,
            models.product_types_products,
            models.ProductTypeModel,
            dto.product_type_ids,
        )
        await self.update_many_to_one_relation(product, models.FileModel, dto.image_ids)
        await self.session.flush()
        return entities.ProductEntity.model_validate(product)

    async def delete(self, id: int) -> None:
        product = await self.get_by_id(models.ProductModel, id)
        await self.session.delete(product)

    async def create_product_type(
        self, dto: dtos.CreateProductTypeDTO
    ) -> entities.ProductTypeWithOptionsEntity:
        product_type = models.ProductTypeModel(**dto.model_dump(exclude={"options"}))

        for option in dto.options:
            product_option = models.ProductOptionModel(name=option)
            product_type.options.append(product_option)

        self.session.add(product_type)
        await self.session.flush()
        return entities.ProductTypeWithOptionsEntity.model_validate(product_type)

    async def create_category(
        self, dto: dtos.CreateCategoryDTO
    ) -> entities.CategoryEntity:
        category = models.CategoryModel(name=dto.name)
        await self.set_optional_relation(
            category, models.CategoryModel, dto.parent_category_id, "parent_category_id"
        )
        await self.set_optional_relation(
            category, models.UserModel, dto.author_id, "author_id"
        )
        self.session.add(category)
        await self.session.flush()
        return entities.CategoryEntity.model_validate(category)

    async def get_category(self, id: int) -> entities.CategoryEntity:
        category = await self.get_by_id(models.CategoryModel, id)
        return entities.CategoryEntity.model_validate(category)

    async def update_category(
        self,
        id: int,
        name: Optional[str] = None,
        parent_category_id: Optional[int] = None,
    ) -> entities.CategoryEntity:
        category = await self.get_by_id(models.CategoryModel, id)

        if name:
            category.name = name

        await self.set_optional_relation(
            category, models.CategoryModel, parent_category_id, "parent_category_id"
        )
        await self.session.flush()
        return entities.CategoryEntity.model_validate(category)

    async def delete_category(self, id: int) -> None:
        category = await self.get_by_id(models.CategoryModel, id)
        await self.session.delete(category)

    async def get_product(self, id: int) -> entities.ProductEntity:
        product = await self.get_by_id(
            models.ProductModel, id, options=get_product_relations()
        )
        return entities.ProductEntity.model_validate(product)

    async def get_categories(
        self, dto: dtos.GetCategoriesDTO
    ) -> List[entities.CategoryEntity]:
        query = (
            select(models.CategoryModel)
            .filter_by(parent_category_id=dto.parent_category_id, is_draft=False)
            .limit(dto.limit)
            .offset(dto.offset)
        )

        if dto.name:
            query = query.filter(models.CategoryModel.name.ilike(f"%{dto.name}%"))
        if dto.search:
            query = query.filter(models.CategoryModel.name.ilike(f"%{dto.search}%"))

        result = await self.session.execute(query)
        return [
            entities.CategoryEntity.model_validate(category)
            for category in result.scalars().all()
        ]

    async def get_products(
        self, dto: dtos.GetProductsDTO
    ) -> List[entities.ProductEntity]:
        query = (
            select(models.ProductModel)
            .filter_by(category_id=dto.category_id, is_draft=False)
            .limit(dto.limit)
            .offset(dto.offset)
        )

        if dto.name:
            query = query.filter(models.ProductModel.name.ilike(f"%{dto.name}%"))
        if dto.search:
            query = query.filter(models.ProductModel.name.ilike(f"%{dto.search}%"))

        result = await self.session.execute(query)
        return [
            entities.ProductEntity.model_validate(product)
            for product in result.scalars().all()
        ]

    async def get_products_by_ids(
        self, ids: List[int]
    ) -> List[entities.ProductEntityWithRelations]:
        result = await self.session.execute(
            select(models.ProductModel)
            .filter(models.ProductModel.id.in_(ids))
            .options(*get_product_relations())
        )
        products = result.scalars().all()
        missing_ids = set(ids) - set([product.id for product in products])

        if missing_ids:
            raise exceptions.ObjectNotFoundException("ProductModel", list(missing_ids))

        return [
            entities.ProductEntityWithRelations.model_validate(product)
            for product in products
        ]
