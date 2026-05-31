import calendar
from typing import List, Optional
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.sales_repo import SalesRepository
from schemas.sales import (
    DailySalesResponse,
    MonthlySalesResponse,
    QuarterlySalesResponse,
    TopProductResponse,
    BranchPerformanceResponse,
    SalesTrendResponse,
    SalesTrendPoint,
)

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}


class SalesService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SalesRepository(session)

    async def get_daily_sales(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
        branch_id: Optional[UUID] = None,
    ) -> List[DailySalesResponse]:
        rows = await self.repo.get_daily_revenue(
            tenant_id, start_date, end_date, branch_id
        )

        # Also fetch previous period for comparison
        delta = (end_date - start_date).days + 1
        prev_start = start_date - timedelta(days=delta)
        prev_end = start_date - timedelta(days=1)
        prev_rows = await self.repo.get_daily_revenue(
            tenant_id, prev_start, prev_end, branch_id
        )
        prev_map = {r["date"]: r for r in prev_rows}

        # Units sold
        units_map = await self.repo.get_units_sold_by_date(
            tenant_id, start_date, end_date
        )

        results = []
        for r in rows:
            prev = prev_map.get(r["date"] - timedelta(days=1))
            prev_rev = prev["total_revenue"] if prev else None
            dod_change = None
            dod_pct = None
            if prev_rev and prev_rev > 0:
                dod_change = r["total_revenue"] - prev_rev
                dod_pct = (dod_change / prev_rev) * 100

            revenue = r["total_revenue"]
            cost = r["total_cost"]
            profit_margin = ((revenue - cost) / revenue * 100) if revenue > 0 else 0.0

            results.append(
                DailySalesResponse(
                    date=r["date"],
                    total_revenue=revenue,
                    total_cost=cost,
                    gross_profit=r["gross_profit"],
                    profit_margin=round(profit_margin, 2),
                    transaction_count=r["transaction_count"],
                    units_sold=units_map.get(r["date"], 0),
                    avg_transaction_value=r["avg_transaction_value"],
                    prev_day_revenue=prev_rev,
                    day_over_day_change=dod_change,
                    day_over_day_change_pct=round(dod_pct, 2) if dod_pct is not None else None,
                )
            )
        return results

    async def get_monthly_sales(
        self,
        tenant_id: UUID,
        year: int,
        branch_id: Optional[UUID] = None,
    ) -> List[MonthlySalesResponse]:
        current_year_rows = await self.repo.get_monthly_revenue(
            tenant_id, year, branch_id
        )
        prev_year_rows = await self.repo.get_monthly_revenue(
            tenant_id, year - 1, branch_id
        )
        prev_year_map = {r["month"]: r for r in prev_year_rows}
        current_map = {r["month"]: r for r in current_year_rows}

        results = []
        for i, r in enumerate(current_year_rows):
            month_num = r["month"]
            # Month over month: compare to previous month
            if i > 0:
                prev_month_data = current_year_rows[i - 1]
                prev_rev = prev_month_data["total_revenue"]
            else:
                prev_rev = None

            mom_pct = None
            if prev_rev and prev_rev > 0:
                mom_pct = ((r["total_revenue"] - prev_rev) / prev_rev) * 100

            # Year over year
            prev_year_data = prev_year_map.get(month_num)
            yoy_pct = None
            if prev_year_data and prev_year_data["total_revenue"] > 0:
                yoy_pct = (
                    (r["total_revenue"] - prev_year_data["total_revenue"])
                    / prev_year_data["total_revenue"]
                ) * 100

            revenue = r["total_revenue"]
            cost = r["total_cost"]
            profit_margin = ((revenue - cost) / revenue * 100) if revenue > 0 else 0.0

            results.append(
                MonthlySalesResponse(
                    year=r["year"],
                    month=month_num,
                    month_name=MONTH_NAMES[month_num],
                    total_revenue=revenue,
                    total_cost=cost,
                    gross_profit=r["gross_profit"],
                    profit_margin=round(profit_margin, 2),
                    transaction_count=r["transaction_count"],
                    units_sold=0,  # filled below if needed
                    prev_month_revenue=prev_rev,
                    month_over_month_growth_pct=round(mom_pct, 2) if mom_pct is not None else None,
                    year_over_year_growth_pct=round(yoy_pct, 2) if yoy_pct is not None else None,
                )
            )
        return results

    async def get_quarterly_sales(
        self,
        tenant_id: UUID,
        year: int,
    ) -> List[QuarterlySalesResponse]:
        monthly = await self.get_monthly_sales(tenant_id, year)

        quarters: dict[int, list] = {1: [], 2: [], 3: [], 4: []}
        for m in monthly:
            q = (m.month - 1) // 3 + 1
            quarters[q].append(m)

        results = []
        for q_num, months in quarters.items():
            if not months:
                continue
            total_rev = sum(m.total_revenue for m in months)
            total_cost = sum(m.total_cost for m in months)
            total_profit = sum(m.gross_profit for m in months)
            total_tx = sum(m.transaction_count for m in months)
            margin = ((total_rev - total_cost) / total_rev * 100) if total_rev > 0 else 0.0

            results.append(
                QuarterlySalesResponse(
                    year=year,
                    quarter=q_num,
                    quarter_label=f"Q{q_num} {year}",
                    total_revenue=total_rev,
                    total_cost=total_cost,
                    gross_profit=total_profit,
                    profit_margin=round(margin, 2),
                    transaction_count=total_tx,
                    months=months,
                )
            )
        return results

    async def get_top_products(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
        limit: int = 10,
    ) -> List[TopProductResponse]:
        rows = await self.repo.get_top_products(tenant_id, start_date, end_date, limit)
        total_rev = sum(r["total_revenue"] for r in rows) or 1
        results = []
        for i, r in enumerate(rows, 1):
            rev = r["total_revenue"]
            profit = r["gross_profit"]
            margin = (profit / rev * 100) if rev > 0 else 0.0
            results.append(
                TopProductResponse(
                    product_id=r["product_id"],
                    product_name=r["product_name"],
                    sku=r["sku"],
                    category=r["category"],
                    total_revenue=rev,
                    total_units_sold=r["total_units_sold"],
                    gross_profit=profit,
                    profit_margin=round(margin, 2),
                    rank=i,
                )
            )
        return results

    async def get_branch_performance(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[BranchPerformanceResponse]:
        rows = await self.repo.get_branch_performance(tenant_id, start_date, end_date)
        total_rev = sum(r["total_revenue"] for r in rows) or 1

        # Previous period for growth
        delta = (end_date - start_date).days + 1
        prev_start = start_date - timedelta(days=delta)
        prev_end = start_date - timedelta(days=1)
        prev_rows = await self.repo.get_branch_performance(
            tenant_id, prev_start, prev_end
        )
        prev_map = {r["branch_id"]: r for r in prev_rows}

        results = []
        for i, r in enumerate(rows, 1):
            rev = r["total_revenue"]
            cost = r["total_cost"]
            profit = r["gross_profit"]
            margin = ((rev - cost) / rev * 100) if rev > 0 else 0.0
            share = (rev / total_rev) * 100
            prev = prev_map.get(r["branch_id"])
            growth = None
            if prev and prev["total_revenue"] > 0:
                growth = ((rev - prev["total_revenue"]) / prev["total_revenue"]) * 100

            results.append(
                BranchPerformanceResponse(
                    branch_id=r["branch_id"],
                    branch_name=r["branch_name"],
                    branch_code=r["branch_code"],
                    region=r["region"],
                    total_revenue=rev,
                    total_cost=cost,
                    gross_profit=profit,
                    profit_margin=round(margin, 2),
                    transaction_count=r["transaction_count"],
                    units_sold=0,
                    revenue_share_pct=round(share, 2),
                    growth_pct=round(growth, 2) if growth is not None else None,
                )
            )
        return results

    async def get_sales_trend(
        self,
        tenant_id: UUID,
        period: str = "30d",
        branch_id: Optional[UUID] = None,
    ) -> SalesTrendResponse:
        today = date.today()
        days = {"7d": 7, "30d": 30, "90d": 90, "365d": 365}.get(period, 30)
        start_date = today - timedelta(days=days - 1)

        rows = await self.repo.get_daily_revenue(
            tenant_id, start_date, today, branch_id
        )
        units_map = await self.repo.get_units_sold_by_date(
            tenant_id, start_date, today
        )

        data_points = [
            SalesTrendPoint(
                date=r["date"],
                revenue=r["total_revenue"],
                transactions=r["transaction_count"],
                units=units_map.get(r["date"], 0),
            )
            for r in rows
        ]

        total_rev = sum(p.revenue for p in data_points)
        avg_daily = total_rev / len(data_points) if data_points else 0.0
        peak = max(data_points, key=lambda x: x.revenue, default=None)

        return SalesTrendResponse(
            period=period,
            data_points=data_points,
            total_revenue=total_rev,
            avg_daily_revenue=avg_daily,
            peak_day=peak.date if peak else None,
            peak_revenue=peak.revenue if peak else None,
        )
