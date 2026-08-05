"""Shared API response schemas."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standardized success envelope: `{success, data, meta}`."""

    model_config = ConfigDict(json_schema_extra={"example": {"success": True, "data": {}}})

    success: bool = True
    data: T
    meta: dict[str, Any] | None = None


class ErrorDetail(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {
        "code": "VALIDATION_ERROR", "message": "Request validation failed", "details": {},
    }})

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {
        "success": False,
        "error": {"code": "VALIDATION_ERROR", "message": "...", "details": {}},
    }})

    success: bool = False
    error: ErrorDetail


class PaginationMeta(BaseModel):
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)
    has_next: bool
    has_prev: bool