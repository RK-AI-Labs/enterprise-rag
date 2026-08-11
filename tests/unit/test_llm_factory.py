"""Unit tests for the LLM client factory."""

import pytest

from app.config.settings import Settings
from app.core.exceptions import ValidationError
from app.llm.client import OpenAiCompatibleLlmClient
from app.llm.factory import get_llm_client


def test_get_llm_client_returns_ollama_backed_client_by_default() -> None:
    """The default `llm_provider` setting should build a client targeting Ollama's OpenAI API."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    client = get_llm_client(settings)

    assert isinstance(client, OpenAiCompatibleLlmClient)


def test_get_llm_client_returns_openai_backed_client_when_configured() -> None:
    """`llm_provider=openai` with an API key should build a client targeting OpenAI."""
    settings = Settings(
        _env_file=None,  # type: ignore[call-arg]
        llm_provider="openai",
        openai_api_key="sk-test",
    )

    client = get_llm_client(settings)

    assert isinstance(client, OpenAiCompatibleLlmClient)


def test_get_llm_client_requires_openai_api_key() -> None:
    """Selecting the openai provider without an API key should raise `ValidationError`."""
    settings = Settings(_env_file=None, llm_provider="openai")  # type: ignore[call-arg]

    with pytest.raises(ValidationError):
        get_llm_client(settings)


def test_get_llm_client_rejects_unsupported_provider() -> None:
    """An unrecognized `llm_provider` value should raise `ValidationError`."""
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    settings.llm_provider = "bogus"  # type: ignore[assignment]

    with pytest.raises(ValidationError):
        get_llm_client(settings)
