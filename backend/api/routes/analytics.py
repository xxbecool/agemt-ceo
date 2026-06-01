"""
Analytics routes: KPIs, branch comparison, product performance, anomaly detection.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, timedelta

from core.database import get_db
from api.deps import CurrentUser
from models.sale import Sale
from models.inventory import InventoryItem
from models.alert import Alert
from services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/kpis")
async def get_kpis(
    current_user: CurrentUser,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Return key performance indicators for the current period."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    svc = AnalyticsService(db)
    result = await svc.get_kpis(current_user.tenant_id, start_date, end_date)
    return result.model_dump()


@router.get("/branch-comparison")
async def get_branch_comparison(
    current_user: CurrentUser,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Return branch performance comparison for a given period."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    svc = AnalyticsService(db)
    result = await svc.get_branch_comparison(
        current_user.tenant_id, start_date, end_date
    )
    return result.model_dump()


@router.get("/product-performance")
async def get_product_performance(
    current_user: CurrentUser,
    days: int = Query(default=30, ge=1, le=365),
    category: str = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Return product performance metrics, optionally filtered by category."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    svc = AnalyticsService(db)
    result = await svc.get_product_performance(
        current_user.tenant_id, start_date, end_date, category, limit
    )
    return result.model_dump()


@router.get("/anomalies")
async def detect_anomalies(
    current_user: CurrentUser,
    lookback_days: int = Query(default=30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Detect statistical anomalies in revenue using z-score method."""
    svc = AnalyticsService(db)
    anomalies = await svc.detect_anomalies(current_user.tenant_id, lookback_days)
    return {
        "detected": len(anomalies) > 0,
        "total_anomalies": len(anomalies),
        "anomalies": [a.model_dump() for a in anomalies],
        "lookback_days": lookback_days,
    }


@router.get("/dashboard-summary")
async def get_dashboard_summary(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return a high-level summary for the executive dashboard."""
    tid = current_user.tenant_id
    today = date.today()
    mtd_start = today.replace(day=1)

    mtd = await db.execute(
        select(
            func.sum(Sale.total_amount).label("revenue"),
            func.count(Sale.id).label("orders"),
            func.sum(Sale.gross_profit).label("gross_profit"),
        ).where(
            and_(Sale.tenant_id == tid, Sale.sale_date >= mtd_start, Sale.sale_date <= today)
        )
    )
    row = mtd.one()
    rev = float(row.revenue or 0)
    orders = int(row.orders or 0)
    gp = float(row.gross_profit or 0)

    prev_end = mtd_start - timedelta(days=1)
    prev_start = prev_end.replace(day=1)
    prev_mtd = await db.execute(
        select(func.sum(Sale.total_amount)).where(
            and_(Sale.tenant_id == tid, Sale.sale_date >= prev_start, Sale.sale_date <= prev_end)
        )
    )
    prev_rev = float(prev_mtd.scalar() or 0)
    growth_pct = ((rev - prev_rev) / prev_rev * 100) if prev_rev else 0

    inv_total = await db.execute(
        select(func.count(InventoryItem.id)).where(InventoryItem.tenant_id == tid)
    )
    from models.inventory import StockStatus
    inv_critical = await db.execute(
        select(func.count(InventoryItem.id)).where(
            and_(
                InventoryItem.tenant_id == tid,
                InventoryItem.stock_status.in_([StockStatus.CRITICAL, StockStatus.OUT_OF_STOCK]),
            )
        )
    )

    total_inv = int(inv_total.scalar() or 0)
    critical_inv = int(inv_critical.scalar() or 0)
    inventory_health_pct = (
        round((total_inv - critical_inv) / total_inv * 100, 1) if total_inv > 0 else 100.0
    )

    alert_count = await db.execute(
        select(func.count(Alert.id)).where(
            and_(Alert.tenant_id == tid, Alert.is_read == False)  # noqa
        )
    )
    active_alerts = int(alert_count.scalar() or 0)

    return {
        "revenue_mtd": round(rev, 2),
        "revenue_growth_pct": round(growth_pct, 1),
        "orders_mtd": orders,
        "gross_profit_mtd": round(gp, 2),
        "profit_margin_pct": round((gp / rev * 100) if rev else 0, 1),
        "avg_order_value": round(rev / orders if orders else 0, 2),
        "inventory_health_pct": inventory_health_pct,
        "critical_inventory_items": critical_inv,
        "active_alerts": active_alerts,
        "generated_at": today.isoformat(),
    }
