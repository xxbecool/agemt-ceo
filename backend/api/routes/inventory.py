from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from core.database import get_db
from core.config import settings
from api.deps import CurrentUser
from models.inventory import InventoryItem
from models.product import Product
from models.warehouse import Warehouse
from models.alert import Alert

router = APIRouter()


@router.get("/status")
async def get_inventory_status(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id

    result = await db.execute(
        select(
            InventoryItem.id,
            InventoryItem.product_id,
            InventoryItem.warehouse_id,
            InventoryItem.quantity_on_hand,
            InventoryItem.reorder_point,
            InventoryItem.max_capacity,
            InventoryItem.avg_daily_consumption,
            InventoryItem.updated_at,
            Product.name.label("product_name"),
            Product.sku,
            Product.category,
            Warehouse.name.label("warehouse_name"),
        )
        .join(Product, InventoryItem.product_id == Product.id)
        .join(Warehouse, InventoryItem.warehouse_id == Warehouse.id)
        .where(InventoryItem.tenant_id == tid)
        .order_by(InventoryItem.quantity_on_hand.asc())
    )
    rows = result.all()

    items = []
    low_count = critical_count = overstock_count = healthy_count = 0
    for row in rows:
        qty = row.quantity_on_hand
        util_pct = (qty / row.max_capacity * 100) if row.max_capacity else 0
        daily = float(row.avg_daily_consumption or 1)
        days_left = int(qty / daily) if daily > 0 else None

        if qty == 0:
            status = "critical"
            critical_count += 1
        elif util_pct < settings.LOW_STOCK_THRESHOLD * 100:
            status = "low"
            low_count += 1
        elif util_pct > settings.OVERSTOCK_THRESHOLD * 100:
            status = "overstock"
            overstock_count += 1
        else:
            status = "ok"
            healthy_count += 1

        cat = row.category.value if hasattr(row.category, "value") else str(row.category)
        items.append({
            "product_id": str(row.product_id),
            "product_name": row.product_name,
            "sku": row.sku,
            "category": cat,
            "warehouse_id": str(row.warehouse_id),
            "warehouse_name": row.warehouse_name,
            "quantity": qty,
            "reorder_point": row.reorder_point,
            "max_capacity": row.max_capacity,
            "utilization_pct": round(util_pct, 1),
            "status": status,
            "avg_daily_consumption": round(daily, 2),
            "days_until_depletion": days_left,
            "last_updated": row.updated_at.isoformat() if row.updated_at else None,
        })

    return {
        "items": items,
        "total_products": len(items),
        "low_stock_count": low_count,
        "critical_count": critical_count,
        "overstock_count": overstock_count,
        "healthy_count": healthy_count,
    }


@router.get("/alerts")
async def get_inventory_alerts(
    current_user: CurrentUser,
    severity: str = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id
    query = select(Alert).where(
        and_(
            Alert.tenant_id == tid,
            Alert.alert_type.in_(["low_stock", "critical_stock", "overstock"]),
        )
    )
    if severity:
        query = query.where(Alert.severity == severity)
    query = query.order_by(Alert.created_at.desc()).limit(50)

    result = await db.execute(query)
    alerts = result.scalars().all()

    alert_list = [
        {
            "alert_id": str(a.id),
            "alert_type": a.alert_type.value if hasattr(a.alert_type, "value") else str(a.alert_type),
            "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
            "message": a.message,
            "metadata": a.metadata_json,
            "created_at": a.created_at.isoformat(),
            "is_read": a.is_read,
        }
        for a in alerts
    ]

    critical = sum(1 for a in alert_list if a["severity"] == "critical")
    warning = sum(1 for a in alert_list if a["severity"] == "warning")

    return {"alerts": alert_list, "total": len(alert_list), "critical": critical, "warning": warning}


@router.get("/warehouses")
async def get_warehouse_utilization(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id
    result = await db.execute(
        select(
            Warehouse.id,
            Warehouse.name.label("warehouse_name"),
            Warehouse.city.label("location"),
            func.sum(InventoryItem.quantity_on_hand).label("used_capacity"),
            func.sum(InventoryItem.max_capacity).label("total_capacity"),
            func.count(InventoryItem.id).label("product_count"),
        )
        .join(InventoryItem, InventoryItem.warehouse_id == Warehouse.id)
        .where(Warehouse.tenant_id == tid)
        .group_by(Warehouse.id, Warehouse.name, Warehouse.city)
    )
    rows = result.all()

    warehouses = []
    for row in rows:
        total = int(row.total_capacity or 1)
        used = int(row.used_capacity or 0)
        util_pct = (used / total * 100) if total else 0
        warehouses.append({
            "warehouse_id": str(row.id),
            "warehouse_name": row.warehouse_name,
            "location": row.location or "",
            "total_capacity": total,
            "used_capacity": used,
            "utilization_pct": round(util_pct, 1),
            "product_count": row.product_count,
        })

    overall = sum(w["utilization_pct"] for w in warehouses) / len(warehouses) if warehouses else 0
    return {"warehouses": warehouses, "total_utilization_pct": round(overall, 1)}
