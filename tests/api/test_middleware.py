"""API tests for correlation ID middleware."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.middleware import CORRELATION_ID_HEADER, correlation_id_middleware
from app.main import create_app


def test_response_includes_correlation_id_header() -> None:
    """Every response should carry a correlation ID header."""
    client = TestClient(create_app())

    response = client.get("/health")

    assert CORRELATION_ID_HEADER in response.headers
    assert response.headers[CORRELATION_ID_HEADER]


def test_correlation_id_header_is_echoed_back() -> None:
    """A caller-supplied correlation ID should be echoed back unchanged."""
    client = TestClient(create_app())

    response = client.get("/health", headers={CORRELATION_ID_HEADER: "test-id-123"})

    assert response.headers[CORRELATION_ID_HEADER] == "test-id-123"


def test_middleware_logs_and_reraises_on_downstream_exception() -> None:
    """An unhandled exception in a route should propagate through the middleware, unmasked."""
    app = FastAPI()
    app.middleware("http")(correlation_id_middleware)

    @app.get("/boom")
    def _raise() -> None:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/boom")

    assert response.status_code == 500
