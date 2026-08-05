"""Application settings loaded from environment variables.

All settings are type-checked via Pydantic v2 and can be overridden via
environment variables or a `.env` file at the project root.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- Application ----------
    APP_NAME: str = "AuthAPI"
    APP_ENV: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ---------- Server ----------
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1, le=65535)
    WORKERS: int = Field(default=1, ge=1)

    # ---------- Security ----------
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1)
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = Field(default=1, ge=1)
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = Field(default=24, ge=1)

    # ---------- CORS ----------
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default_factory=lambda: ["*"])

    # ---------- Database ----------
    DATABASE_URL: str = Field(..., description="Async DB URL (asyncpg)")
    DATABASE_URL_SYNC: str = Field(..., description="Sync DB URL for Alembic")
    DATABASE_POOL_SIZE: int = Field(default=20, ge=1)
    DATABASE_MAX_OVERFLOW: int = Field(default=10, ge=0)
    DATABASE_ECHO: bool = False
    DATABASE_POOL_TIMEOUT: int = Field(default=30, ge=1)

    # ---------- Cookies ----------
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: Literal["strict", "lax", "none"] = "lax"
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"

    # ---------- Rate Limiting ----------
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1)
    RATE_LIMIT_LOGIN_PER_MINUTE: int = Field(default=5, ge=1)
    RATE_LIMIT_REGISTER_PER_MINUTE: int = Field(default=3, ge=1)

    # ---------- Logging ----------
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    # ---------- Email ----------
    EMAIL_FROM: str = "noreply@example.com"
    EMAIL_FROM_NAME: str = "AuthAPI"
    FRONTEND_URL: str = "http://localhost:3000"

    # ---------- Validators ----------
    @field_validator("CORS_ORIGINS", "CORS_ALLOW_METHODS", "CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def _split_csv(cls, value: str | list[str]) -> list[str]:
        """Allow list fields to be provided as comma-separated strings."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    # ---------- Computed properties ----------
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_test(self) -> bool:
        return self.APP_ENV == "test"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings (loaded once per process)."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()