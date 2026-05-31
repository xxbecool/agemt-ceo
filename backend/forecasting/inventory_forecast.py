from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.inventory import InventoryItem
from models.product import Product


class InventoryForecast:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def predict(self) -> dict:
        result = await self.db.execute(
            select(
                InventoryItem.product_id,
                InventoryItem.quantity_on_hand,
                InventoryItem.reorder_point,
                InventoryItem.avg_daily_consumption,
                Product.name.label("product_name"),
                Product.sku,
            )
            .join(Product, InventoryItem.product_id == Product.id)
            .where(InventoryItem.tenant_id == self.tenant_id)
            .order_by(InventoryItem.quantity_on_hand.asc())
        )
        rows = result.all()

        items = []
        critical_count = 0
        reorder_required = 0

        for row in rows:
            daily = float(row.avg_daily_consumption or 1)
            qty = row.quantity_on_hand
            days_remaining = int(qty / daily) if daily > 0 else None
            depletion_date = (
                (date.today() + timedelta(days=days_remaining)).isoformat()
                if days_remaining is not None
                else None
            )
            reorder = qty <= row.reorder_point
            recommended_qty = max(0, int(row.reorder_point * 2 - qty))

            if days_remaining is not None and days_remaining < 7:
                critical_count += 1
            if reorder:
                reorder_required += 1

            items.append({
                "product_id": str(row.product_id),
                "product_name": row.product_name,
                "sku": row.sku,
                "current_stock": qty,
                "avg_daily_consumption": round(daily, 2),
                "predicted_depletion_date": depletion_date,
                "days_remaining": days_remaining,
                "reorder_recommended": reorder,
                "recommended_order_qty": recommended_qty,
            })

        return {
            "items": items,
            "critical_items": critical_count,
            "reorder_required": reorder_required,
        }
