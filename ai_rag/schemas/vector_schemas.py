"""Pydantic v2 schemas for Qdrant vector database storage and similarity search."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CollectionConfig(BaseModel):
    """Configuration for a Qdrant vector store collection."""

    collection_name: str = Field(
        "edumate_study_materials",
        description="Name of the Qdrant collection",
    )
    vector_size: int = Field(
        768,
        description="Dimensionality of text embedding vectors (e.g. 768 for text-embedding-004)",
    )
    distance_metric: str = Field(
        "Cosine",
        description="Distance metric for vector similarity (Cosine, Dot, Euclidean)",
    )


class VectorPayload(BaseModel):
    """Payload metadata attached to a single vector point in Qdrant."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_name: str = Field(..., description="Original PDF filename")
    page_number: int = Field(..., ge=1, description="1-indexed source page number")
    text: str = Field(..., description="Text content of the chunk")
    section_title: Optional[str] = Field(None, description="Section heading if detected")
    subject: Optional[str] = Field(None, description="Academic subject context")
    topic: Optional[str] = Field(None, description="Specific topic context")
    char_count: int = Field(..., ge=0, description="Character length of chunk text")


class VectorPoint(BaseModel):
    """Represents a vector entry ready to be inserted into Qdrant."""

    id: str = Field(..., description="Unique point ID (UUID or chunk_id)")
    vector: List[float] = Field(..., description="Dense embedding vector floats")
    payload: VectorPayload = Field(..., description="Associated metadata payload")


class SearchQuery(BaseModel):
    """Parameters for executing a vector similarity search."""

    query_vector: List[float] = Field(..., description="Query embedding vector")
    top_k: int = Field(5, ge=1, le=50, description="Maximum number of results to return")
    score_threshold: float = Field(
        0.65, ge=0.0, le=1.0, description="Minimum cosine similarity score threshold"
    )
    subject_filter: Optional[str] = Field(None, description="Filter by subject metadata")
    topic_filter: Optional[str] = Field(None, description="Filter by topic metadata")


class HybridSearchQuery(BaseModel):
    """Parameters for hybrid dense vector + BM25 keyword search with rank fusion."""

    query_text: str = Field(..., description="Raw textual search query for BM25 keyword matching")
    query_vector: List[float] = Field(..., description="Query embedding vector for dense search")
    top_k: int = Field(5, ge=1, le=50, description="Number of hybrid results to return")
    dense_weight: float = Field(0.6, ge=0.0, le=1.0, description="Weight factor for dense vector similarity (0-1)")
    score_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum fused similarity score threshold")
    subject_filter: Optional[str] = Field(None, description="Filter by subject metadata")
    topic_filter: Optional[str] = Field(None, description="Filter by topic metadata")


class SearchResult(BaseModel):
    """Represents a matched chunk returned from similarity search."""

    chunk_id: str = Field(..., description="Matched chunk ID")
    score: float = Field(..., description="Similarity score (0.0 to 1.0)")
    document_name: str = Field(..., description="Source PDF filename")
    page_number: int = Field(..., description="Source page number")
    text_snippet: str = Field(..., description="Chunk text snippet")
    section_title: Optional[str] = Field(None, description="Section title if present")


class HybridSearchResult(SearchResult):
    """Extends SearchResult with hybrid search rank and BM25 metadata."""

    dense_score: float = Field(0.0, description="Dense cosine similarity score")
    bm25_score: float = Field(0.0, description="BM25 keyword match score")
    rrf_score: float = Field(0.0, description="Combined Reciprocal Rank Fusion score")

