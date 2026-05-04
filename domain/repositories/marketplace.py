from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from sqlalchemy.orm import joinedload

from domain.objects.models.associate_tables import (
    advertisement_options_product_options,
)
from domain.objects.types import SortType
from domain.repositories.relations import (
    get_advertisement_relations,
    get_full_advertisement_relations,
    get_advertisement_option_relations,
    get_trade_relations,
)
from domain.objects import entities, dtos, exceptions, models
from .base import BaseRepository


class MarketplaceRepository(BaseRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_advertisement(
        self, dto: dtos.CreateAdvertisementDTO
    ) -> entities.AdvertisementEntity:
        advertisement = models.AdvertisementModel()
        await self.create_relation(advertisement, models.UserModel, dto.user_id)
        await self.create_relation(advertisement, models.ProductModel, dto.product_id)
        currency_ids = [
            price_dto.currency_id
            for option_dto in dto.options
            for price_dto in option_dto.prices
        ]
        product_ids = [
            trade_dto.product_id
            for option_dto in dto.options
            for trade_dto in option_dto.trades
        ]
        product_ids.append(dto.product_id)
        all_product_option_ids = [
            product_option_id
            for option_dto in dto.options
            for product_option_id in option_dto.product_option_ids
        ] + [
            product_option_id
            for option_dto in dto.options
            for trade_dto in option_dto.trades
            for product_option_id in trade_dto.product_option_ids
        ]
        await self.validator.validate_ids_exist(models.CurrencyModel, currency_ids)
        await self.validator.validate_ids_exist(models.ProductModel, product_ids)
        await self.validator.validate_exists(models.UserModel, dto.user_id)
        product_options = await self.get_all_by_id(
            models.ProductOptionModel, all_product_option_ids
        )
        product_options_by_id = {
            product_option.id: product_option for product_option in product_options
        }

        for option_dto in dto.options:
            option = models.AdvertisementOptionModel(count=option_dto.count)
            option.product_options = [
                product_options_by_id[product_option_id]
                for product_option_id in option_dto.product_option_ids
            ]

            for price_dto in option_dto.prices:
                price = models.AdvertisementOptionPriceModel(
                    amount=price_dto.amount, currency_id=price_dto.currency_id
                )
                option.prices.append(price)

            for trade_dto in option_dto.trades:
                trade = models.TradeModel(
                    product_id=trade_dto.product_id,
                    count=trade_dto.count,
                )
                trade.product_options = [
                    product_options_by_id[product_option_id]
                    for product_option_id in trade_dto.product_option_ids
                ]
                option.trades.append(trade)

            advertisement.options.append(option)

        self.session.add(advertisement)
        await self.session.flush()
        return entities.AdvertisementEntity.model_validate(advertisement)

    async def update_advertisement(
        self, id: int, dto: dtos.UpdateAdvertisementDTO
    ) -> entities.AdvertisementEntity:
        advertisement = await self.get_one_by_data(
            models.AdvertisementModel,
            get_advertisement_relations(),
            user_id=dto.user_id,
            id=id,
        )
        advertisement.is_draft = dto.is_draft
        await self._validate_references(advertisement, dto.options)
        all_product_option_ids = {
            product_option_id
            for option_dto in dto.options
            for product_option_id in option_dto.product_option_ids
        } | {
            product_option_id
            for option_dto in dto.options
            for trade_dto in option_dto.trades
            for product_option_id in trade_dto.product_option_ids
        }
        product_options = await self.get_all_by_id(
            models.ProductOptionModel, list(all_product_option_ids)
        )
        product_options_by_id = {
            product_option.id: product_option for product_option in product_options
        }
        self._sync_options(advertisement, dto.options, product_options_by_id)
        await self.session.flush()
        return entities.AdvertisementEntity.model_validate(advertisement)

    async def _validate_references(
        self,
        advertisement: models.AdvertisementModel,
        update_dtos: List[dtos.UpdateAdvertisementOptionDTO],
    ) -> None:
        incoming_option_ids_list = [
            option_dto.id for option_dto in update_dtos if option_dto.id is not None
        ]

        if len(incoming_option_ids_list) != len(set(incoming_option_ids_list)):
            raise exceptions.DuplicateIdsException(
                models.AdvertisementOptionModel.__name__,
                incoming_option_ids_list,
            )

        incoming_option_ids = set(incoming_option_ids_list)
        existing_option_ids = {
            option.id for option in advertisement.options if option.id is not None
        }
        unknown_option_ids = incoming_option_ids - existing_option_ids

        if unknown_option_ids:
            raise exceptions.ObjectNotFoundException(
                models.AdvertisementOptionModel.__name__,
                list(unknown_option_ids),
            )

        options_by_id: Dict[int, models.AdvertisementOptionModel] = {
            option.id: option
            for option in advertisement.options
            if option.id is not None
        }

        for option_dto in update_dtos:
            option = options_by_id[option_dto.id]
            price_ids_in_order = [
                price_dto.id
                for price_dto in option_dto.prices
                if price_dto.id is not None
            ]

            if len(price_ids_in_order) != len(set(price_ids_in_order)):
                raise exceptions.DuplicateIdsException(
                    models.AdvertisementOptionPriceModel.__name__,
                    price_ids_in_order,
                )

            trade_ids_in_order = [
                trade_dto.id
                for trade_dto in option_dto.trades
                if trade_dto.id is not None
            ]

            if len(trade_ids_in_order) != len(set(trade_ids_in_order)):
                raise exceptions.DuplicateIdsException(
                    models.TradeModel.__name__,
                    trade_ids_in_order,
                )
            dto_price_ids = {
                price_dto.id
                for price_dto in option_dto.prices
                if price_dto.id is not None
            }
            existing_price_ids = {price.id for price in option.prices}

            unknown_prices = dto_price_ids - existing_price_ids

            if unknown_prices:
                raise exceptions.ObjectNotFoundException(
                    models.AdvertisementOptionPriceModel.__name__,
                    list(unknown_prices),
                )

            dto_trade_ids = {
                trade_dto.id
                for trade_dto in option_dto.trades
                if trade_dto.id is not None
            }
            existing_trade_ids = {trade.id for trade in option.trades}
            unknown_trades = dto_trade_ids - existing_trade_ids

            if unknown_trades:
                raise exceptions.ObjectNotFoundException(
                    models.TradeModel.__name__,
                    list(unknown_trades),
                )

        currency_ids = [
            price_dto.currency_id
            for option_dto in update_dtos
            for price_dto in option_dto.prices
        ]
        product_ids = [advertisement.product_id] + [
            trade_dto.product_id
            for option_dto in update_dtos
            for trade_dto in option_dto.trades
        ]
        await self.validator.validate_ids_exist(models.CurrencyModel, currency_ids)
        await self.validator.validate_ids_exist(models.ProductModel, product_ids)

    def _sync_options(
        self,
        advertisement: models.AdvertisementModel,
        update_dtos: List[dtos.UpdateAdvertisementOptionDTO],
        product_options_by_id: Dict[int, models.ProductOptionModel],
    ) -> None:
        def create(
            option_dto: dtos.UpdateAdvertisementOptionDTO,
        ) -> models.AdvertisementOptionModel:
            return models.AdvertisementOptionModel(count=option_dto.count)

        def update(
            obj: models.AdvertisementOptionModel,
            option_dto: dtos.UpdateAdvertisementOptionDTO,
        ) -> None:
            obj.count = option_dto.count

        synced = self.sync_children(advertisement.options, update_dtos, create, update)

        for dto, option in zip(update_dtos, synced):
            option.product_options = [
                product_options_by_id[product_option_id]
                for product_option_id in dto.product_option_ids
            ]
            self._sync_prices(option, dto.prices)
            self._sync_trades(option, dto.trades, product_options_by_id)

    def _sync_prices(
        self,
        option: models.AdvertisementOptionModel,
        update_dtos: List[dtos.UpdateAdvertisementOptionPriceDTO],
    ) -> None:
        def create(
            price_dto: dtos.UpdateAdvertisementOptionPriceDTO,
        ) -> models.AdvertisementOptionPriceModel:
            return models.AdvertisementOptionPriceModel(
                amount=price_dto.amount, currency_id=price_dto.currency_id
            )

        def update(
            obj: models.AdvertisementOptionPriceModel,
            price_dto: dtos.UpdateAdvertisementOptionPriceDTO,
        ) -> None:
            obj.amount = price_dto.amount
            obj.currency_id = price_dto.currency_id

        self.sync_children(option.prices, update_dtos, create, update)

    def _sync_trades(
        self,
        option: models.AdvertisementOptionModel,
        update_dtos: List[dtos.UpdateAdvertisementTradeDTO],
        product_options_by_id: Dict[int, models.ProductOptionModel],
    ) -> None:
        def create(trade_dto: dtos.UpdateAdvertisementTradeDTO) -> models.TradeModel:
            trade = models.TradeModel(
                product_id=trade_dto.product_id, count=trade_dto.count
            )
            trade.product_options = [
                product_options_by_id[product_option_id]
                for product_option_id in trade_dto.product_option_ids
            ]
            return trade

        def update(
            obj: models.TradeModel, trade_dto: dtos.UpdateAdvertisementTradeDTO
        ) -> None:
            obj.product_id = trade_dto.product_id
            obj.count = trade_dto.count
            obj.product_options = [
                product_options_by_id[product_option_id]
                for product_option_id in trade_dto.product_option_ids
            ]

        self.sync_children(option.trades, update_dtos, create, update)

    async def delete_advertisement(self, id: int, user_id: int) -> None:
        advertisement = await self.get_one_by_data(
            models.AdvertisementModel,
            user_id=user_id,
            id=id,
        )
        await self.session.delete(advertisement)

    async def get_advertisement(
        self, id: int
    ) -> entities.AdvertisementEntityWithOptions:
        advertisement = await self.get_by_id(
            models.AdvertisementModel, id, get_full_advertisement_relations()
        )
        return entities.AdvertisementEntityWithOptions.model_validate(advertisement)

    async def is_user_allowed_to_access(self, id: int, user_id: int) -> bool:
        advertisement = await self.get_by_id(models.AdvertisementModel, id)
        return advertisement.user_id == user_id or not advertisement.is_draft

    async def get_advertisement_product(self, id: int) -> entities.ProductEntity:
        result = await self.session.execute(
            select(models.ProductModel)
            .join(models.AdvertisementModel)
            .where(models.AdvertisementModel.id == id)
        )
        product = result.scalar_one_or_none()

        if not product:
            raise exceptions.ObjectNotFoundException(models.ProductModel.__name__, id)

        return entities.ProductEntity.model_validate(product)

    async def get_catalog(
        self, dto: dtos.GetCatalogDTO
    ) -> List[entities.AdvertisementOptionEntityWithAdvertisement]:
        query = (
            select(models.AdvertisementOptionModel)
            .options(*get_advertisement_option_relations())
            .join(
                models.AdvertisementModel,
                models.AdvertisementOptionModel.advertisement_id
                == models.AdvertisementModel.id,
            )
            .join(
                models.ProductModel,
                models.AdvertisementModel.product_id == models.ProductModel.id,
            )
            .where(models.AdvertisementModel.is_draft == False)
        )

        if dto.category_ids:
            query = query.where(models.ProductModel.category_id.in_(dto.category_ids))
        if dto.product_ids:
            query = query.where(models.ProductModel.id.in_(dto.product_ids))
        if dto.seller_ids:
            query = query.where(models.AdvertisementModel.user_id.in_(dto.seller_ids))
        if dto.product_option_ids:
            for product_option_id in dto.product_option_ids:
                query = query.where(
                    exists(
                        select(1)
                        .select_from(advertisement_options_product_options)
                        .where(
                            advertisement_options_product_options.c.advertisement_option_id
                            == models.AdvertisementOptionModel.id,
                            advertisement_options_product_options.c.product_option_id
                            == product_option_id,
                        )
                    )
                )
        if dto.min_count:
            query = query.where(models.AdvertisementOptionModel.count >= dto.min_count)
        if dto.high_rating:
            query = query.join(
                models.MarketplaceUserModel,
                models.MarketplaceUserModel.user_id
                == models.AdvertisementModel.user_id,
            ).where(models.MarketplaceUserModel.rating >= 4.5)

        match dto.sort_type:
            case SortType.POPULARITY:
                query = query.order_by(
                    models.AdvertisementOptionModel.sold_count.desc()
                )
            case SortType.NEW:
                query = query.order_by(
                    models.AdvertisementOptionModel.created_at.desc()
                )
            case SortType.OLD:
                query = query.order_by(models.AdvertisementOptionModel.created_at.asc())

        query = query.limit(dto.limit).offset(dto.offset)
        options = await self.session.execute(query)
        return [
            entities.AdvertisementOptionEntityWithAdvertisement.model_validate(option)
            for option in options.scalars().all()
        ]

    async def get_suggestion_categories(
        self, dto: dtos.GetAdvertisementSuggestionsDTO
    ) -> List[entities.CategoryEntity]:
        query = (
            select(models.CategoryModel)
            .join(models.ProductModel)
            .join(models.AdvertisementModel)
            .where(
                models.AdvertisementModel.is_draft == False,
                exists(
                    select(1)
                    .select_from(models.AdvertisementOptionModel)
                    .where(
                        models.AdvertisementOptionModel.advertisement_id
                        == models.AdvertisementModel.id,
                    ),
                ),
            )
        )

        if dto.category_ids:
            query = query.where(
                models.CategoryModel.parent_category_id.in_(dto.category_ids)
            )
        if dto.seller_ids:
            query = query.where(models.AdvertisementModel.user_id.in_(dto.seller_ids))
        if dto.search:
            query = query.where(models.CategoryModel.name.ilike(f"%{dto.search}%"))

        query = query.limit(dto.limit).offset(dto.offset)
        categories = await self.session.execute(query)
        return [
            entities.CategoryEntity.model_validate(category)
            for category in categories.scalars().unique().all()
        ]

    async def get_suggestion_products(
        self, dto: dtos.GetAdvertisementSuggestionsDTO
    ) -> List[entities.ProductEntity]:
        query = (
            select(models.ProductModel)
            .join(models.AdvertisementModel)
            .where(
                models.AdvertisementModel.is_draft == False,
                exists(
                    select(1)
                    .select_from(models.AdvertisementOptionModel)
                    .where(
                        models.AdvertisementOptionModel.advertisement_id
                        == models.AdvertisementModel.id,
                    ),
                ),
            )
        )

        if dto.category_ids:
            query = query.where(models.ProductModel.category_id.in_(dto.category_ids))
        if dto.seller_ids:
            query = query.where(models.AdvertisementModel.user_id.in_(dto.seller_ids))
        if dto.search:
            query = query.where(models.ProductModel.name.ilike(f"%{dto.search}%"))

        query = query.limit(dto.limit).offset(dto.offset)
        products = await self.session.execute(query)
        return [
            entities.ProductEntity.model_validate(product)
            for product in products.scalars().unique().all()
        ]

    async def get_suggestion_sellers(
        self, dto: dtos.GetAdvertisementSuggestionsDTO
    ) -> List[entities.UserEntity]:
        query = (
            select(models.UserModel)
            .join(models.AdvertisementModel)
            .where(
                models.AdvertisementModel.is_draft == False,
                exists(
                    select(1)
                    .select_from(models.AdvertisementOptionModel)
                    .where(
                        models.AdvertisementOptionModel.advertisement_id
                        == models.AdvertisementModel.id,
                    ),
                ),
            )
        )

        if dto.category_ids:
            query = query.join(
                models.ProductModel,
                models.AdvertisementModel.product_id == models.ProductModel.id,
            ).where(
                models.ProductModel.category_id.in_(dto.category_ids),
            )
        if dto.product_ids:
            query = query.where(
                models.AdvertisementModel.product_id.in_(dto.product_ids)
            )
        if dto.search:
            query = query.where(
                models.UserModel.username.isnot(None),
                models.UserModel.username.ilike(f"%{dto.search}%"),
            )

        query = query.limit(dto.limit).offset(dto.offset)
        sellers = await self.session.execute(query)
        return [
            entities.UserEntity.model_validate(seller)
            for seller in sellers.scalars().unique().all()
        ]

    async def get_suggestion_product_options(
        self, dto: dtos.GetAdvertisementSuggestionsDTO
    ) -> List[entities.ProductOptionEntity]:
        query = (
            select(models.ProductOptionModel)
            .join(models.ProductOptionModel.advertisement_options)
            .join(models.AdvertisementOptionModel.advertisement)
            .where(models.AdvertisementModel.is_draft == False)
        )

        if dto.category_ids:
            query = query.join(
                models.ProductModel,
                models.AdvertisementModel.product_id == models.ProductModel.id,
            ).where(models.ProductModel.category_id.in_(dto.category_ids))
        if dto.product_ids:
            query = query.where(
                models.AdvertisementModel.product_id.in_(dto.product_ids)
            )
        if dto.seller_ids:
            query = query.where(models.AdvertisementModel.user_id.in_(dto.seller_ids))
        if dto.product_option_ids:
            for product_option_id in dto.product_option_ids:
                query = query.where(
                    exists(
                        select(1)
                        .select_from(advertisement_options_product_options)
                        .where(
                            advertisement_options_product_options.c.advertisement_option_id
                            == models.AdvertisementOptionModel.id,
                            advertisement_options_product_options.c.product_option_id
                            == product_option_id,
                        )
                    )
                )
        if dto.search:
            query = query.where(models.ProductOptionModel.name.ilike(f"%{dto.search}%"))

        query = query.limit(dto.limit).offset(dto.offset)
        product_options = await self.session.execute(query)
        return [
            entities.ProductOptionEntity.model_validate(product_option)
            for product_option in product_options.scalars().unique().all()
        ]

    async def get_advertisement_option(
        self, id: int
    ) -> entities.AdvertisementOptionEntityWithAdvertisement:
        option = await self.get_by_id(
            models.AdvertisementOptionModel, id, get_advertisement_option_relations()
        )
        return entities.AdvertisementOptionEntityWithAdvertisement.model_validate(
            option
        )

    async def get_advertisement_option_price(
        self, id: int
    ) -> entities.AdvertisementOptionPriceWithCurrency:
        price = await self.get_by_id(
            models.AdvertisementOptionPriceModel,
            id,
            [joinedload(models.AdvertisementOptionPriceModel.currency)],
        )
        return entities.AdvertisementOptionPriceWithCurrency.model_validate(price)

    async def get_advertisement_option_trade(
        self, id: int
    ) -> entities.TradeWithRelations:
        trade = await self.get_by_id(models.TradeModel, id, get_trade_relations())
        return entities.TradeWithRelations.model_validate(trade)
