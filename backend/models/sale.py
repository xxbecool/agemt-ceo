import uuid
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, index=True)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    gross_profit: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    customer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payment_method: Mapped[str] = mapped_column(String(50), default="cash", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="sales")
    branch: Mapped["Branch"] = relationship("Branch", back_populates="sales")
    items: Mapped[List["SaleItem"]] = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Sale {self.invoice_number}: ${self.total_amount:.2f}>"


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    sale_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discount_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    line_total: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    sale: Mapped["Sale"] = relationship("Sale", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="sale_items")

    def __repr__(self) -> str:
        return f"<SaleItem {self.product_id}: qty={self.quantity}>"
