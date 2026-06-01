from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from models.inventory import InventoryItem, StockStatus
from models.product import Product
from models.warehouse import Warehouse
from repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryItem]):
    def __init__(self, session: AsyncSession):
        super().__init__(InventoryItem, session)

    async def get_full_inventory(self, tenant_id: UUID) -> List[dict]:
        result = await self.session.execute(
            select(
                InventoryItem.id,
                InventoryItem.quantity_on_hand,
                InventoryItem.quantity_reserved,
                InventoryItem.quantity_available,
                InventoryItem.reorder_point,
                InventoryItem.max_capacity,
                InventoryItem.avg_daily_consumption,
                InventoryItem.stock_status,
                InventoryItem.last_restocked_at,
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.sku,
                Product.category,
                Warehouse.id.label("warehouse_id"),
                Warehouse.name.label("warehouse_name"),
            )
            .join(Product, InventoryItem.product_id == Product.id)
            .join(Warehouse, InventoryItem.warehouse_id == Warehouse.id)
            .where(InventoryItem.tenant_id == tenant_id)
            .order_by(Product.name)
        )
        rows = result.all()
        return [
            {
                "item_id": str(row.id),
                "product_id": str(row.product_id),
                "product_name": row.product_name,
                "sku": row.sku,
                "category": row.category.value if hasattr(row.category, "value") else str(row.category),
                "warehouse_id": str(row.warehouse_id),
                "warehouse_name": row.warehouse_name,
                "quantity_on_hand": row.quantity_on_hand,
                "quantity_reserved": row.quantity_reserved,
                "quantity_available": row.quantity_available,
                "reorder_point": row.reorder_point,
                "max_capacity": row.max_capacity,
                "avg_daily_consumption": float(row.avg_daily_consumption or 0),
                "stock_status": row.stock_status,
                "last_restocked_at": row.last_restocked_at,
            }
            for row in rows
        ]

    async def get_low_stock_items(self, tenant_id: UUID) -> List[dict]:
        result = await self.session.execute(
            select(
                InventoryItem,
                Product.name.label("product_name"),
                Product.sku,
                Warehouse.name.label("warehouse_name"),
            )
            .join(Product, InventoryItem.product_id == Product.id)
            .join(Warehouse, InventoryItem.warehouse_id == Warehouse.id)
            .where(
                InventoryItem.tenant_id == tenant_id,
                InventoryItem.stock_status.in_(
                    [StockStatus.LOW, StockStatus.CRITICAL, StockStatus.OUT_OF_STOCK]
                ),
            )
            .order_by(InventoryItem.quantity_on_hand)
        )
        rows = result.all()
        return [
            {
                "item": row.InventoryItem,
                "product_name": row.product_name,
                "sku": row.sku,
                "warehouse_name": row.warehouse_name,
            }
            for row in rows
        ]

    async def get_warehouse_utilization(self, tenant_id: UUID) -> List[dict]:
        result = await self.session.execute(
            select(
                Warehouse.id.label("warehouse_id"),
                Warehouse.name.label("warehouse_name"),
                Warehouse.code.label("warehouse_code"),
                Warehouse.city,
                Warehouse.max_capacity,
                func.count(InventoryItem.id).label("item_count"),
                func.sum(InventoryItem.quantity_on_hand).label("total_stock"),
                func.sum(
                    func.case(
                        (InventoryItem.stock_status == StockStatus.LOW, 1),
                        (InventoryItem.stock_status == StockStatus.CRITICAL, 1),
                        else_=0,
                    )
                ).label("low_stock_items"),
                func.sum(
                    func.case(
                        (InventoryItem.stock_status == StockStatus.OVERSTOCK, 1),
                        else_=0,
                    )
                ).label("overstock_items"),
                func.sum(
                    func.case(
                        (InventoryItem.stock_status == StockStatus.OUT_OF_STOCK, 1),
                        else_=0,
                    )
                ).label("out_of_stock_items"),
            )
            .outerjoin(
                InventoryItem,
                and_(
                    Warehouse.id == InventoryItem.warehouse_id,
                    InventoryItem.tenant_id == tenant_id,
                ),
            )
            .where(Warehouse.tenant_id == tenant_id)
            .group_by(
                Warehouse.id,
                Warehouse.name,
                Warehouse.code,
                Warehouse.city,
                Warehouse.max_capacity,
            )
        )
        rows = result.all()
        return [
            {
                "warehouse_id": str(row.warehouse_id),
                "warehouse_name": row.warehouse_name,
                "warehouse_code": row.warehouse_code,
                "city": row.city,
                "max_capacity": row.max_capacity,
                "item_count": int(row.item_count or 0),
                "current_stock_count": int(row.total_stock or 0),
                "low_stock_items": int(row.low_stock_items or 0),
                "overstock_items": int(row.overstock_items or 0),
                "out_of_stock_items": int(row.out_of_stock_items or 0),
            }
            for row in rows
        ]

    async def get_item_by_product_warehouse(
        self, tenant_id: UUID, product_id: UUID, warehouse_id: UUID
    ) -> Optional[InventoryItem]:
        result = await self.session.execute(
            select(InventoryItem).where(
                InventoryItem.tenant_id == tenant_id,
                InventoryItem.product_id == product_id,
                InventoryItem.warehouse_id == warehouse_id,
            )
        )
        return result.scalar_one_or_none()
