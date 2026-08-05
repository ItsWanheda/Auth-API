"""User-related business logic (registration, profile updates, password change)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate
from app.security.password import hash_password, verify_and_upgrade_password

logger = get_logger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = UserRepository(session)

    async def register(self, *, username: str, email: str,
                       password: str, full_name: str | None = None) -> User:
        """Create a new user. Raises ConflictError on duplicate email/username."""
        username = username.strip()
        email = email.lower().strip()

        if await self.repo.exists_by_email(email):
            raise ConflictError("Email already registered",
                                details={"field": "email"})
        if await self.repo.exists_by_username(username):
            raise ConflictError("Username already taken",
                                details={"field": "username"})

        user = await self.repo.create({
            "username": username,
            "email": email,
            "full_name": full_name.strip() if full_name else None,
            "hashed_password": hash_password(password),
            "is_active": True,
            "is_verified": False,
        })
        logger.info("User registered", user_id=str(user.id), username=user.username)
        return user

    async def get(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def get_by_identifier(self, identifier: str) -> User | None:
        return await self.repo.get_by_identifier(identifier.strip())

    async def update_profile(self, user: User, data: UserUpdate) -> User:
        """Update mutable profile fields. Validates email uniqueness."""
        updates: dict = {}
        if data.full_name is not None:
            updates["full_name"] = data.full_name.strip() or None

        if data.email is not None and data.email.lower() != user.email:
            new_email = data.email.lower().strip()
            existing = await self.repo.get_by_email(new_email)
            if existing and existing.id != user.id:
                raise ConflictError("Email already in use", details={"field": "email"})
            updates["email"] = new_email
            updates["is_verified"] = False  # re-verify on email change

        if not updates:
            return user

        updated = await self.repo.update(user, updates)
        logger.info("Profile updated", user_id=str(user.id), fields=list(updates))
        return updated

    async def change_password(self, user: User, *, current: str, new: str) -> None:
        ok, upgraded = verify_and_upgrade_password(current, user.hashed_password)
        if not ok:
            raise ValidationError("Current password is incorrect",
                                  details={"field": "current_password"})

        user.hashed_password = upgraded or hash_password(new)
        self.session.add(user)
        await self.session.flush()
        logger.info("Password changed", user_id=str(user.id))

    async def set_verified(self, user: User) -> User:
        user.is_verified = True
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_last_login(self, user: User) -> None:
        from app.models.base import utc_now
        user.last_login_at = utc_now()
        self.session.add(user)
        await self.session.flush()