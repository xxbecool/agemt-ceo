from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from api.deps import CurrentUser
from forecasting.revenue_forecast import RevenueForecast
from forecasting.inventory_forecast import InventoryForecast

router = APIRouter()


@router.get("/revenue")
async def forecast_revenue(
    current_user: CurrentUser,
    days: int = Query(default=30, ge=7, le=180),
    db: AsyncSession = Depends(get_db),
):
    forecaster = RevenueForecast(db=db, tenant_id=str(current_user.tenant_id))
    return await forecaster.predict(forecast_days=days)


@router.get("/inventory")
async def forecast_inventory(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    forecaster = InventoryForecast(db=db, tenant_id=str(current_user.tenant_id))
    return await forecaster.predict()
