from typing import Optional

from domain.repositories import ProductRepository, MediaRepository
from domain.objects import entities, dtos, exceptions


class ProductService:

    def __init__(self, product_repository: ProductRepository, media_repository: MediaRepository) -> None:
        self.product_repository = product_repository
        self.media_repository = media_repository

    async def create_product(
        self, dto: dtos.CreateProductDTO
    ) -> entities.ProductEntity:
        if not await self.media_repository.is_user_unlinked_files(
            dto.author_id, dto.image_ids
        ):
            raise exceptions.FileNotFoundException(*dto.image_ids)

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
        self, dto: dtos.CreateCategoryDTO
    ) -> entities.CategoryEntity:
        return await self.product_repository.create_category(dto)

    async def update_category(
        self,
        id: int,
        name: Optional[str] = None,
        parent_category_id: Optional[int] = None,
    ) -> entities.CategoryEntity:
        return await self.product_repository.update_category(
            id, name, parent_category_id
        )

    async def delete_category(self, id: int) -> None:
        return await self.product_repository.delete_category(id)

    async def get_category(self, id: int) -> entities.CategoryEntity:
        return await self.product_repository.get_category(id)

    async def get_categories(self, dto: dtos.GetCategoriesDTO) -> dtos.CategoriesDTO:
        dto = dto.model_copy(update={"limit": dto.limit + 1})
        categories = await self.product_repository.get_categories(dto)
        has_more = len(categories) == dto.limit

        if has_more:
            categories = categories[:-1]

        return dtos.CategoriesDTO(items=categories, has_more=has_more)

    async def get_product(self, id: int) -> entities.ProductEntity:
        return await self.product_repository.get_product(id)

    async def get_products(self, dto: dtos.GetProductsDTO) -> dtos.ProductsDTO:
        dto = dto.model_copy(update={"limit": dto.limit + 1})
        products = await self.product_repository.get_products(dto)
        has_more = len(products) == dto.limit

        if has_more:
            products = products[:-1]

        return dtos.ProductsDTO(items=products, has_more=has_more)

    async def get_attachment(self, product_id: int, file_id: int) -> entities.FileEntity:
        return await self.media_repository.get_product_file(product_id, file_id)