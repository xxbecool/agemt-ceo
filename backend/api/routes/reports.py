"""
Reports routes: generate, list, and deliver executive reports.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, date, timedelta
import uuid

from core.database import get_db
from api.deps import CurrentUser
from services.report_service import ReportService
from schemas.ai import ReportGenerateRequest, ReportResponse

router = APIRouter()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    payload: ReportGenerateRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a comprehensive executive report with real data.
    Sections include: sales, inventory, KPIs, forecasts, alerts.
    """
    svc = ReportService(db)
    return await svc.generate_report(current_user.tenant_id, payload)


@router.get("/list")
async def list_reports(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return a list of available report types with metadata."""
    today = date.today()
    reports = [
        {
            "id": str(uuid.uuid4()),
            "type": "daily",
            "title": f"Daily Executive Report — {today.isoformat()}",
            "description": "Yesterday's performance vs 7-day average",
            "status": "available",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "id": str(uuid.uuid4()),
            "type": "weekly",
            "title": f"Weekly Executive Report — Week {today.isocalendar()[1]}, {today.year}",
            "description": "Last 7 days performance summary",
            "status": "available",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "id": str(uuid.uuid4()),
            "type": "monthly",
            "title": f"Monthly Executive Report — {today.strftime('%B %Y')}",
            "description": "Month-to-date performance with comparisons",
            "status": "available",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "id": str(uuid.uuid4()),
            "type": "quarterly",
            "title": f"Quarterly Report — Q{(today.month - 1) // 3 + 1} {today.year}",
            "description": "Quarter-to-date performance analysis",
            "status": "available",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    ]
    return {"reports": reports, "total": len(reports)}


@router.post("/quick/{report_type}")
async def quick_report(
    report_type: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a quick report using default settings.
    report_type: daily | weekly | monthly | quarterly
    """
    valid_types = {"daily", "weekly", "monthly", "quarterly"}
    if report_type not in valid_types:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report type. Must be one of: {', '.join(valid_types)}",
        )

    svc = ReportService(db)
    payload = ReportGenerateRequest(
        report_type=report_type,
        include_sections=["sales", "inventory", "kpis", "alerts"],
    )
    return await svc.generate_report(current_user.tenant_id, payload)
