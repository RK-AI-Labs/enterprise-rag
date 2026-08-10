"""Dense (vector similarity) retrieval backed by an embedding provider and vector store."""

from app.embedding.base import EmbeddingProvider
from app.models.retrieval import RetrievedChunk
from app.repositories.interfaces import VectorRepository


class DenseRetriever:
    """Retrieves chunks by embedding the query and searching the vector store."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_repository: VectorRepository,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_repository = vector_repository

    async def search(self, query: str, limit: int = 5) -> list[RetrievedChunk]:
        """Embed `query` and return the top-`limit` nearest chunks from the vector store."""
        [query_vector] = await self._embedding_provider.embed([query])
        points = await self._vector_repository.search(query_vector, limit=limit)
        return [
            RetrievedChunk(
                chunk_id=point.id,
                content=str(point.payload.get("content", "")),
                score=point.score if point.score is not None else 0.0,
                source=str(point.payload.get("source", "")),
                metadata=point.payload,
            )
            for point in points
        ]
