import uuid
from datetime import datetime, date
from typing import Optional
from enum import Enum

from sqlalchemy import String, DateTime, Float, ForeignKey, Date, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base


class ForecastType(str, Enum):
    REVENUE = "revenue"
    INVENTORY = "inventory"
    DEMAND = "demand"


class ForecastRecord(Base):
    __tablename__ = "forecast_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    forecast_type: Mapped[ForecastType] = mapped_column(
        SAEnum(ForecastType, name="forecasttype"), nullable=False, index=True
    )
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    yhat: Mapped[float] = mapped_column(Float, nullable=False)
    yhat_lower: Mapped[float] = mapped_column(Float, nullable=False)
    yhat_upper: Mapped[float] = mapped_column(Float, nullable=False)
    trend: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    seasonality: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), default="prophet_v1", nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ForecastRecord {self.forecast_type} {self.forecast_date}: {self.yhat:.2f}>"
