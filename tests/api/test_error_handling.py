"""API tests for custom exception handling."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.exception_handlers import register_exception_handlers
from app.core.exceptions import NotFoundError, ValidationError


def _build_test_app() -> FastAPI:
    """Build a minimal app wired with the real exception handlers for isolated testing."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom/not-found")
    def _raise_not_found() -> None:
        raise NotFoundError("missing")

    @app.get("/boom/validation")
    def _raise_validation() -> None:
        raise ValidationError("bad input")

    @app.get("/boom/unhandled")
    def _raise_unhandled() -> None:
        raise RuntimeError("boom")

    return app


def test_not_found_error_returns_404() -> None:
    """A NotFoundError should be mapped to a 404 with its message, not a stack trace."""
    client = TestClient(_build_test_app(), raise_server_exceptions=False)

    response = client.get("/boom/not-found")

    assert response.status_code == 404
    assert response.json() == {"detail": "missing"}


def test_validation_error_returns_422() -> None:
    """A ValidationError should be mapped to a 422 with its message."""
    client = TestClient(_build_test_app(), raise_server_exceptions=False)

    response = client.get("/boom/validation")

    assert response.status_code == 422
    assert response.json() == {"detail": "bad input"}


def test_unhandled_exception_returns_generic_500() -> None:
    """Unhandled exceptions must never leak stack traces or exception details."""
    client = TestClient(_build_test_app(), raise_server_exceptions=False)

    response = client.get("/boom/unhandled")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text
