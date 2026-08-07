"""Request-scoped correlation ID context, backed by structlog's contextvars support."""

import uuid

import structlog


def generate_correlation_id() -> str:
    """Generate a new random correlation ID."""
    return uuid.uuid4().hex


def bind_correlation_id(correlation_id: str | None = None) -> str:
    """Bind a correlation ID to the current logging context, generating one if omitted."""
    correlation_id = correlation_id or generate_correlation_id()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    return correlation_id


def clear_correlation_id() -> None:
    """Remove the correlation ID from the current logging context, if any."""
    structlog.contextvars.unbind_contextvars("correlation_id")
