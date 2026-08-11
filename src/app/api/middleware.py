"""HTTP middleware for correlation IDs and request timing."""

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.logging.context import bind_correlation_id, clear_correlation_id
from app.logging.setup import get_logger

logger = get_logger(__name__)

CORRELATION_ID_HEADER = "X-Request-ID"


async def correlation_id_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Bind a correlation ID for the request lifecycle and log request timing."""
    correlation_id = bind_correlation_id(request.headers.get(CORRELATION_ID_HEADER))
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.exception(
            "request_failed",
            method=request.method,
            path=request.url.path,
            duration_ms=round(duration_ms, 2),
        )
        clear_correlation_id()
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers[CORRELATION_ID_HEADER] = correlation_id
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
    )
    clear_correlation_id()
    return response
