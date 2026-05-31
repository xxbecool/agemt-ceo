from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
import uuid

from core.database import get_db
from api.deps import CurrentUser
from models.alert import Alert

router = APIRouter()


@router.get("/")
async def get_alerts(
    current_user: CurrentUser,
    unread_only: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id
    query = select(Alert).where(Alert.tenant_id == tid)
    if unread_only:
        query = query.where(Alert.is_read == False)
    query = query.order_by(Alert.created_at.desc()).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    return {
        "alerts": [
            {
                "id": str(a.id),
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "is_read": a.is_read,
                "created_at": a.created_at.isoformat(),
            }
            for a in alerts
        ],
        "total": len(alerts),
    }


@router.patch("/{alert_id}/read")
async def mark_read(
    alert_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Alert)
        .where(and_(Alert.id == alert_id, Alert.tenant_id == current_user.tenant_id))
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "ok"}
