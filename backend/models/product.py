import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Float, Integer, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class ProductCategory(str, Enum):
    ELECTRONICS = "Electronics"
    FOOD = "Food"
    CLOTHING = "Clothing"
    HEALTH = "Health"
    SPORTS = "Sports"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[ProductCategory] = mapped_column(SAEnum(ProductCategory, name="productcategory"), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    cost_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="piece", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reorder_point: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    max_stock_level: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="products")
    sale_items: Mapped[List["SaleItem"]] = relationship("SaleItem", back_populates="product")
    inventory_items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product {self.sku}: {self.name}>"
