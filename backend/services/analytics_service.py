from typing import List, Optional
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from models.sale import Sale, SaleItem
from models.product import Product
from models.branch import Branch
from repositories.sales_repo import SalesRepository
from schemas.analytics import (
    KPIResponse,
    KPIMetric,
    BranchComparisonResponse,
    BranchComparisonMetric,
    ProductPerformanceResponse,
    ProductPerformanceMetric,
    AnomalyDetectionResponse,
)


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SalesRepository(session)

    async def get_kpis(
        self,
        tenant_id: UUID,
        period_start: date,
        period_end: date,
    ) -> KPIResponse:
        # Current period aggregates
        rows = await self.repo.get_daily_revenue(tenant_id, period_start, period_end)
        total_rev = sum(r["total_revenue"] for r in rows)
        total_cost = sum(r["total_cost"] for r in rows)
        total_profit = sum(r["gross_profit"] for r in rows)
        total_tx = sum(r["transaction_count"] for r in rows)
        avg_tx_val = total_rev / total_tx if total_tx > 0 else 0.0
        margin = (total_profit / total_rev * 100) if total_rev > 0 else 0.0

        # Previous period
        delta_days = (period_end - period_start).days + 1
        prev_start = period_start - timedelta(days=delta_days)
        prev_end = period_start - timedelta(days=1)
        prev_rows = await self.repo.get_daily_revenue(tenant_id, prev_start, prev_end)
        prev_rev = sum(r["total_revenue"] for r in prev_rows)
        prev_profit = sum(r["gross_profit"] for r in prev_rows)
        prev_tx = sum(r["transaction_count"] for r in prev_rows)

        def _pct_change(current, prev):
            if prev and prev > 0:
                return round((current - prev) / prev * 100, 2)
            return None

        def _trend(pct):
            if pct is None:
                return "stable"
            return "up" if pct > 0 else "down" if pct < 0 else "stable"

        rev_change = _pct_change(total_rev, prev_rev)
        profit_change = _pct_change(total_profit, prev_profit)
        tx_change = _pct_change(total_tx, prev_tx)

        metrics = [
            KPIMetric(
                name="Total Revenue",
                value=round(total_rev, 2),
                unit="USD",
                previous_value=round(prev_rev, 2) if prev_rev else None,
                change_pct=rev_change,
                trend=_trend(rev_change),
            ),
            KPIMetric(
                name="Gross Profit",
                value=round(total_profit, 2),
                unit="USD",
                previous_value=round(prev_profit, 2) if prev_profit else None,
                change_pct=profit_change,
                trend=_trend(profit_change),
            ),
            KPIMetric(
                name="Profit Margin",
                value=round(margin, 2),
                unit="%",
                previous_value=None,
            ),
            KPIMetric(
                name="Total Transactions",
                value=total_tx,
                unit="count",
                previous_value=prev_tx if prev_tx else None,
                change_pct=tx_change,
                trend=_trend(tx_change),
            ),
            KPIMetric(
                name="Avg Transaction Value",
                value=round(avg_tx_val, 2),
                unit="USD",
            ),
            KPIMetric(
                name="Daily Revenue (Avg)",
                value=round(total_rev / delta_days, 2) if delta_days > 0 else 0,
                unit="USD",
            ),
        ]

        summary = (
            f"Revenue: ${total_rev:,.0f} "
            f"({'▲' if rev_change and rev_change > 0 else '▼'}{abs(rev_change or 0):.1f}% vs prior period). "
            f"Gross profit: ${total_profit:,.0f} at {margin:.1f}% margin."
        )

        return KPIResponse(
            period_start=period_start,
            period_end=period_end,
            metrics=metrics,
            summary=summary,
        )

    async def get_branch_comparison(
        self,
        tenant_id: UUID,
        period_start: date,
        period_end: date,
    ) -> BranchComparisonResponse:
        rows = await self.repo.get_branch_performance(tenant_id, period_start, period_end)
        total_rev = sum(r["total_revenue"] for r in rows) or 1

        delta = (period_end - period_start).days + 1
        prev_start = period_start - timedelta(days=delta)
        prev_end = period_start - timedelta(days=1)
        prev_rows = await self.repo.get_branch_performance(
            tenant_id, prev_start, prev_end
        )
        prev_map = {r["branch_id"]: r for r in prev_rows}

        branches = []
        for i, r in enumerate(rows, 1):
            rev = r["total_revenue"]
            cost = r["total_cost"]
            profit = r["gross_profit"]
            tx = r["transaction_count"]
            margin = ((rev - cost) / rev * 100) if rev > 0 else 0.0
            avg_tx = rev / tx if tx > 0 else 0.0
            prev = prev_map.get(r["branch_id"])
            growth = None
            if prev and prev["total_revenue"] > 0:
                growth = round(
                    (rev - prev["total_revenue"]) / prev["total_revenue"] * 100, 2
                )

            branches.append(
                BranchComparisonMetric(
                    branch_id=r["branch_id"],
                    branch_name=r["branch_name"],
                    region=r["region"],
                    revenue=rev,
                    gross_profit=profit,
                    profit_margin=round(margin, 2),
                    transaction_count=tx,
                    avg_transaction_value=round(avg_tx, 2),
                    growth_pct=growth,
                    rank=i,
                )
            )

        top_branch = branches[0].branch_name if branches else None

        return BranchComparisonResponse(
            period_start=period_start,
            period_end=period_end,
            branches=branches,
            top_branch=top_branch,
            total_revenue=sum(r["total_revenue"] for r in rows),
        )

    async def get_product_performance(
        self,
        tenant_id: UUID,
        period_start: date,
        period_end: date,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> ProductPerformanceResponse:
        rows = await self.repo.get_top_products(tenant_id, period_start, period_end, limit)
        if category:
            rows = [r for r in rows if r["category"].lower() == category.lower()]

        total_rev = sum(r["total_revenue"] for r in rows) or 1
        total_units = sum(r["total_units_sold"] for r in rows)

        # Previous period
        delta = (period_end - period_start).days + 1
        prev_start = period_start - timedelta(days=delta)
        prev_end = period_start - timedelta(days=1)
        prev_rows = await self.repo.get_top_products(
            tenant_id, prev_start, prev_end, limit * 2
        )
        prev_map = {r["product_id"]: r for r in prev_rows}

        products = []
        for i, r in enumerate(rows, 1):
            rev = r["total_revenue"]
            profit = r["gross_profit"]
            units = r["total_units_sold"]
            cost = rev - profit
            margin = (profit / rev * 100) if rev > 0 else 0.0
            contrib = (rev / total_rev * 100)
            prev = prev_map.get(r["product_id"])
            growth = None
            if prev and prev["total_revenue"] > 0:
                growth = round(
                    (rev - prev["total_revenue"]) / prev["total_revenue"] * 100, 2
                )

            products.append(
                ProductPerformanceMetric(
                    product_id=r["product_id"],
                    product_name=r["product_name"],
                    sku=r["sku"],
                    category=r["category"],
                    units_sold=units,
                    revenue=rev,
                    cost=cost,
                    gross_profit=profit,
                    profit_margin=round(margin, 2),
                    revenue_contribution_pct=round(contrib, 2),
                    growth_pct=growth,
                    rank=i,
                )
            )

        return ProductPerformanceResponse(
            period_start=period_start,
            period_end=period_end,
            category=category,
            products=products,
            total_revenue=sum(r["total_revenue"] for r in rows),
            total_units_sold=total_units,
        )

    async def detect_anomalies(
        self,
        tenant_id: UUID,
        lookback_days: int = 30,
    ) -> List[AnomalyDetectionResponse]:
        """Simple z-score based anomaly detection on daily revenue."""
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days)
        rows = await self.repo.get_daily_revenue(tenant_id, start_date, end_date)

        if len(rows) < 7:
            return []

        revenues = [r["total_revenue"] for r in rows]
        import statistics
        mean = statistics.mean(revenues)
        stdev = statistics.stdev(revenues) if len(revenues) > 1 else 0

        anomalies = []
        for r in rows:
            rev = r["total_revenue"]
            if stdev > 0:
                z = (rev - mean) / stdev
                if abs(z) > 2.0:
                    deviation_pct = ((rev - mean) / mean * 100) if mean > 0 else 0
                    severity = "critical" if abs(z) > 3.0 else "warning"
                    direction = "spike" if rev > mean else "drop"
                    anomalies.append(
                        AnomalyDetectionResponse(
                            detected_at=r["date"],
                            metric="daily_revenue",
                            expected_value=round(mean, 2),
                            actual_value=round(rev, 2),
                            deviation_pct=round(deviation_pct, 2),
                            severity=severity,
                            description=(
                                f"Revenue {direction} detected: ${rev:,.0f} vs expected ${mean:,.0f} "
                                f"(z-score: {z:.2f})"
                            ),
                        )
                    )

        return sorted(anomalies, key=lambda x: x.detected_at, reverse=True)
