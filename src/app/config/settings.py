"""Typed, environment-driven application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration sourced from environment variables and `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Enterprise RAG"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)

    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_user: str = "enterprise_rag"
    postgres_password: str = "change-me"
    postgres_db: str = "enterprise_rag"

    qdrant_host: str = "localhost"
    qdrant_port: int = Field(default=6333, ge=1, le=65535)
    qdrant_grpc_port: int = Field(default=6334, ge=1, le=65535)
    qdrant_collection: str = "documents"

    chunk_size: int = Field(default=1000, ge=1)
    chunk_overlap: int = Field(default=200, ge=0)

    ollama_host: str = "localhost"
    ollama_port: int = Field(default=11434, ge=1, le=65535)
    ollama_model: str = "qwen3"

    embedding_provider: Literal["ollama", "openai"] = "ollama"
    embedding_model: str = "nomic-embed-text"
    embedding_batch_size: int = Field(default=32, ge=1)

    llm_provider: Literal["ollama", "openai"] = "ollama"
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)

    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_llm_model: str = "gpt-4o-mini"

    retrieval_top_k: int = Field(default=5, ge=1)
    retrieval_dense_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    bm25_k1: float = Field(default=1.5, gt=0.0)
    bm25_b: float = Field(default=0.75, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _validate_chunk_overlap(self) -> "Settings":
        """Ensure chunk overlap never exceeds or equals the chunk size."""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return self

    @property
    def postgres_dsn(self) -> str:
        """Async SQLAlchemy DSN for the Postgres metadata/document registry."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def qdrant_url(self) -> str:
        """HTTP URL for the Qdrant vector store."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    @property
    def ollama_base_url(self) -> str:
        """HTTP base URL for the Ollama server."""
        return f"http://{self.ollama_host}:{self.ollama_port}"

    @property
    def ollama_openai_base_url(self) -> str:
        """HTTP base URL for Ollama's OpenAI-compatible chat completions API."""
        return f"{self.ollama_base_url}/v1"


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide cached `Settings` instance for dependency injection."""
    return Settings()
