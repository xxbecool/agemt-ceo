from typing import List, Optional
from datetime import date
from pydantic import BaseModel


class ForecastPoint(BaseModel):
    date: date
    yhat: float
    yhat_lower: float
    yhat_upper: float
    trend: Optional[float] = None
    seasonality: Optional[float] = None


class ForecastResponse(BaseModel):
    entity_id: Optional[str] = None
    entity_type: str
    forecast_horizon_days: int
    model: str
    generated_at: str
    historical_avg: float
    forecast_avg: float
    growth_pct: float
    data_points: List[ForecastPoint]
    confidence_level: float = 0.80


class RevenueForecastResponse(BaseModel):
    forecast_horizon_days: int
    total_forecasted_revenue: float
    avg_daily_revenue: float
    growth_pct_vs_historical: float
    data_points: List[ForecastPoint]
    model: str = "prophet"
    confidence_level: float = 0.80


class InventoryForecastPoint(BaseModel):
    date: date
    predicted_quantity: float
    quantity_lower: float
    quantity_upper: float
    reorder_suggested: bool = False


class InventoryForecastDetailResponse(BaseModel):
    product_id: str
    product_name: str
    sku: str
    warehouse_id: str
    current_quantity: int
    avg_daily_consumption: float
    forecast_horizon_days: int
    reorder_point: int
    data_points: List[InventoryForecastPoint]
    days_until_stockout: Optional[float] = None
    recommended_reorder_date: Optional[date] = None
    recommended_reorder_quantity: int = 0
