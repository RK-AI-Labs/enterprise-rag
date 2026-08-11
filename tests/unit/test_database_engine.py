"""Unit tests for the Postgres async engine/session factory."""

from app.config.settings import Settings
from app.database.engine import create_engine, get_engine, get_session_factory


def test_create_engine_uses_settings_dsn() -> None:
    """The engine's URL should be derived from the given settings' Postgres DSN."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    engine = create_engine(settings)

    assert engine.url.render_as_string(hide_password=False) == settings.postgres_dsn


def test_get_engine_is_cached() -> None:
    """`get_engine` should return the same cached instance across calls."""
    assert get_engine() is get_engine()


def test_get_session_factory_binds_to_given_engine() -> None:
    """`get_session_factory` should bind the returned session factory to the given engine."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    engine = create_engine(settings)

    session_factory = get_session_factory(engine)

    assert session_factory.kw["bind"] is engine
