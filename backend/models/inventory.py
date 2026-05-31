import uuid
from datetime import datetime, date
from typing import Optional
from enum import Enum

from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Date, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class StockStatus(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    CRITICAL = "critical"
    OVERSTOCK = "overstock"
    OUT_OF_STOCK = "out_of_stock"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    quantity_on_hand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=500)
    avg_daily_consumption: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stock_status: Mapped[StockStatus] = mapped_column(
        SAEnum(StockStatus, name="stockstatus"),
        nullable=False,
        default=StockStatus.NORMAL,
    )
    last_restocked_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="inventory_items")
    product: Mapped["Product"] = relationship("Product", back_populates="inventory_items")

    def __repr__(self) -> str:
        return f"<InventoryItem product={self.product_id} qty={self.quantity_on_hand}>"
