"""User repository."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import or_, select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        return (await self.session.execute(
            select(User).where(User.email == email.lower())
        )).scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        return (await self.session.execute(
            select(User).where(User.username == username)
        )).scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> User | None:
        """Identify by email if '@' present, else by username."""
        if "@" in identifier:
            return await self.get_by_email(identifier)
        return await self.get_by_username(identifier)

    async def exists_by_email(self, email: str) -> bool:
        return (await self.session.execute(
            select(User.id).where(User.email == email.lower())
        )).scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        return (await self.session.execute(
            select(User.id).where(User.username == username)
        )).scalar_one_or_none() is not None

    async def get_many(self, *, skip: int = 0, limit: int = 100,
                       active_only: bool = False) -> Sequence[User]:
        query = select(User).order_by(User.created_at.desc())
        if active_only:
            query = query.where(User.is_active.is_(True))
        return (await self.session.execute(query.offset(skip).limit(limit))).scalars().all()

    async def search(self, term: str, *, skip: int = 0, limit: int = 50) -> Sequence[User]:
        pattern = f"%{term}%"
        return (await self.session.execute(
            select(User).where(or_(
                User.username.ilike(pattern),
                User.email.ilike(pattern),
                User.full_name.ilike(pattern),
            )).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )).scalars().all()