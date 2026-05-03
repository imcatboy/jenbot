from typing import List, Tuple

from domain.repositories import MarketplaceRepository, ProductRepository
from domain.mappers import MarketplaceMapper
from domain.objects import dtos, exceptions


class MarketplaceService:

    def __init__(
        self,
        marketplace_repository: MarketplaceRepository,
        mapper: MarketplaceMapper,
        product_repository: ProductRepository,
    ) -> None:
        self.marketplace_repository = marketplace_repository
        self.mapper = mapper
        self.product_repository = product_repository

    async def get_advertisement(self, id: int, user_id: int) -> dtos.AdvertisementDTO:
        if not await self.marketplace_repository.is_user_allowed_to_access(id, user_id):
            raise exceptions.ObjectNotFoundException("AdvertisementModel", [id])

        advertisement = await self.marketplace_repository.get_advertisement(id)
        return self.mapper.advertisement_to_dto(advertisement)

    async def create_advertisement(
        self, dto: dtos.CreateAdvertisementDTO
    ) -> dtos.AdvertisementDTO:
        product_relations: List[Tuple[int, List[int]]] = [
            (dto.product_id, option.product_option_ids) for option in dto.options
        ] + [
            (trade.product_id, trade.product_option_ids)
            for option in dto.options
            for trade in option.trades
        ]
        await self.check_option_relations(product_relations)
        advertisement = await self.marketplace_repository.create_advertisement(dto)
        return await self.get_advertisement(advertisement.id, dto.user_id)

    async def update_advertisement(
        self, id: int, dto: dtos.UpdateAdvertisementDTO
    ) -> dtos.AdvertisementDTO:
        product = await self.marketplace_repository.get_advertisement_product(id)
        product_relations: List[Tuple[int, List[int]]] = [
            (product.id, option.product_option_ids) for option in dto.options
        ] + [
            (trade.product_id, trade.product_option_ids)
            for option in dto.options
            for trade in option.trades
        ]
        await self.check_option_relations(product_relations)
        advertisement = await self.marketplace_repository.update_advertisement(id, dto)
        return await self.get_advertisement(advertisement.id, dto.user_id)

    async def delete_advertisement(self, id: int, user_id: int) -> None:
        await self.marketplace_repository.delete_advertisement(id, user_id)

    async def check_option_relations(
        self, product_relations: List[Tuple[int, List[int]]]
    ) -> None:
        if not product_relations:
            return

        requested_product_ids = list(
            set(product_relation[0] for product_relation in product_relations)
        )
        products = await self.product_repository.get_products_by_ids(
            requested_product_ids
        )

        for product in products:
            product_option_ids = [
                product_option.id
                for product_type in product.product_types
                for product_option in product_type.options
            ]
            product_one_type_option_ids = [
                [product_option.id for product_option in product_type.options]
                for product_type in product.product_types
                if not product_type.can_many
            ]

            relations = [
                product_relation[1]
                for product_relation in product_relations
                if product_relation[0] == product.id
            ]

            for relation in relations:
                if not all(option_id in product_option_ids for option_id in relation):
                    raise exceptions.MissingOptionException(product.id, relation)

                for product_one_type_option_id in product_one_type_option_ids:
                    intersection = set(product_one_type_option_id) & set(relation)

                    if len(intersection) > 1:
                        raise exceptions.InvalidOptionRelationException(
                            product.id, intersection
                        )

    async def get_catalog(self, dto: dtos.GetCatalogDTO) -> dtos.CatalogDTO:
        dto = dto.model_copy(update={"limit": dto.limit + 1})
        options = await self.marketplace_repository.get_catalog(dto)
        has_more = len(options) == dto.limit

        if has_more:
            options = options[:-1]

        return dtos.CatalogDTO(
            items=[self.mapper.option_short_to_dto(option) for option in options],
            has_more=has_more,
        )
