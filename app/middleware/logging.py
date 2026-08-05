"""Structured request/response logging middleware."""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("http")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration = (time.perf_counter() - start) * 1000
            logger.exception("HTTP error",
                             method=request.method, path=request.url.path,
                             request_id=request_id, duration_ms=round(duration, 2))
            raise

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "HTTP request",
            method=request.method, path=request.url.path,
            status_code=response.status_code,
            request_id=request_id, duration_ms=round(duration, 2),
            client_ip=(request.client.host if request.client else None),
            user_agent=request.headers.get("user-agent"),
        )
        response.headers["X-Request-ID"] = request_id
        return response