"""FastAPI exception handlers that translate errors into safe HTTP responses."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError, NotFoundError, ValidationError
from app.logging.setup import get_logger

logger = get_logger(__name__)

_STATUS_CODE_BY_ERROR: dict[type[AppError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Map known application errors to their corresponding HTTP status codes."""
    assert isinstance(exc, AppError)
    status_code = _STATUS_CODE_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)

    logger.warning("app_error", path=request.url.path, error=exc.message, status_code=status_code)
    return JSONResponse(status_code=status_code, content={"detail": exc.message})


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler ensuring stack traces never leak to clients."""
    logger.exception("unhandled_exception", path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the given FastAPI app."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
