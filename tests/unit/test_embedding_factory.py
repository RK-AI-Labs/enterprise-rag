"""Unit tests for the embedding provider factory."""

import pytest

from app.config.settings import Settings
from app.core.exceptions import ValidationError
from app.embedding.factory import get_embedding_provider
from app.embedding.ollama_provider import OllamaEmbeddingProvider
from app.embedding.openai_provider import OpenAiEmbeddingProvider


def test_get_embedding_provider_returns_ollama_by_default() -> None:
    """The default `embedding_provider` setting should build an `OllamaEmbeddingProvider`."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    provider = get_embedding_provider(settings)

    assert isinstance(provider, OllamaEmbeddingProvider)


def test_get_embedding_provider_returns_openai_when_configured() -> None:
    """`embedding_provider=openai` with an API key should build an `OpenAiEmbeddingProvider`."""
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        embedding_provider="openai",
        openai_api_key="sk-test",
    )

    provider = get_embedding_provider(settings)

    assert isinstance(provider, OpenAiEmbeddingProvider)


def test_get_embedding_provider_requires_openai_api_key() -> None:
    """Selecting the openai provider without an API key should raise `ValidationError`."""
    settings = Settings(_env_file=None, embedding_provider="openai")  # type: ignore[call-arg]

    with pytest.raises(ValidationError):
        get_embedding_provider(settings)
