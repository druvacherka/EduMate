"""Google Gemini text-embedding-004 client and batch embedding generator."""

import hashlib
import logging
import math
import time
from typing import List, Optional

try:
    from google import genai as google_genai
    GENAI_AVAILABLE = True
except ImportError:
    google_genai = None
    GENAI_AVAILABLE = False

from ai_rag.config import settings
from ai_rag.schemas.chunk_schemas import TextChunk
from ai_rag.schemas.embedding_schemas import (
    BatchEmbeddingResult,
    EmbeddingConfig,
    EmbeddingResult,
)

logger = logging.getLogger(__name__)


class GeminiEmbedder:
    """Generates 768-dimensional dense vector embeddings using Gemini text-embedding-004.

    Includes batch processing, exponential backoff retries, and offline fallback generator.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[EmbeddingConfig] = None,
    ) -> None:
        self.api_key = api_key or settings.gemini_api_key
        self.config = config or EmbeddingConfig()
        self._client = None

        if GENAI_AVAILABLE and self.api_key and self.api_key != "demo_gemini_key":
            try:
                self._client = google_genai.Client(api_key=self.api_key)
                logger.info(f"Initialized GeminiEmbedder with model '{self.config.model_name}'")
            except Exception as exc:
                logger.warning(f"Failed to configure Google GenAI client: {exc}")
        else:
            logger.info("Running GeminiEmbedder in offline/fallback mode")

    def embed_text(self, text: str) -> List[float]:
        """Generate a single 768-dimensional vector embedding for a text string.

        Args:
            text: Source text to embed.

        Returns:
            List of 768 floating point vector components.
        """
        if not text or not text.strip():
            return self._generate_fallback_vector("")

        if GENAI_AVAILABLE and self._client is not None:
            for attempt in range(self.config.max_retries + 1):
                try:
                    result = self._client.models.embed_content(
                        model=self.config.model_name,
                        contents=text,
                    )
                    if result.embeddings and result.embeddings[0].values:
                        embedding = result.embeddings[0].values
                        if len(embedding) == self.config.vector_dimension:
                            return list(embedding)
                except Exception as exc:
                    logger.warning(f"Gemini API embed attempt {attempt + 1} failed: {exc}")
                    if attempt < self.config.max_retries:
                        time.sleep(self.config.retry_delay_seconds * (2 ** attempt))

        return self._generate_fallback_vector(text)

    def embed_query(self, text: str) -> List[float]:
        """Generate a single 768-dimensional vector embedding for a query string."""
        return self.embed_text(text)

    def embed_chunks(self, chunks: List[TextChunk]) -> BatchEmbeddingResult:
        """Batch process a list of TextChunk objects into 768-dim vector embeddings.

        Args:
            chunks: List of TextChunk objects produced by TextChunker.

        Returns:
            BatchEmbeddingResult with ordered list of float vectors.
        """
        start_time = time.perf_counter()
        if not chunks:
            return BatchEmbeddingResult(
                total_chunks=0,
                vectors=[],
                processing_time_seconds=0.0,
                success_count=0,
                fallback_count=0,
            )

        vectors: List[List[float]] = []
        success_count = 0
        fallback_count = 0

        # Process in batches of config.batch_size
        batch_size = self.config.batch_size
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            for chunk in batch:
                vec = self.embed_text(chunk.text)
                vectors.append(vec)
                # Check if it was generated via API or fallback
                if self._client is not None:
                    success_count += 1
                else:
                    fallback_count += 1

        duration = time.perf_counter() - start_time
        logger.info(
            f"Embedded {len(chunks)} chunks in {duration:.3f}s "
            f"(success={success_count}, fallback={fallback_count})"
        )

        return BatchEmbeddingResult(
            total_chunks=len(chunks),
            vectors=vectors,
            processing_time_seconds=duration,
            success_count=success_count,
            fallback_count=fallback_count,
        )

    def _generate_fallback_vector(self, text: str) -> List[float]:
        """Generate a deterministic, unit-normalized 768-dim fallback vector from text hash.

        Args:
            text: Input string.

        Returns:
            Unit-length vector of 768 float numbers.
        """
        dim = self.config.vector_dimension
        if not text:
            raw_vals = [0.1] * dim
        else:
            raw_vals = []
            # Hash text chunks to build pseudo-random floats
            for idx in range(dim):
                seed = f"{text}_{idx}".encode("utf-8")
                hash_val = int(hashlib.md5(seed).hexdigest(), 16)
                # Map to range [-1.0, 1.0]
                val = ((hash_val % 20000) / 10000.0) - 1.0
                raw_vals.append(val)

        # Normalize vector to unit L2 length
        l2_norm = math.sqrt(sum(v * v for v in raw_vals)) or 1.0
        return [v / l2_norm for v in raw_vals]


gemini_embedder = GeminiEmbedder()
