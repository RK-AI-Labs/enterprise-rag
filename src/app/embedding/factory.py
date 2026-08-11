"""Factory for constructing the `EmbeddingProvider` configured by application settings."""

from app.config.settings import Settings
from app.core.exceptions import ValidationError
from app.embedding.base import EmbeddingProvider
from app.embedding.ollama_provider import OllamaEmbeddingProvider
from app.embedding.openai_provider import OpenAiEmbeddingProvider


def get_embedding_provider(settings: Settings) -> EmbeddingProvider:
    """Build the `EmbeddingProvider` selected by `settings.embedding_provider`."""
    if settings.embedding_provider == "ollama":
        return OllamaEmbeddingProvider(
            base_url=settings.ollama_base_url,
            model=settings.embedding_model,
            batch_size=settings.embedding_batch_size,
        )
    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise ValidationError("OPENAI_API_KEY must be set to use the openai embedding provider")
        return OpenAiEmbeddingProvider(
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
            batch_size=settings.embedding_batch_size,
        )
    raise ValidationError(f"Unsupported embedding provider: {settings.embedding_provider}")
