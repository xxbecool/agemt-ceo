from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from models.alert import Alert, AlertType, AlertSeverity
from repositories.base import BaseRepository


class AlertService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_alerts(
        self,
        tenant_id: UUID,
        unread_only: bool = False,
        unresolved_only: bool = True,
        alert_type: Optional[AlertType] = None,
        severity: Optional[AlertSeverity] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Alert]:
        filters = [Alert.tenant_id == tenant_id]
        if unread_only:
            filters.append(Alert.is_read == False)  # noqa
        if unresolved_only:
            filters.append(Alert.is_resolved == False)  # noqa
        if alert_type:
            filters.append(Alert.alert_type == alert_type)
        if severity:
            filters.append(Alert.severity == severity)

        result = await self.session.execute(
            select(Alert)
            .where(and_(*filters))
            .order_by(Alert.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_alert(
        self,
        tenant_id: UUID,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Alert:
        alert = Alert(
            tenant_id=tenant_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata,
        )
        self.session.add(alert)
        await self.session.flush()
        await self.session.refresh(alert)
        return alert

    async def mark_read(self, alert_id: UUID, tenant_id: UUID) -> bool:
        result = await self.session.execute(
            update(Alert)
            .where(Alert.id == alert_id, Alert.tenant_id == tenant_id)
            .values(is_read=True)
        )
        return result.rowcount > 0

    async def mark_resolved(
        self, alert_id: UUID, tenant_id: UUID, resolved_by: str
    ) -> bool:
        result = await self.session.execute(
            update(Alert)
            .where(Alert.id == alert_id, Alert.tenant_id == tenant_id)
            .values(
                is_resolved=True,
                resolved_at=datetime.now(timezone.utc),
                resolved_by=resolved_by,
            )
        )
        return result.rowcount > 0

    async def mark_all_read(self, tenant_id: UUID) -> int:
        result = await self.session.execute(
            update(Alert)
            .where(Alert.tenant_id == tenant_id, Alert.is_read == False)  # noqa
            .values(is_read=True)
        )
        return result.rowcount

    async def get_alert_summary(self, tenant_id: UUID) -> dict:
        alerts = await self.get_alerts(tenant_id, unresolved_only=True, limit=500)
        return {
            "total_unresolved": len(alerts),
            "critical": sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL),
            "warning": sum(1 for a in alerts if a.severity == AlertSeverity.WARNING),
            "info": sum(1 for a in alerts if a.severity == AlertSeverity.INFO),
            "unread": sum(1 for a in alerts if not a.is_read),
            "by_type": {
                t.value: sum(1 for a in alerts if a.alert_type == t)
                for t in AlertType
            },
        }
