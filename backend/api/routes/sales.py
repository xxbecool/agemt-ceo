from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, timedelta

from core.database import get_db
from api.deps import CurrentUser
from models.sale import Sale, SaleItem
from models.product import Product
from models.branch import Branch

router = APIRouter()


@router.get("/daily")
async def get_daily_sales(
    current_user: CurrentUser,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    tid = current_user.tenant_id

    result = await db.execute(
        select(
            Sale.sale_date,
            func.sum(Sale.total_amount).label("revenue"),
            func.count(Sale.id).label("orders"),
            func.sum(Sale.gross_profit).label("gross_profit"),
        )
        .where(and_(Sale.tenant_id == tid, Sale.sale_date >= start_date, Sale.sale_date <= end_date))
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date)
    )
    rows = result.all()

    data = []
    for row in rows:
        margin = (float(row.gross_profit) / float(row.revenue) * 100) if row.revenue else 0
        data.append({
            "date": row.sale_date.isoformat(),
            "revenue": round(float(row.revenue), 2),
            "orders": row.orders,
            "gross_profit": round(float(row.gross_profit), 2),
            "profit_margin": round(margin, 1),
        })

    total_revenue = sum(d["revenue"] for d in data)
    total_orders = sum(d["orders"] for d in data)
    avg_order_value = total_revenue / total_orders if total_orders else 0

    prev_start = start_date - timedelta(days=days)
    prev_result = await db.execute(
        select(func.sum(Sale.total_amount))
        .where(and_(Sale.tenant_id == tid, Sale.sale_date >= prev_start, Sale.sale_date < start_date))
    )
    prev_revenue = float(prev_result.scalar() or 0)
    growth_pct = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0

    return {
        "data": data,
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "avg_order_value": round(avg_order_value, 2),
        "revenue_growth_pct": round(growth_pct, 1),
        "period_days": days,
    }


@router.get("/monthly")
async def get_monthly_sales(
    current_user: CurrentUser,
    months: int = Query(default=12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id
    result = await db.execute(
        select(
            func.extract("year", Sale.sale_date).label("year"),
            func.extract("month", Sale.sale_date).label("month"),
            func.sum(Sale.total_amount).label("revenue"),
            func.count(Sale.id).label("orders"),
            func.sum(Sale.gross_profit).label("gross_profit"),
        )
        .where(Sale.tenant_id == tid)
        .group_by("year", "month")
        .order_by("year", "month")
        .limit(months)
    )
    rows = result.all()

    monthly = []
    prev_rev = None
    for row in rows:
        rev = float(row.revenue)
        growth = ((rev - prev_rev) / prev_rev * 100) if prev_rev else 0
        monthly.append({
            "year": int(row.year),
            "month": int(row.month),
            "revenue": round(rev, 2),
            "orders": row.orders,
            "growth_pct": round(growth, 1),
            "gross_profit": round(float(row.gross_profit), 2),
        })
        prev_rev = rev

    return {"monthly": monthly}


@router.get("/quarterly")
async def get_quarterly_sales(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id
    result = await db.execute(
        select(
            func.extract("year", Sale.sale_date).label("year"),
            func.extract("quarter", Sale.sale_date).label("quarter"),
            func.sum(Sale.total_amount).label("revenue"),
            func.count(Sale.id).label("orders"),
            func.sum(Sale.gross_profit).label("gross_profit"),
        )
        .where(Sale.tenant_id == tid)
        .group_by("year", "quarter")
        .order_by("year", "quarter")
    )
    rows = result.all()

    quarterly = []
    prev_rev = None
    for row in rows:
        rev = float(row.revenue)
        growth = ((rev - prev_rev) / prev_rev * 100) if prev_rev else 0
        quarterly.append({
            "year": int(row.year),
            "quarter": int(row.quarter),
            "revenue": round(rev, 2),
            "orders": row.orders,
            "growth_pct": round(growth, 1),
            "gross_profit": round(float(row.gross_profit), 2),
        })
        prev_rev = rev

    return {"quarterly": quarterly}


@router.get("/trends")
async def get_sales_trends(
    current_user: CurrentUser,
    period: str = Query(default="7d", pattern="^(7d|30d|90d)$"),
    db: AsyncSession = Depends(get_db),
):
    days_map = {"7d": 7, "30d": 30, "90d": 90}
    days = days_map[period]
    start_date = date.today() - timedelta(days=days)
    tid = current_user.tenant_id

    result = await db.execute(
        select(
            Sale.sale_date,
            func.sum(Sale.total_amount).label("revenue"),
            func.count(Sale.id).label("orders"),
        )
        .where(and_(Sale.tenant_id == tid, Sale.sale_date >= start_date))
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date)
    )
    data = [
        {"date": r.sale_date.isoformat(), "revenue": round(float(r.revenue), 2), "orders": r.orders}
        for r in result.all()
    ]
    return {"period": period, "data": data}


@router.get("/top-products")
async def get_top_products(
    current_user: CurrentUser,
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id
    start_date = date.today() - timedelta(days=days)

    result = await db.execute(
        select(
            SaleItem.product_id,
            Product.name.label("product_name"),
            Product.category,
            func.sum(SaleItem.line_total).label("revenue"),
            func.sum(SaleItem.quantity).label("units_sold"),
            func.sum(SaleItem.quantity * (SaleItem.unit_price - SaleItem.unit_cost)).label("gross_profit"),
        )
        .join(Product, SaleItem.product_id == Product.id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(and_(SaleItem.tenant_id == tid, Sale.sale_date >= start_date))
        .group_by(SaleItem.product_id, Product.name, Product.category)
        .order_by(func.sum(SaleItem.line_total).desc())
        .limit(limit)
    )
    rows = result.all()

    products = []
    for row in rows:
        rev = float(row.revenue)
        gp = float(row.gross_profit)
        margin = (gp / rev * 100) if rev else 0
        cat = row.category.value if hasattr(row.category, "value") else str(row.category)
        products.append({
            "product_id": str(row.product_id),
            "product_name": row.product_name,
            "category": cat,
            "revenue": round(rev, 2),
            "units_sold": row.units_sold,
            "gross_profit": round(gp, 2),
            "profit_margin": round(margin, 1),
        })

    return {"products": products, "period": f"{days}d"}


@router.get("/branch-comparison")
async def get_branch_comparison(
    current_user: CurrentUser,
    days: int = Query(default=30),
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id
    start_date = date.today() - timedelta(days=days)
    prev_start = start_date - timedelta(days=days)

    current_result = await db.execute(
        select(
            Sale.branch_id,
            Branch.name.label("branch_name"),
            func.sum(Sale.total_amount).label("revenue"),
            func.count(Sale.id).label("orders"),
        )
        .join(Branch, Sale.branch_id == Branch.id)
        .where(and_(Sale.tenant_id == tid, Sale.sale_date >= start_date))
        .group_by(Sale.branch_id, Branch.name)
        .order_by(func.sum(Sale.total_amount).desc())
    )
    current_rows = {str(r.branch_id): r for r in current_result.all()}

    prev_result = await db.execute(
        select(Sale.branch_id, func.sum(Sale.total_amount).label("revenue"))
        .where(and_(Sale.tenant_id == tid, Sale.sale_date >= prev_start, Sale.sale_date < start_date))
        .group_by(Sale.branch_id)
    )
    prev_rows = {str(r.branch_id): float(r.revenue) for r in prev_result.all()}

    branches = []
    for rank, (bid, row) in enumerate(current_rows.items(), 1):
        rev = float(row.revenue)
        prev_rev = prev_rows.get(bid, 0)
        growth = ((rev - prev_rev) / prev_rev * 100) if prev_rev else 0
        branches.append({
            "branch_id": bid,
            "branch_name": row.branch_name,
            "revenue": round(rev, 2),
            "orders": row.orders,
            "growth_pct": round(growth, 1),
            "rank": rank,
        })

    top_branch = branches[0]["branch_name"] if branches else "N/A"
    return {"branches": branches, "top_branch": top_branch, "period": f"{days}d"}
