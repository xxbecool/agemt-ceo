from typing import List, Optional, Dict, Any
from datetime import date
from pydantic import BaseModel


class KPIMetric(BaseModel):
    name: str
    value: float
    unit: str
    previous_value: Optional[float] = None
    change_pct: Optional[float] = None
    trend: Optional[str] = None
    target: Optional[float] = None
    target_achievement_pct: Optional[float] = None


class KPIResponse(BaseModel):
    period_start: date
    period_end: date
    metrics: List[KPIMetric]
    summary: str


class BranchComparisonMetric(BaseModel):
    branch_id: str
    branch_name: str
    region: Optional[str] = None
    revenue: float
    gross_profit: float
    profit_margin: float
    transaction_count: int
    avg_transaction_value: float
    growth_pct: Optional[float] = None
    rank: int


class BranchComparisonResponse(BaseModel):
    period_start: date
    period_end: date
    branches: List[BranchComparisonMetric]
    top_branch: Optional[str] = None
    total_revenue: float


class ProductPerformanceMetric(BaseModel):
    product_id: str
    product_name: str
    sku: str
    category: str
    units_sold: int
    revenue: float
    cost: float
    gross_profit: float
    profit_margin: float
    revenue_contribution_pct: float
    growth_pct: Optional[float] = None
    rank: int


class ProductPerformanceResponse(BaseModel):
    period_start: date
    period_end: date
    category: Optional[str] = None
    products: List[ProductPerformanceMetric]
    total_revenue: float
    total_units_sold: int


class AnomalyDetectionResponse(BaseModel):
    detected_at: date
    metric: str
    expected_value: float
    actual_value: float
    deviation_pct: float
    severity: str
    description: str
    affected_entity: Optional[str] = None
    affected_entity_type: Optional[str] = None
