"""Generic CRUD repository."""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id_: uuid.UUID) -> ModelType | None:
        return (await self.session.execute(
            select(self.model).where(self.model.id == id_)
        )).scalar_one_or_none()

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return list((await self.session.execute(
            select(self.model).order_by(self.model.created_at.desc())
            .offset(skip).limit(limit)
        )).scalars().all())

    async def count(self) -> int:
        return int((await self.session.execute(
            select(func.count()).select_from(self.model)
        )).scalar_one())

    async def create(self, obj_in: ModelType | dict[str, Any]) -> ModelType:
        obj = self.model(**obj_in) if isinstance(obj_in, dict) else obj_in
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id_: uuid.UUID) -> bool:
        result = await self.session.execute(delete(self.model).where(self.model.id == id_))
        return result.rowcount > 0