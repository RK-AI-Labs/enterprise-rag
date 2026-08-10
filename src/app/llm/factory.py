"""Factory for constructing the `LlmClient` configured by application settings."""

from app.config.settings import Settings
from app.core.exceptions import ValidationError
from app.llm.base import LlmClient
from app.llm.client import OpenAiCompatibleLlmClient


def get_llm_client(settings: Settings) -> LlmClient:
    """Build the `LlmClient` selected by `settings.llm_provider`."""
    if settings.llm_provider == "ollama":
        return OpenAiCompatibleLlmClient(
            base_url=settings.ollama_openai_base_url,
            model=settings.ollama_model,
            temperature=settings.llm_temperature,
        )
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValidationError("OPENAI_API_KEY must be set to use the openai llm provider")
        return OpenAiCompatibleLlmClient(
            base_url=settings.openai_base_url,
            model=settings.openai_llm_model,
            api_key=settings.openai_api_key,
            temperature=settings.llm_temperature,
        )
    raise ValidationError(f"Unsupported llm provider: {settings.llm_provider}")
