from typing import List, Optional, Tuple
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, and_
from sqlalchemy.orm import selectinload

from models.sale import Sale, SaleItem
from models.product import Product
from models.branch import Branch
from repositories.base import BaseRepository


class SalesRepository(BaseRepository[Sale]):
    def __init__(self, session: AsyncSession):
        super().__init__(Sale, session)

    async def get_daily_revenue(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
        branch_id: Optional[UUID] = None,
    ) -> List[dict]:
        filters = [
            Sale.tenant_id == tenant_id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
        ]
        if branch_id:
            filters.append(Sale.branch_id == branch_id)

        result = await self.session.execute(
            select(
                Sale.sale_date,
                func.sum(Sale.total_amount).label("total_revenue"),
                func.sum(Sale.total_cost).label("total_cost"),
                func.sum(Sale.gross_profit).label("gross_profit"),
                func.count(Sale.id).label("transaction_count"),
                func.avg(Sale.total_amount).label("avg_transaction_value"),
            )
            .where(and_(*filters))
            .group_by(Sale.sale_date)
            .order_by(Sale.sale_date)
        )
        rows = result.all()
        return [
            {
                "date": row.sale_date,
                "total_revenue": float(row.total_revenue or 0),
                "total_cost": float(row.total_cost or 0),
                "gross_profit": float(row.gross_profit or 0),
                "transaction_count": int(row.transaction_count or 0),
                "avg_transaction_value": float(row.avg_transaction_value or 0),
            }
            for row in rows
        ]

    async def get_monthly_revenue(
        self,
        tenant_id: UUID,
        year: int,
        branch_id: Optional[UUID] = None,
    ) -> List[dict]:
        filters = [
            Sale.tenant_id == tenant_id,
            func.extract("year", Sale.sale_date) == year,
        ]
        if branch_id:
            filters.append(Sale.branch_id == branch_id)

        result = await self.session.execute(
            select(
                func.extract("year", Sale.sale_date).label("year"),
                func.extract("month", Sale.sale_date).label("month"),
                func.sum(Sale.total_amount).label("total_revenue"),
                func.sum(Sale.total_cost).label("total_cost"),
                func.sum(Sale.gross_profit).label("gross_profit"),
                func.count(Sale.id).label("transaction_count"),
            )
            .where(and_(*filters))
            .group_by(
                func.extract("year", Sale.sale_date),
                func.extract("month", Sale.sale_date),
            )
            .order_by(
                func.extract("year", Sale.sale_date),
                func.extract("month", Sale.sale_date),
            )
        )
        rows = result.all()
        return [
            {
                "year": int(row.year),
                "month": int(row.month),
                "total_revenue": float(row.total_revenue or 0),
                "total_cost": float(row.total_cost or 0),
                "gross_profit": float(row.gross_profit or 0),
                "transaction_count": int(row.transaction_count or 0),
            }
            for row in rows
        ]

    async def get_top_products(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
        limit: int = 10,
    ) -> List[dict]:
        result = await self.session.execute(
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.sku,
                Product.category,
                func.sum(SaleItem.line_total).label("total_revenue"),
                func.sum(SaleItem.quantity).label("total_units_sold"),
                func.sum(
                    SaleItem.quantity * (SaleItem.unit_price - SaleItem.unit_cost)
                ).label("gross_profit"),
            )
            .join(SaleItem, Product.id == SaleItem.product_id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .where(
                Sale.tenant_id == tenant_id,
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
            )
            .group_by(Product.id, Product.name, Product.sku, Product.category)
            .order_by(func.sum(SaleItem.line_total).desc())
            .limit(limit)
        )
        rows = result.all()
        return [
            {
                "product_id": str(row.product_id),
                "product_name": row.product_name,
                "sku": row.sku,
                "category": row.category.value if hasattr(row.category, "value") else str(row.category),
                "total_revenue": float(row.total_revenue or 0),
                "total_units_sold": int(row.total_units_sold or 0),
                "gross_profit": float(row.gross_profit or 0),
            }
            for row in rows
        ]

    async def get_branch_performance(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[dict]:
        result = await self.session.execute(
            select(
                Branch.id.label("branch_id"),
                Branch.name.label("branch_name"),
                Branch.code.label("branch_code"),
                Branch.region,
                func.sum(Sale.total_amount).label("total_revenue"),
                func.sum(Sale.total_cost).label("total_cost"),
                func.sum(Sale.gross_profit).label("gross_profit"),
                func.count(Sale.id).label("transaction_count"),
            )
            .join(Sale, Branch.id == Sale.branch_id)
            .where(
                Sale.tenant_id == tenant_id,
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
            )
            .group_by(Branch.id, Branch.name, Branch.code, Branch.region)
            .order_by(func.sum(Sale.total_amount).desc())
        )
        rows = result.all()
        return [
            {
                "branch_id": str(row.branch_id),
                "branch_name": row.branch_name,
                "branch_code": row.branch_code,
                "region": row.region,
                "total_revenue": float(row.total_revenue or 0),
                "total_cost": float(row.total_cost or 0),
                "gross_profit": float(row.gross_profit or 0),
                "transaction_count": int(row.transaction_count or 0),
            }
            for row in rows
        ]

    async def get_sales_for_forecast(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[dict]:
        result = await self.session.execute(
            select(
                Sale.sale_date,
                func.sum(Sale.total_amount).label("y"),
            )
            .where(
                Sale.tenant_id == tenant_id,
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
            )
            .group_by(Sale.sale_date)
            .order_by(Sale.sale_date)
        )
        rows = result.all()
        return [{"ds": row.sale_date, "y": float(row.y or 0)} for row in rows]

    async def get_units_sold_by_date(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
    ) -> dict:
        result = await self.session.execute(
            select(
                Sale.sale_date,
                func.sum(SaleItem.quantity).label("units_sold"),
            )
            .join(SaleItem, Sale.id == SaleItem.sale_id)
            .where(
                Sale.tenant_id == tenant_id,
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
            )
            .group_by(Sale.sale_date)
        )
        return {row.sale_date: int(row.units_sold or 0) for row in result.all()}
