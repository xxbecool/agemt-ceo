"""
Data tools used by the ExecutiveAI LangGraph agent.
Each tool queries the database and returns structured data for the LLM.
"""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, timedelta

from models.sale import Sale, SaleItem
from models.inventory import InventoryItem, StockStatus
from models.product import Product
from models.alert import Alert, AlertSeverity
from models.branch import Branch


async def get_sales_summary(db: AsyncSession, tenant_id: str, period: str = "7d") -> dict:
    """Fetch aggregated sales summary for the specified period."""
    days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
    days = days_map.get(period, 7)
    start_date = date.today() - timedelta(days=days)

    result = await db.execute(
        select(
            func.sum(Sale.total_amount).label("revenue"),
            func.count(Sale.id).label("orders"),
            func.sum(Sale.gross_profit).label("gross_profit"),
        ).where(and_(Sale.tenant_id == tenant_id, Sale.sale_date >= start_date))
    )
    row = result.one()
    rev = float(row.revenue or 0)
    gp = float(row.gross_profit or 0)
    orders = int(row.orders or 0)

    # Daily breakdown
    daily_result = await db.execute(
        select(Sale.sale_date, func.sum(Sale.total_amount).label("rev"))
        .where(and_(Sale.tenant_id == tenant_id, Sale.sale_date >= start_date))
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date.desc())
        .limit(7)
    )
    daily = [
        {"date": r.sale_date.isoformat(), "revenue": round(float(r.rev), 2)}
        for r in daily_result.all()
    ]

    return {
        "period": period,
        "total_revenue": round(rev, 2),
        "total_orders": orders,
        "gross_profit": round(gp, 2),
        "profit_margin_pct": round((gp / rev * 100) if rev else 0, 1),
        "avg_daily_revenue": round(rev / days, 2),
        "daily_breakdown": daily,
    }


async def get_inventory_status(db: AsyncSession, tenant_id: str) -> dict:
    """Fetch current inventory status with alert classification."""
    result = await db.execute(
        select(
            InventoryItem.quantity_on_hand,
            InventoryItem.reorder_point,
            InventoryItem.max_capacity,
            InventoryItem.avg_daily_consumption,
            InventoryItem.stock_status,
            Product.name.label("product_name"),
            Product.category,
        )
        .join(Product, InventoryItem.product_id == Product.id)
        .where(InventoryItem.tenant_id == tenant_id)
        .order_by(InventoryItem.quantity_on_hand.asc())
    )
    rows = result.all()

    critical = []
    low = []
    ok = 0

    for row in rows:
        daily = float(row.avg_daily_consumption or 1)
        days_left = int(row.quantity_on_hand / daily) if daily > 0 else 999
        cat = row.category.value if hasattr(row.category, "value") else str(row.category)

        if row.quantity_on_hand == 0 or days_left < 3:
            critical.append({
                "product": row.product_name,
                "category": cat,
                "quantity": row.quantity_on_hand,
                "days_until_depletion": days_left,
            })
        elif row.quantity_on_hand < row.reorder_point:
            low.append({
                "product": row.product_name,
                "category": cat,
                "quantity": row.quantity_on_hand,
                "reorder_point": row.reorder_point,
            })
        else:
            ok += 1

    return {
        "total_skus": len(rows),
        "critical_stock": critical,
        "low_stock": low,
        "healthy_count": ok,
        "requires_immediate_attention": len(critical),
    }


async def get_kpi_metrics(db: AsyncSession, tenant_id: str) -> dict:
    """Fetch month-to-date KPI metrics."""
    today = date.today()
    mtd_start = today.replace(day=1)

    mtd_result = await db.execute(
        select(
            func.sum(Sale.total_amount).label("revenue"),
            func.sum(Sale.gross_profit).label("gp"),
            func.count(Sale.id).label("orders"),
        ).where(and_(Sale.tenant_id == tenant_id, Sale.sale_date >= mtd_start))
    )
    row = mtd_result.one()
    rev = float(row.revenue or 0)
    gp = float(row.gp or 0)
    orders = int(row.orders or 0)

    alerts_count = await db.execute(
        select(func.count(Alert.id)).where(
            and_(Alert.tenant_id == tenant_id, Alert.is_read == False)  # noqa
        )
    )

    # Yesterday vs day before
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)

    y_result = await db.execute(
        select(func.sum(Sale.total_amount)).where(
            and_(Sale.tenant_id == tenant_id, Sale.sale_date == yesterday)
        )
    )
    db_result = await db.execute(
        select(func.sum(Sale.total_amount)).where(
            and_(Sale.tenant_id == tenant_id, Sale.sale_date == day_before)
        )
    )
    y_rev = float(y_result.scalar() or 0)
    db_rev = float(db_result.scalar() or 0)
    dod_change = round((y_rev - db_rev) / db_rev * 100, 1) if db_rev else 0

    return {
        "revenue_mtd": round(rev, 2),
        "gross_profit_mtd": round(gp, 2),
        "profit_margin_pct": round((gp / rev * 100) if rev else 0, 1),
        "orders_mtd": orders,
        "avg_order_value": round(rev / orders if orders else 0, 2),
        "active_alerts": int(alerts_count.scalar() or 0),
        "yesterday_revenue": round(y_rev, 2),
        "day_over_day_change_pct": dod_change,
    }


async def get_anomalies(db: AsyncSession, tenant_id: str, lookback_days: int = 30) -> dict:
    """Detect revenue anomalies using z-score method."""
    end_date = date.today()
    start_date = end_date - timedelta(days=lookback_days)

    result = await db.execute(
        select(Sale.sale_date, func.sum(Sale.total_amount).label("revenue"))
        .where(and_(Sale.tenant_id == tenant_id, Sale.sale_date >= start_date))
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date)
    )
    rows = result.all()

    if len(rows) < 7:
        return {"anomalies": [], "message": "Insufficient data for anomaly detection"}

    revenues = [float(r.revenue) for r in rows]
    import statistics

    mean = statistics.mean(revenues)
    stdev = statistics.stdev(revenues) if len(revenues) > 1 else 0

    anomalies = []
    for r in rows:
        rev = float(r.revenue)
        if stdev > 0:
            z = (rev - mean) / stdev
            if abs(z) > 2.0:
                anomalies.append({
                    "date": r.sale_date.isoformat(),
                    "revenue": round(rev, 2),
                    "expected": round(mean, 2),
                    "deviation_pct": round((rev - mean) / mean * 100, 1),
                    "z_score": round(z, 2),
                    "type": "spike" if rev > mean else "drop",
                    "severity": "critical" if abs(z) > 3.0 else "warning",
                })

    return {
        "lookback_days": lookback_days,
        "avg_daily_revenue": round(mean, 2),
        "anomalies": sorted(anomalies, key=lambda x: x["date"], reverse=True),
        "total_anomalies": len(anomalies),
    }


async def get_top_products(
    db: AsyncSession, tenant_id: str, days: int = 30
) -> dict:
    """Fetch top 5 products by revenue."""
    start_date = date.today() - timedelta(days=days)
    result = await db.execute(
        select(
            Product.name.label("product_name"),
            Product.category,
            func.sum(SaleItem.line_total).label("revenue"),
            func.sum(SaleItem.quantity).label("units"),
        )
        .join(Product, SaleItem.product_id == Product.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(and_(SaleItem.tenant_id == tenant_id, Sale.sale_date >= start_date))
        .group_by(Product.name, Product.category)
        .order_by(func.sum(SaleItem.line_total).desc())
        .limit(5)
    )
    products = [
        {
            "product": r.product_name,
            "category": r.category.value if hasattr(r.category, "value") else str(r.category),
            "revenue": round(float(r.revenue), 2),
            "units": int(r.units),
        }
        for r in result.all()
    ]
    return {"top_products": products, "period_days": days}
