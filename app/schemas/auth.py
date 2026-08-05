"""Authentication-related request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.utils.validators import validate_password_strength, validate_username


# ============================================================
# Requests
# ============================================================


class RegisterRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {
        "username": "john_doe", "email": "john@example.com", "full_name": "John Doe",
        "password": "MyStr0ng!Pass", "password_confirm": "MyStr0ng!Pass",
    }})

    username: str = Field(..., min_length=3, max_length=32, examples=["john_doe"])
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=100)
    password: str = Field(..., min_length=12, max_length=128)
    password_confirm: str

    @field_validator("username")
    @classmethod
    def _validate_username(cls, v: str) -> str:
        return validate_username(v)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v: str) -> str:
        return validate_password_strength(v)

    @field_validator("password_confirm")
    @classmethod
    def _passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {
        "identifier": "john@example.com", "password": "MyStr0ng!Pass",
    }})

    identifier: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"refresh_token": "eyJhbGciOi..."}})

    refresh_token: str = Field(..., min_length=10)


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"email": "john@example.com"}})
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {
        "token": "abc123...", "password": "NewStr0ng!Pass", "password_confirm": "NewStr0ng!Pass",
    }})

    token: str = Field(..., min_length=10)
    password: str = Field(..., min_length=12, max_length=128)
    password_confirm: str

    @field_validator("password")
    @classmethod
    def _validate(cls, v: str) -> str:
        return validate_password_strength(v)

    @field_validator("password_confirm")
    @classmethod
    def _match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {
        "current_password": "Old!Pass1", "new_password": "New!Pass1",
        "new_password_confirm": "New!Pass1",
    }})

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=12, max_length=128)
    new_password_confirm: str

    @field_validator("new_password")
    @classmethod
    def _validate(cls, v: str) -> str:
        return validate_password_strength(v)

    @field_validator("new_password_confirm")
    @classmethod
    def _match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class VerifyEmailRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"token": "abc123..."}})
    token: str = Field(..., min_length=10)


class ResendVerificationRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"email": "john@example.com"}})
    email: EmailStr


# ============================================================
# Responses
# ============================================================


class TokenResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {
        "access_token": "eyJhbGciOi...", "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g...",
        "token_type": "bearer", "expires_in": 900, "refresh_expires_in": 604800,
        "access_token_expires_at": "2024-01-15T10:45:00Z",
        "refresh_token_expires_at": "2024-01-22T10:30:00Z",
    }})

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class LogoutResponse(MessageResponse):
    pass


class LogoutAllResponse(MessageResponse):
    revoked_count: int = 0