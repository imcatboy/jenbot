from sqlalchemy import Column, ForeignKey, Integer, Table

from .base import BaseModel


product_types_products = Table(
    "product_types_products",
    BaseModel.metadata,
    Column(
        "product_id",
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
    Column(
        "product_type_id",
        Integer,
        ForeignKey("product_types.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
)

advertisement_options_product_options = Table(
    "advertisement_options_product_options",
    BaseModel.metadata,
    Column(
        "product_option_id",
        Integer,
        ForeignKey("product_options.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
    Column(
        "advertisement_option_id",
        Integer,
        ForeignKey("advertisement_options.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
)
