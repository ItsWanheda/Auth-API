"""Opaque token generation for password reset & email verification."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.config.settings import settings
from app.utils.helpers import generate_secure_token, hash_token


def hash_refresh_token(token: str) -> str:
    """SHA-256 hash a refresh token for storage."""
    return hash_token(token)


def create_password_reset_token(user_id: uuid.UUID) -> tuple[str, str, datetime]:
    raw = generate_secure_token(32)
    return raw, hash_token(raw), datetime.now(timezone.utc) + timedelta(
        hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)


def create_email_verification_token(user_id: uuid.UUID) -> tuple[str, str, datetime]:
    raw = generate_secure_token(32)
    return raw, hash_token(raw), datetime.now(timezone.utc) + timedelta(
        hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)