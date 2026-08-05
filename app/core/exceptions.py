"""Custom exceptions and standardized JSON error handlers."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


# ============================================================
# Exception classes
# ============================================================


class AppException(Exception):
    """Base application exception with HTTP semantics."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED,
                         error_code="AUTHENTICATION_FAILED", details=details)


class AuthorizationError(AppException):
    def __init__(self, message: str = "Permission denied", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN,
                         error_code="PERMISSION_DENIED", details=details)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND,
                         error_code="NOT_FOUND", details=details)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=status.HTTP_409_CONFLICT,
                         error_code="CONFLICT", details=details)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                         error_code="VALIDATION_ERROR", details=details)


class TokenError(AuthenticationError):
    def __init__(self, message: str = "Invalid or expired token", details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, details=details)
        self.error_code = "TOKEN_ERROR"


# ============================================================
# Helpers
# ============================================================


def _build_response(*, status_code: int, error_code: str, message: str,
                    details: dict[str, Any] | None = None) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {"code": error_code, "message": message, "details": details or {}},
        },
    )


# ============================================================
# Handlers
# ============================================================


async def app_exception_handler(request: Request, exc: AppException) -> ORJSONResponse:
    logger.warning("Application exception",
                   path=request.url.path, status_code=exc.status_code,
                   error_code=exc.error_code, message=exc.message)
    return _build_response(status_code=exc.status_code, error_code=exc.error_code,
                           message=exc.message, details=exc.details)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> ORJSONResponse:
    errors = [{"field": ".".join(str(loc) for loc in e["loc"]),
               "message": e["msg"], "type": e["type"]} for e in exc.errors()]
    return _build_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": errors},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> ORJSONResponse:
    return _build_response(status_code=exc.status_code,
                           error_code=f"HTTP_{exc.status_code}", message=str(exc.detail))


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> ORJSONResponse:
    logger.exception("Database error", path=request.url.path)
    if isinstance(exc, IntegrityError):
        return _build_response(status_code=status.HTTP_409_CONFLICT,
                               error_code="DATABASE_INTEGRITY_ERROR",
                               message="A database integrity error occurred")
    return _build_response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                           error_code="DATABASE_ERROR", message="A database error occurred")


async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    logger.exception("Unhandled exception", path=request.url.path, method=request.method)
    return _build_response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                           error_code="INTERNAL_ERROR", message="An internal server error occurred")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)