"""Miscellaneous helpers (token generation, hashing)."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone


def generate_secure_token(length: int = 32) -> str:
    """Cryptographically secure URL-safe token."""
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """SHA-256 hex hash of a token (used for opaque-token storage)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)