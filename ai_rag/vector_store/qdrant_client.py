"""Qdrant Vector Store client manager for EduMate RAG Knowledge Engine.

Manages collection initialization, chunk embedding indexing, and similarity search
with in-memory fallback support.
"""

import logging
import uuid
from typing import List, Optional

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as rest_models
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

from ai_rag.schemas.chunk_schemas import TextChunk
from ai_rag.schemas.vector_schemas import (
    CollectionConfig,
    SearchQuery,
    SearchResult,
    VectorPayload,
    VectorPoint,
)

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Manages Qdrant vector collection and operations for study material RAG.

    Supports both remote Qdrant server connection and local in-memory fallback.
    """

    def __init__(
        self,
        config: Optional[CollectionConfig] = None,
        location: Optional[str] = ":memory:",
        url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.config = config or CollectionConfig()
        self.client: Optional[Any] = None

        if QDRANT_AVAILABLE:
            try:
                if url:
                    self.client = QdrantClient(url=url, api_key=api_key)
                    logger.info(f"Connected to remote Qdrant server at '{url}'")
                else:
                    self.client = QdrantClient(location=location)
                    logger.info(f"Initialized local Qdrant client (location='{location}')")
            except Exception as exc:
                logger.warning(f"Failed to initialize QdrantClient: {exc}")
                self.client = None
        else:
            logger.warning("qdrant-client library not installed; running in stub mode")

        self.init_collection()

    def init_collection(self) -> bool:
        """Create or verify the Qdrant collection with vector configuration.

        Returns:
            True if collection is ready, False otherwise.
        """
        if not self.client:
            return False

        try:
            collections = self.client.get_collections().collections
            existing_names = {c.name for c in collections}

            if self.config.collection_name not in existing_names:
                distance = (
                    rest_models.Distance.COSINE
                    if self.config.distance_metric.upper() == "COSINE"
                    else rest_models.Distance.DOT
                )

                self.client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=rest_models.VectorParams(
                        size=self.config.vector_size,
                        distance=distance,
                    ),
                )
                logger.info(
                    f"Created Qdrant collection '{self.config.collection_name}' "
                    f"(size={self.config.vector_size}, distance={self.config.distance_metric})"
                )
            else:
                logger.info(f"Qdrant collection '{self.config.collection_name}' already exists")
            return True
        except Exception as exc:
            logger.error(f"Error initializing Qdrant collection: {exc}")
            return False

    def upsert_chunks(
        self,
        chunks: List[TextChunk],
        vectors: List[List[float]],
        document_name: str,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> int:
        """Insert or update document text chunks and vector embeddings in Qdrant.

        Args:
            chunks: List of TextChunk objects.
            vectors: List of dense vector float lists corresponding to chunks.
            document_name: Source PDF document name.
            subject: Optional subject context filter.
            topic: Optional topic context filter.

        Returns:
            Number of points successfully upserted.
        """
        if not self.client:
            logger.warning("Qdrant client uninitialized; skipping upsert")
            return 0

        if len(chunks) != len(vectors):
            raise ValueError(
                f"Mismatch between chunks count ({len(chunks)}) and vectors count ({len(vectors)})"
            )

        points: List[rest_models.PointStruct] = []

        for chunk, vector in zip(chunks, vectors):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            payload = VectorPayload(
                chunk_id=chunk.chunk_id,
                document_name=document_name,
                page_number=chunk.page_number,
                text=chunk.text,
                section_title=chunk.section_title,
                subject=subject,
                topic=topic,
                char_count=chunk.char_count,
            ).model_dump()

            points.append(
                rest_models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

        try:
            self.client.upsert(
                collection_name=self.config.collection_name,
                points=points,
            )
            logger.info(
                f"Upserted {len(points)} points into '{self.config.collection_name}' for '{document_name}'"
            )
            return len(points)
        except Exception as exc:
            logger.error(f"Failed to upsert points into Qdrant: {exc}")
            return 0

    def search_similar(self, query: SearchQuery) -> List[SearchResult]:
        """Execute similarity search against indexed vector chunks.

        Args:
            query: SearchQuery with query vector, top_k, threshold, and optional metadata filters.

        Returns:
            List of SearchResult objects matching similarity threshold.
        """
        if not self.client:
            logger.warning("Qdrant client uninitialized; returning empty search results")
            return []

        try:
            query_filter = None
            conditions = []

            if query.subject_filter:
                conditions.append(
                    rest_models.FieldCondition(
                        key="subject",
                        match=rest_models.MatchValue(value=query.subject_filter),
                    )
                )

            if query.topic_filter:
                conditions.append(
                    rest_models.FieldCondition(
                        key="topic",
                        match=rest_models.MatchValue(value=query.topic_filter),
                    )
                )

            if conditions:
                query_filter = rest_models.Filter(must=conditions)

            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.config.collection_name,
                    query=query.query_vector,
                    query_filter=query_filter,
                    limit=query.top_k,
                    score_threshold=query.score_threshold if query.score_threshold > 0 else None,
                )
                hits = response.points
            elif hasattr(self.client, "search"):
                hits = self.client.search(
                    collection_name=self.config.collection_name,
                    query_vector=query.query_vector,
                    query_filter=query_filter,
                    limit=query.top_k,
                    score_threshold=query.score_threshold if query.score_threshold > 0 else None,
                )
            else:
                hits = []

            results: List[SearchResult] = []
            for hit in hits:
                payload = hit.payload or {}
                results.append(
                    SearchResult(
                        chunk_id=payload.get("chunk_id", ""),
                        score=hit.score,
                        document_name=payload.get("document_name", ""),
                        page_number=payload.get("page_number", 1),
                        text_snippet=payload.get("text", ""),
                        section_title=payload.get("section_title"),
                    )
                )

            logger.info(f"Vector search returned {len(results)} matches (top_k={query.top_k})")
            return results
        except Exception as exc:
            logger.error(f"Error executing vector similarity search: {exc}")
            return []


qdrant_store = QdrantVectorStore()
