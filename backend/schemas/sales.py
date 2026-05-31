from typing import List, Optional
from datetime import date
from pydantic import BaseModel


class DailySalesResponse(BaseModel):
    date: date
    total_revenue: float
    total_cost: float
    gross_profit: float
    profit_margin: float
    transaction_count: int
    units_sold: int
    avg_transaction_value: float
    prev_day_revenue: Optional[float] = None
    day_over_day_change: Optional[float] = None  # percentage
    day_over_day_change_pct: Optional[float] = None


class MonthlySalesResponse(BaseModel):
    year: int
    month: int
    month_name: str
    total_revenue: float
    total_cost: float
    gross_profit: float
    profit_margin: float
    transaction_count: int
    units_sold: int
    prev_month_revenue: Optional[float] = None
    month_over_month_growth_pct: Optional[float] = None
    year_over_year_growth_pct: Optional[float] = None


class QuarterlySalesResponse(BaseModel):
    year: int
    quarter: int
    quarter_label: str
    total_revenue: float
    total_cost: float
    gross_profit: float
    profit_margin: float
    transaction_count: int
    months: List[MonthlySalesResponse] = []


class TopProductResponse(BaseModel):
    product_id: str
    product_name: str
    sku: str
    category: str
    total_revenue: float
    total_units_sold: int
    gross_profit: float
    profit_margin: float
    rank: int


class BranchPerformanceResponse(BaseModel):
    branch_id: str
    branch_name: str
    branch_code: str
    region: Optional[str] = None
    total_revenue: float
    total_cost: float
    gross_profit: float
    profit_margin: float
    transaction_count: int
    units_sold: int
    revenue_share_pct: float
    growth_pct: Optional[float] = None


class SalesTrendPoint(BaseModel):
    date: date
    revenue: float
    transactions: int
    units: int


class SalesTrendResponse(BaseModel):
    period: str
    data_points: List[SalesTrendPoint]
    total_revenue: float
    avg_daily_revenue: float
    peak_day: Optional[date] = None
    peak_revenue: Optional[float] = None
