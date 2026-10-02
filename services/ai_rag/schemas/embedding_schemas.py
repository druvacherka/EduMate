"""Pydantic v2 schemas for Gemini embedding generation and batch processing."""

from typing import List, Optional
from pydantic import BaseModel, Field


class EmbeddingConfig(BaseModel):
    """Configuration parameters for Gemini embedding generator."""

    model_name: str = Field(
        "text-embedding-004", description="Google Gemini embedding model identifier"
    )
    vector_dimension: int = Field(
        768, ge=1, description="Expected vector embedding dimensionality"
    )
    batch_size: int = Field(
        16, ge=1, le=100, description="Number of text chunks to process per API batch"
    )
    max_retries: int = Field(
        3, ge=0, le=10, description="Maximum retry attempts on API rate limits"
    )
    retry_delay_seconds: float = Field(
        1.0, ge=0.1, description="Initial retry delay in seconds for exponential backoff"
    )


class EmbeddingResult(BaseModel):
    """Result for a single text chunk embedding operation."""

    chunk_id: str = Field(..., description="Target text chunk identifier")
    vector: List[float] = Field(..., description="768-dimensional float vector")
    is_fallback: bool = Field(
        False, description="True if fallback hash vector was generated"
    )


class BatchEmbeddingResult(BaseModel):
    """Container for batch embedding processing results."""

    total_chunks: int = Field(..., ge=0, description="Total chunks processed")
    vectors: List[List[float]] = Field(
        default_factory=list, description="Ordered list of embedding vectors"
    )
    processing_time_seconds: float = Field(
        ..., ge=0.0, description="Batch processing duration in seconds"
    )
    success_count: int = Field(..., ge=0, description="Number of successful embeddings")
    fallback_count: int = Field(..., ge=0, description="Number of fallback embeddings used")
