"""Factory dependencies for services."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.services.auth import AuthService
from app.services.email import EmailService
from app.services.token import TokenService
from app.services.user import UserService


def get_user_service(session: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(session)


def get_token_service(session: Annotated[AsyncSession, Depends(get_db)]) -> TokenService:
    return TokenService(session)


def get_auth_service(session: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    return AuthService(session)


def get_email_service() -> EmailService:
    # Stateless; could be made singleton later.
    return EmailService()