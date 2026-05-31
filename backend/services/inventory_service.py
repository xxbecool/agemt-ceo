from typing import List, Optional
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.inventory_repo import InventoryRepository
from schemas.inventory import (
    InventoryStatusResponse,
    InventoryAlertResponse,
    WarehouseUtilizationResponse,
)
from models.inventory import StockStatus
from core.config import settings


class InventoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = InventoryRepository(session)

    def _calculate_days_until_depletion(
        self, quantity: int, avg_daily_consumption: float
    ) -> Optional[float]:
        if avg_daily_consumption <= 0 or quantity <= 0:
            return None
        return round(quantity / avg_daily_consumption, 1)

    def _calculate_stock_turnover(
        self, avg_daily_consumption: float, max_capacity: int
    ) -> Optional[float]:
        """Annual stock turnover = (annual consumption) / avg_inventory."""
        if max_capacity <= 0:
            return None
        annual_consumption = avg_daily_consumption * 365
        avg_inventory = max_capacity / 2
        return round(annual_consumption / avg_inventory, 2) if avg_inventory > 0 else None

    async def get_inventory_status(
        self, tenant_id: UUID
    ) -> List[InventoryStatusResponse]:
        items = await self.repo.get_full_inventory(tenant_id)
        today = date.today()
        results = []

        for item in items:
            qty = item["quantity_on_hand"]
            max_cap = item["max_capacity"]
            avg_consumption = item["avg_daily_consumption"]

            utilization = (qty / max_cap * 100) if max_cap > 0 else 0.0
            days_depletion = self._calculate_days_until_depletion(qty, avg_consumption)
            depletion_date = (
                today + timedelta(days=int(days_depletion))
                if days_depletion is not None
                else None
            )
            turnover = self._calculate_stock_turnover(avg_consumption, max_cap)

            results.append(
                InventoryStatusResponse(
                    item_id=item["item_id"],
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    sku=item["sku"],
                    category=item["category"],
                    warehouse_id=item["warehouse_id"],
                    warehouse_name=item["warehouse_name"],
                    quantity_on_hand=qty,
                    quantity_reserved=item["quantity_reserved"],
                    quantity_available=item["quantity_available"],
                    reorder_point=item["reorder_point"],
                    max_capacity=max_cap,
                    stock_status=item["stock_status"],
                    utilization_pct=round(utilization, 2),
                    avg_daily_consumption=avg_consumption,
                    days_until_depletion=days_depletion,
                    estimated_depletion_date=depletion_date,
                    last_restocked_at=item["last_restocked_at"],
                    stock_turnover_rate=turnover,
                )
            )
        return results

    async def get_inventory_alerts(
        self, tenant_id: UUID
    ) -> List[InventoryAlertResponse]:
        items = await self.repo.get_full_inventory(tenant_id)
        alerts = []

        for item in items:
            qty = item["quantity_on_hand"]
            max_cap = item["max_capacity"]
            reorder_pt = item["reorder_point"]
            avg_consumption = item["avg_daily_consumption"]

            low_threshold = max_cap * settings.LOW_STOCK_THRESHOLD
            overstock_threshold = max_cap * settings.OVERSTOCK_THRESHOLD

            days_depletion = self._calculate_days_until_depletion(qty, avg_consumption)

            if qty == 0:
                alerts.append(
                    InventoryAlertResponse(
                        product_id=item["product_id"],
                        product_name=item["product_name"],
                        sku=item["sku"],
                        warehouse_name=item["warehouse_name"],
                        alert_type="out_of_stock",
                        severity="critical",
                        current_quantity=qty,
                        threshold_quantity=reorder_pt,
                        message=f"{item['product_name']} is OUT OF STOCK at {item['warehouse_name']}",
                        days_until_depletion=0.0,
                    )
                )
            elif qty < low_threshold:
                severity = "critical" if qty < (low_threshold * 0.5) else "warning"
                alerts.append(
                    InventoryAlertResponse(
                        product_id=item["product_id"],
                        product_name=item["product_name"],
                        sku=item["sku"],
                        warehouse_name=item["warehouse_name"],
                        alert_type="low_stock",
                        severity=severity,
                        current_quantity=qty,
                        threshold_quantity=int(low_threshold),
                        message=(
                            f"{item['product_name']} stock is critically low "
                            f"({qty} units, {round(qty/max_cap*100, 1)}% capacity) "
                            f"at {item['warehouse_name']}"
                        ),
                        days_until_depletion=days_depletion,
                    )
                )
            elif qty > overstock_threshold:
                alerts.append(
                    InventoryAlertResponse(
                        product_id=item["product_id"],
                        product_name=item["product_name"],
                        sku=item["sku"],
                        warehouse_name=item["warehouse_name"],
                        alert_type="overstock",
                        severity="info",
                        current_quantity=qty,
                        threshold_quantity=int(overstock_threshold),
                        message=(
                            f"{item['product_name']} is overstocked "
                            f"({qty} units, {round(qty/max_cap*100, 1)}% capacity) "
                            f"at {item['warehouse_name']}"
                        ),
                        days_until_depletion=days_depletion,
                    )
                )
            elif qty <= reorder_pt:
                alerts.append(
                    InventoryAlertResponse(
                        product_id=item["product_id"],
                        product_name=item["product_name"],
                        sku=item["sku"],
                        warehouse_name=item["warehouse_name"],
                        alert_type="reorder",
                        severity="warning",
                        current_quantity=qty,
                        threshold_quantity=reorder_pt,
                        message=(
                            f"{item['product_name']} has reached reorder point "
                            f"({qty} units) at {item['warehouse_name']}. Consider restocking."
                        ),
                        days_until_depletion=days_depletion,
                    )
                )

        return sorted(
            alerts,
            key=lambda x: {"critical": 0, "warning": 1, "info": 2}.get(x.severity, 3),
        )

    async def get_warehouse_utilization(
        self, tenant_id: UUID
    ) -> List[WarehouseUtilizationResponse]:
        rows = await self.repo.get_warehouse_utilization(tenant_id)
        results = []
        for r in rows:
            max_cap = r["max_capacity"]
            stock = r["current_stock_count"]
            utilization = (stock / max_cap * 100) if max_cap > 0 else 0.0
            results.append(
                WarehouseUtilizationResponse(
                    warehouse_id=r["warehouse_id"],
                    warehouse_name=r["warehouse_name"],
                    warehouse_code=r["warehouse_code"],
                    city=r["city"],
                    max_capacity=max_cap,
                    current_stock_count=stock,
                    utilization_pct=round(utilization, 2),
                    item_count=r["item_count"],
                    low_stock_items=r["low_stock_items"],
                    overstock_items=r["overstock_items"],
                    out_of_stock_items=r["out_of_stock_items"],
                )
            )
        return results
