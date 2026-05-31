from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.product import Product, ProductCategory
from repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_by_sku(self, tenant_id: UUID, sku: str) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(
                Product.tenant_id == tenant_id, Product.sku == sku
            )
        )
        return result.scalar_one_or_none()

    async def get_by_category(
        self, tenant_id: UUID, category: ProductCategory
    ) -> List[Product]:
        result = await self.session.execute(
            select(Product).where(
                Product.tenant_id == tenant_id,
                Product.category == category,
                Product.is_active == True,  # noqa: E712
            )
        )
        return list(result.scalars().all())

    async def get_active_products(self, tenant_id: UUID) -> List[Product]:
        result = await self.session.execute(
            select(Product).where(
                Product.tenant_id == tenant_id,
                Product.is_active == True,  # noqa: E712
            ).order_by(Product.name)
        )
        return list(result.scalars().all())

    async def search_products(
        self, tenant_id: UUID, query: str, limit: int = 20
    ) -> List[Product]:
        result = await self.session.execute(
            select(Product).where(
                Product.tenant_id == tenant_id,
                Product.is_active == True,  # noqa: E712
                Product.name.ilike(f"%{query}%"),
            ).limit(limit)
        )
        return list(result.scalars().all())
