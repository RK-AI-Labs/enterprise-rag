"""Unit tests for structured logging configuration and correlation ID context."""

import json

from app.config.settings import Settings
from app.logging.context import bind_correlation_id, clear_correlation_id
from app.logging.setup import configure_logging, get_logger


def test_json_output_in_non_development_environment(capsys) -> None:
    """Non-development environments should render logs as parseable JSON."""
    configure_logging(Settings(_env_file=None, environment="production"))  # type: ignore[call-arg]
    logger = get_logger("test")

    logger.info("hello", foo="bar")

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["event"] == "hello"
    assert payload["foo"] == "bar"
    assert payload["level"] == "info"


def test_console_output_in_development_environment(capsys) -> None:
    """Development environment should render human-readable (non-JSON) console output."""
    configure_logging(Settings(_env_file=None, environment="development"))  # type: ignore[call-arg]
    logger = get_logger("test")

    logger.info("hello")

    output = capsys.readouterr().out.strip().splitlines()[-1]
    assert "hello" in output
    try:
        json.loads(output)
    except ValueError:
        pass
    else:
        raise AssertionError("development output should not be JSON")


def test_correlation_id_included_in_json_output(capsys) -> None:
    """A bound correlation ID should be propagated into every log event."""
    configure_logging(Settings(_env_file=None, environment="production"))  # type: ignore[call-arg]
    logger = get_logger("test")

    correlation_id = bind_correlation_id("req-123")
    try:
        logger.info("hello")
        payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
        assert payload["correlation_id"] == correlation_id == "req-123"
    finally:
        clear_correlation_id()


def test_clear_correlation_id_removes_it_from_output(capsys) -> None:
    """Clearing the correlation ID should stop it from appearing in subsequent log events."""
    configure_logging(Settings(_env_file=None, environment="production"))  # type: ignore[call-arg]
    logger = get_logger("test")

    bind_correlation_id("req-456")
    clear_correlation_id()
    logger.info("hello")

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert "correlation_id" not in payload


def test_bind_correlation_id_generates_value_when_omitted() -> None:
    """Omitting an explicit correlation ID should generate one automatically."""
    correlation_id = bind_correlation_id()
    try:
        assert correlation_id
    finally:
        clear_correlation_id()
