from fastapi import APIRouter

from .v1 import v1_router
from .exceptions import *


api_router = APIRouter(
    prefix="/api",
)
api_router.include_router(v1_router)
