import uuid
from typing import Dict, Any, Optional
from datetime import date, datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from services.sales_service import SalesService
from services.inventory_service import InventoryService
from services.analytics_service import AnalyticsService
from services.alert_service import AlertService
from schemas.ai import ReportGenerateRequest, ReportResponse


class ReportService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sales_svc = SalesService(session)
        self.inventory_svc = InventoryService(session)
        self.analytics_svc = AnalyticsService(session)
        self.alert_svc = AlertService(session)

    async def generate_report(
        self,
        tenant_id,
        request: ReportGenerateRequest,
    ) -> ReportResponse:
        today = date.today()

        if request.period_start and request.period_end:
            period_start = date.fromisoformat(request.period_start)
            period_end = date.fromisoformat(request.period_end)
        elif request.report_type == "daily":
            period_start = period_end = today - timedelta(days=1)
        elif request.report_type == "weekly":
            period_start = today - timedelta(days=7)
            period_end = today
        elif request.report_type == "monthly":
            period_start = today.replace(day=1)
            period_end = today
        elif request.report_type == "quarterly":
            q_month = ((today.month - 1) // 3) * 3 + 1
            period_start = today.replace(month=q_month, day=1)
            period_end = today
        else:
            period_start = today - timedelta(days=30)
            period_end = today

        sections: Dict[str, Any] = {}

        if "sales" in request.include_sections:
            daily = await self.sales_svc.get_daily_sales(
                tenant_id, period_start, period_end
            )
            sections["sales"] = {
                "daily_summary": [d.model_dump() for d in daily[-7:]],
                "total_revenue": sum(d.total_revenue for d in daily),
                "total_transactions": sum(d.transaction_count for d in daily),
            }

        if "inventory" in request.include_sections:
            inv_status = await self.inventory_svc.get_inventory_status(tenant_id)
            inv_alerts = await self.inventory_svc.get_inventory_alerts(tenant_id)
            sections["inventory"] = {
                "total_items": len(inv_status),
                "alerts_count": len(inv_alerts),
                "critical_alerts": sum(
                    1 for a in inv_alerts if a.severity == "critical"
                ),
                "alerts": [a.model_dump() for a in inv_alerts[:10]],
            }

        if "kpis" in request.include_sections:
            kpis = await self.analytics_svc.get_kpis(
                tenant_id, period_start, period_end
            )
            sections["kpis"] = kpis.model_dump()

        if "forecasts" in request.include_sections:
            sections["forecasts"] = {
                "note": "Forecasts available via /api/v1/forecasting endpoints"
            }

        if "alerts" in request.include_sections:
            alert_summary = await self.alert_svc.get_alert_summary(tenant_id)
            sections["alerts"] = alert_summary

        report_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        kpi_summary = sections.get("kpis", {}).get("summary", "")
        summary = (
            f"Executive Report ({request.report_type.title()}) for "
            f"{period_start} to {period_end}. {kpi_summary}"
        )

        return ReportResponse(
            report_id=report_id,
            report_type=request.report_type,
            generated_at=now,
            period_start=str(period_start),
            period_end=str(period_end),
            sections=sections,
            summary=summary,
        )
