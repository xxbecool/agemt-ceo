from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_by_tenant(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.tenant_id == tenant_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def create_many(self, objects: List[ModelType]) -> List[ModelType]:
        for obj in objects:
            self.session.add(obj)
        await self.session.flush()
        return objects

    async def update_by_id(self, id: UUID, values: Dict[str, Any]) -> Optional[ModelType]:
        await self.session.execute(update(self.model).where(self.model.id == id).values(**values))
        return await self.get_by_id(id)

    async def delete_by_id(self, id: UUID) -> bool:
        result = await self.session.execute(delete(self.model).where(self.model.id == id))
        return result.rowcount > 0

    async def count_by_tenant(self, tenant_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(self.model).where(self.model.tenant_id == tenant_id)
        )
        return result.scalar_one()
