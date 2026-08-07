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
