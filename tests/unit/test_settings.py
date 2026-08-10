"""Unit tests for application settings."""

import pytest
from pydantic import ValidationError

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
    assert settings.chunk_size == 1000
    assert settings.chunk_overlap == 200
    assert settings.ollama_host == "localhost"
    assert settings.ollama_port == 11434
    assert settings.embedding_provider == "ollama"
    assert settings.embedding_model == "nomic-embed-text"
    assert settings.embedding_batch_size == 32
    assert settings.openai_api_key is None
    assert settings.openai_base_url == "https://api.openai.com/v1"
    assert settings.openai_embedding_model == "text-embedding-3-small"
    assert settings.retrieval_top_k == 5
    assert settings.retrieval_dense_weight == 0.5
    assert settings.bm25_k1 == 1.5
    assert settings.bm25_b == 0.75


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


def test_settings_ollama_base_url() -> None:
    """`ollama_base_url` should assemble an HTTP URL from the configured host/port."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.ollama_base_url == "http://localhost:11434"


def test_settings_rejects_chunk_overlap_gte_chunk_size() -> None:
    """Settings should reject a chunk_overlap that is not smaller than chunk_size."""
    with pytest.raises(ValidationError):
        Settings(_env_file=None, chunk_size=100, chunk_overlap=100)  # type: ignore[call-arg]


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
