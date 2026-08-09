"""Unit tests for application settings."""

from app.config.settings import Settings, get_settings


def test_settings_defaults() -> None:
    """Settings should fall back to documented defaults when no env vars are set."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.app_name == "Enterprise RAG"
    assert settings.environment == "development"
    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5432
    assert settings.qdrant_host == "localhost"
    assert settings.qdrant_port == 6333


def test_settings_postgres_dsn() -> None:
    """`postgres_dsn` should assemble an asyncpg-driver SQLAlchemy DSN from the parts."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.postgres_dsn == (
        "postgresql+asyncpg://enterprise_rag:change-me@localhost:5432/enterprise_rag"
    )


def test_settings_qdrant_url() -> None:
    """`qdrant_url` should assemble an HTTP URL from the configured host/port."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.qdrant_url == "http://localhost:6333"


def test_settings_env_override(monkeypatch) -> None:
    """Environment variables should override the documented defaults."""
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("API_PORT", "9000")
    monkeypatch.setenv("ENVIRONMENT", "production")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.debug is True
    assert settings.api_port == 9000
    assert settings.environment == "production"


def test_get_settings_is_cached() -> None:
    """`get_settings` should return the same cached instance across calls."""
    assert get_settings() is get_settings()
