from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from datetime import datetime

from api.dependencies.auth import get_current_user, Authorize
from domain.objects.types import ID, DealStatus, UserRole
from api.dependencies.uow import get_trading_service
from domain.objects import schemas, entities, dtos
from domain.services import TradingService

trading_router = APIRouter(prefix="/trading", tags=["Marketplace"])


@trading_router.post("/buy", response_model=schemas.DealResponse)
async def buy_advertisement_option(
    data: schemas.BuyAdvertisementOptionRequest,
    trading_service: TradingService = Depends(get_trading_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> schemas.DealResponse:
    dto = dtos.BuyAdvertisementOptionDTO(
        user_id=user.id,
        **data.model_dump(),
    )
    return await trading_service.buy_advertisement_option(dto)


@trading_router.put("/{deal_id}/condition", status_code=status.HTTP_204_NO_CONTENT)
async def change_deal_condition(
    deal_id: ID,
    data: schemas.UpdateDealConditionRequest,
    trading_service: TradingService = Depends(get_trading_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> None:
    return await trading_service.change_condition(deal_id, user.id, data.condition)


@trading_router.get("/{deal_id}", response_model=schemas.DealResponse)
async def get_deal(
    deal_id: ID,
    trading_service: TradingService = Depends(get_trading_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> schemas.DealResponse:
    return await trading_service.get_deal(deal_id, user.id)


@trading_router.get("/", response_model=List[schemas.DealResponse])
async def get_deals(
    buyer_id: Optional[ID] = Query(None, description="Buyer ID"),
    seller_id: Optional[ID] = Query(None, description="Seller ID"),
    agent_id: Optional[ID] = Query(None, description="Agent ID"),
    expires_at: Optional[datetime] = Query(None, description="Expires at"),
    status: Optional[DealStatus] = Query(None, description="Status"),
    product_id: Optional[ID] = Query(None, description="Product ID"),
    trading_service: TradingService = Depends(get_trading_service),
    user: entities.UserEntity = Depends(get_current_user),
) -> List[schemas.DealResponse]:
    dto = dtos.GetDealsDTO(
        user_id=user.id,
        buyer_id=buyer_id,
        seller_id=seller_id,
        agent_id=agent_id,
        expires_at=expires_at,
        status=status,
        product_id=product_id,
    )
    return await trading_service.get_deals(dto)


@trading_router.get(
    "/scam-reports/{report_id}", response_model=schemas.ScamReportResponse
)
async def get_scam_report(
    report_id: ID,
    trading_service: TradingService = Depends(get_trading_service),
    user: entities.UserEntity = Depends(
        Authorize([UserRole.ADMIN, UserRole.MODERATOR])
    ),
) -> schemas.ScamReportResponse:
    return await trading_service.get_scam_report(report_id)
