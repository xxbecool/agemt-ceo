import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)
    current_utilization: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="warehouses")
    inventory_items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="warehouse")

    def __repr__(self) -> str:
        return f"<Warehouse {self.name}>"
