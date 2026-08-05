"""Liveness / readiness probes."""

from __future__ import annotations

from fastapi import APIRouter, status
from sqlalchemy import text

from app.config.settings import settings
from app.dependencies.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK, summary="Liveness probe")
async def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


@router.get("/health/ready", status_code=status.HTTP_200_OK, summary="Readiness probe")
async def readiness(session: AsyncSession = Depends(get_db)) -> dict:
    await session.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}