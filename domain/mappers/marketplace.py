from collections import defaultdict
from typing import Dict, List

from domain.objects import entities, dtos


class MarketplaceMapper:

    def get_advertisement_option_key(
        self,
        options: List[entities.ProductOptionEntity],
    ) -> str:
        options_by_type = defaultdict[int, List[int]](list)

        for option in options:
            options_by_type[option.product_type_id].append(option.id)

        sorted_type_ids = sorted(options_by_type.keys())
        parts = []

        for type_id in sorted_type_ids:
            type_id_str = str(type_id)
            sorted_option_ids = sorted(options_by_type[type_id])
            options_str = ",".join(str(option_id) for option_id in sorted_option_ids)
            parts.append(f"{type_id_str}:{options_str}")

        key = ";".join(parts)
        return key

    def category_path(self, category: entities.CategoryWithParentEntity) -> str:
        return (
            category.name + " > " + category.parent_category.name
            if category.parent_category
            else category.name
        )

    def advertisement_to_dto(
        self, advertisement: entities.AdvertisementEntityWithOptions
    ) -> dtos.AdvertisementDTO:
        category_path = self.category_path(advertisement.product.category)
        return dtos.AdvertisementDTO(
            id=advertisement.id,
            name=advertisement.product.name,
            category_path=category_path,
            user=self.user_to_dto(advertisement.user),
            product_types=advertisement.product.product_types,
            options=self.options_to_dto(advertisement.options),
        )

    def user_to_dto(
        self, user: entities.UserWithMarketplaceUserEntity
    ) -> dtos.SellerDTO:
        return dtos.SellerDTO(
            usernames=[username.username for username in user.usernames],
            **user.marketplace_user.model_dump(),
        )

    def options_to_dto(
        self,
        options: List[entities.AdvertisementOptionWithRelations],
    ) -> Dict[str, dtos.AdvertisementOptionDTO]:
        return {
            self.get_advertisement_option_key(
                option.product_options
            ): self.option_to_dto(option)
            for option in options
        }

    def option_to_dto(
        self, option: entities.AdvertisementOptionWithRelations
    ) -> dtos.AdvertisementOptionDTO:
        return dtos.AdvertisementOptionDTO(
            id=option.id,
            count=option.count,
            prices=self.prices_to_dto(option.prices),
            product_options=option.product_options,
            trades=self.trades_to_dto(option.trades),
        )

    def prices_to_dto(
        self, prices: List[entities.AdvertisementOptionPriceWithCurrency]
    ) -> List[dtos.AdvertisementOptionPriceDTO]:
        return [self.price_to_dto(price) for price in prices]

    def price_to_dto(
        self, price: entities.AdvertisementOptionPriceWithCurrency
    ) -> dtos.AdvertisementOptionPriceDTO:
        return dtos.AdvertisementOptionPriceDTO(
            id=price.id,
            amount=price.amount,
            currency_sign=price.currency.sign,
        )

    def trades_to_dto(
        self, trades: List[entities.TradeWithRelations]
    ) -> List[dtos.TradeDTO]:
        return [self.trade_to_dto(trade) for trade in trades]

    def trade_to_dto(self, trade: entities.TradeWithRelations) -> dtos.TradeDTO:
        return dtos.TradeDTO(
            id=trade.id,
            count=trade.count,
            product=self.product_to_dto(trade.product),
            product_options=trade.product_options,
        )

    def product_to_dto(
        self, product: entities.ProductEntityWithRelations
    ) -> dtos.ProductDTO:
        category_path = self.category_path(product.category)
        return dtos.ProductDTO(
            id=product.id,
            name=product.name,
            images=product.images,
            category_path=category_path,
        )

    def advertisement_options_to_dto(
        self, options: List[entities.AdvertisementOptionEntityWithAdvertisement]
    ) -> List[dtos.AdvertisementOptionShortDTO]:
        return [self.option_short_to_dto(option) for option in options]

    def option_short_to_dto(
        self, option: entities.AdvertisementOptionEntityWithAdvertisement
    ) -> dtos.AdvertisementOptionShortDTO:
        image_url = f"/api/v1/products/{option.advertisement.product.id}/attachments/{option.advertisement.product.images[0].id}"
        return dtos.AdvertisementOptionShortDTO(
            id=option.id,
            name=option.advertisement.product.name,
            category_path=self.category_path(option.advertisement.product.category),
            has_trades=len(option.trades) > 0,
            image_url=image_url,
            user=self.user_to_dto(option.advertisement.user),
            options=[option.name for option in option.product_options],
            prices=[
                f"{price.amount:.2f} {price.currency.sign}" for price in option.prices
            ],
        )
