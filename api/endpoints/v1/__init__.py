from fastapi import APIRouter

from .user import user_router
from .product import product_router
from .marketplace import marketplace_router
from .trading import trading_router
from .messaging import messaging_router
from .reputation import reputation_router

v1_router = APIRouter(
    prefix="/v1",
)

v1_router.include_router(user_router)
v1_router.include_router(product_router)
v1_router.include_router(marketplace_router)
v1_router.include_router(trading_router)
v1_router.include_router(messaging_router)
v1_router.include_router(reputation_router)
