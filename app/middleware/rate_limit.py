"""Simple in-memory token-bucket rate limiter.

Production note: replace the in-memory store with Redis (e.g. via
`slowapi` or `aiocache`) when running more than one worker.
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from collections.abc import MutableMapping

from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings
from app.core.exceptions import _build_response  # noqa: SLF001  (internal helper)


class _Bucket:
    __slots__ = ("tokens", "last_refill")

    def __init__(self, capacity: int) -> None:
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP sliding-window limiter with path-based buckets."""

    def __init__(self, app, default_per_min: int | None = None) -> None:
        super().__init__(app)
        self.default_per_min = default_per_min or settings.RATE_LIMIT_PER_MINUTE
        self.buckets: MutableMapping[str, _Bucket] = defaultdict(
            lambda: _Bucket(self.default_per_min))
        self._lock = asyncio.Lock()

    @staticmethod
    def _client_key(request: Request) -> str:
        fwd = request.headers.get("x-forwarded-for")
        if fwd:
            return fwd.split(",").strip()
        return request.client.host if request.client else "unknown"

    def _capacity_for(self, path: str) -> int:
        if path.startswith("/api/v1/auth/login"):
            return settings.RATE_LIMIT_LOGIN_PER_MINUTE
        if path.startswith("/api/v1/auth/register"):
            return settings.RATE_LIMIT_REGISTER_PER_MINUTE
        return self.default_per_min

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED or request.url.path in {"/health", "/docs", "/openapi.json"}:
            return await call_next(request)

        key = f"{self._client_key(request)}:{request.url.path}"
        capacity = self._capacity_for(request.url.path)
        now = time.monotonic()

        async with self._lock:
            bucket = self.buckets[key]
            elapsed = now - bucket.last_refill
            bucket.tokens = min(capacity, bucket.tokens + elapsed * (capacity / 60.0))
            bucket.last_refill = now
            if bucket.tokens < 1:
                retry_after = int((1 - bucket.tokens) * 60 / capacity) + 1
                return _build_response(
                    status_code=429, error_code="RATE_LIMIT_EXCEEDED",
                    message="Too many requests",
                    details={"retry_after_seconds": retry_after},
                )
            bucket.tokens -= 1

        return await call_next(request)