"""Structured logging configuration built on structlog, integrated with stdlib logging."""

import logging
import sys
from typing import cast

import structlog

from app.config.settings import Settings, get_settings

_SHARED_PROCESSORS: list[structlog.types.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]


def configure_logging(settings: Settings | None = None) -> None:
    """Configure structlog and stdlib logging based on application settings.

    Renders human-readable console output in development and structured JSON otherwise, so
    logs are consistent whether emitted via structlog or third-party stdlib loggers (e.g. uvicorn).
    """
    settings = settings or get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    renderer: structlog.types.Processor = (
        structlog.dev.ConsoleRenderer()
        if settings.environment == "development"
        else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[*_SHARED_PROCESSORS, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=_SHARED_PROCESSORS,
        processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, renderer],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(level)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog-bound logger configured via `configure_logging`."""
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
