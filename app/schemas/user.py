"""User-related schemas."""
from pydantic import field_validator
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.utils.validators import validate_username


class UserPublic(BaseModel):
    """Public representation of a user (no password or sensitive fields)."""

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"example": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "john_doe", "email": "john@example.com", "full_name": "John Doe",
        "is_active": True, "is_verified": False, "is_superuser": False,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "last_login_at": None,
    }})

    id: uuid.UUID
    username: str
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None


class UserUpdate(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"full_name": "Jane Doe"}})

    full_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None

    @field_validator("full_name")
    @classmethod
    def _strip(cls, v: str | None) -> str | None:
        return v.strip() if v else None

    @field_validator("full_name")
    @classmethod
    def _strip(cls, v: str | None) -> str | None:
        return v.strip() if v else None