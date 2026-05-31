from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from models.inventory import StockStatus


class InventoryStatusResponse(BaseModel):
    item_id: str
    product_id: str
    product_name: str
    sku: str
    category: str
    warehouse_id: str
    warehouse_name: str
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    reorder_point: int
    max_capacity: int
    stock_status: StockStatus
    utilization_pct: float
    avg_daily_consumption: float
    days_until_depletion: Optional[float] = None
    estimated_depletion_date: Optional[date] = None
    last_restocked_at: Optional[date] = None
    stock_turnover_rate: Optional[float] = None


class InventoryAlertResponse(BaseModel):
    product_id: str
    product_name: str
    sku: str
    warehouse_name: str
    alert_type: str  # low_stock, overstock, out_of_stock, reorder
    severity: str
    current_quantity: int
    threshold_quantity: int
    message: str
    days_until_depletion: Optional[float] = None


class WarehouseUtilizationResponse(BaseModel):
    warehouse_id: str
    warehouse_name: str
    warehouse_code: str
    city: Optional[str] = None
    max_capacity: int
    current_stock_count: int
    utilization_pct: float
    item_count: int
    low_stock_items: int
    overstock_items: int
    out_of_stock_items: int


class InventoryForecastResponse(BaseModel):
    product_id: str
    product_name: str
    sku: str
    warehouse_id: str
    warehouse_name: str
    current_quantity: int
    avg_daily_consumption: float
    reorder_point: int
    forecast_days: int
    predicted_quantity: float
    days_until_reorder: Optional[float] = None
    days_until_stockout: Optional[float] = None
    recommended_reorder_quantity: int
