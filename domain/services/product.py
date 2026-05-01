from typing import Optional, List

from domain.repositories import ProductRepository
from domain.objects import entities, dtos


class ProductService:

    def __init__(self, product_repository: ProductRepository) -> None:
        self.product_repository = product_repository

    async def create_product(
        self, dto: dtos.CreateProductDTO
    ) -> entities.ProductEntity:
        return await self.product_repository.create(dto)

    async def update_product(
        self, id: int, dto: dtos.UpdateProductDTO
    ) -> entities.ProductEntity:
        return await self.product_repository.update(id, dto)

    async def delete_product(self, id: int) -> None:
        return await self.product_repository.delete(id)

    async def create_product_type(
        self, dto: dtos.CreateProductTypeDTO
    ) -> entities.ProductTypeWithOptionsEntity:
        return await self.product_repository.create_product_type(dto)

    async def create_category(
        self, name: str, parent_category_id: Optional[int] = None
    ) -> entities.CategoryEntity:
        return await self.product_repository.create_category(name, parent_category_id)

    async def update_category(
        self, id: int, name: Optional[str] = None, parent_category_id: Optional[int] = None
    ) -> entities.CategoryEntity:
        return await self.product_repository.update_category(id, name, parent_category_id)

    async def delete_category(self, id: int) -> None:
        return await self.product_repository.delete_category(id)

    async def get_category(self, id: int) -> entities.CategoryEntity:
        return await self.product_repository.get_category(id)

    async def get_categories(
        self, name: Optional[str] = None, parent_category_id: Optional[int] = None
    ) -> List[entities.CategoryEntity]:
        return await self.product_repository.get_categories(name, parent_category_id)

    async def get_product(self, id: int) -> entities.ProductEntity:
        return await self.product_repository.get_product(id)

    async def get_products(
        self, category_id: int, name: Optional[str] = None
    ) -> List[entities.ProductEntity]:
        return await self.product_repository.get_products(category_id, name)
