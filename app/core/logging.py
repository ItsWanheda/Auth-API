"""Structured logging via structlog (JSON in prod, pretty in dev)."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.config.settings import settings


def _shared_processors() -> list[Processor]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[structlog.processors.CallsiteParameter.MODULE,
                        structlog.processors.CallsiteParameter.LINENO],
        ),
    ]


def configure_logging() -> None:
    """Configure stdlib + structlog according to settings."""
    shared = _shared_processors()
    renderer = structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" \
        else structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared,
        processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, renderer],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.LOG_LEVEL)

    for noisy in ("uvicorn.access", "sqlalchemy.engine", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str | None = None, **initial: Any) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger with optional initial context."""
    logger = structlog.get_logger(name)
    if initial:
        logger = logger.bind(**initial)
    return logger  # type: ignore[return-value]


logger = get_logger(__name__)