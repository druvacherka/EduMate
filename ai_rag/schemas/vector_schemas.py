"""Pydantic schemas for dense and hybrid vector search."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Parameters for executing account-scoped dense vector search."""

    query_vector: List[float] = Field(..., description="Query embedding vector")
    top_k: int = Field(5, ge=1, le=50, description="Maximum number of results to return")
    score_threshold: float = Field(0.65, ge=0.0, le=1.0, description="Minimum cosine similarity")
    subject_filter: Optional[str] = Field(None, description="Filter by subject metadata")
    topic_filter: Optional[str] = Field(None, description="Filter by topic metadata")
    document_id: Optional[str] = Field(None, description="Limit search to one uploaded document")
    owner_id: Optional[int] = Field(None, description="Student profile that owns the embeddings")


class HybridSearchQuery(BaseModel):
    """Parameters for hybrid dense-vector and BM25 keyword search."""

    query_text: str = Field(..., description="Raw textual search query for BM25 keyword matching")
    query_vector: List[float] = Field(..., description="Query vector for dense search")
    top_k: int = Field(5, ge=1, le=50, description="Number of hybrid results to return")
    dense_weight: float = Field(0.6, ge=0.0, le=1.0, description="Weight given to dense ranking")
    score_threshold: float = Field(0.3, ge=0.0, le=1.0, description="Minimum fused score")
    min_dense_score: float = Field(
        0.35, ge=0.0, le=1.0, description="Minimum cosine similarity for dense candidates"
    )
    subject_filter: Optional[str] = Field(None, description="Filter by subject metadata")
    topic_filter: Optional[str] = Field(None, description="Filter by topic metadata")
    document_id: Optional[str] = Field(None, description="Limit search to one uploaded document")
    owner_id: Optional[int] = Field(None, description="Student profile that owns the embeddings")


class SearchResult(BaseModel):
    """A matched text chunk returned by dense search."""

    chunk_id: str = Field(..., description="Matched chunk ID")
    score: float = Field(..., description="Cosine similarity")
    document_name: str = Field(..., description="Source PDF document name")
    page_number: int = Field(..., description="Source page number")
    text_snippet: str = Field(..., description="Matched chunk text")
    section_title: Optional[str] = Field(None, description="Section title, if present")


class HybridSearchResult(SearchResult):
    """A search match with dense, BM25, and reciprocal-rank fusion scores."""

    dense_score: float = Field(0.0, description="Dense cosine similarity")
    bm25_score: float = Field(0.0, description="BM25 keyword match score")
    rrf_score: float = Field(0.0, description="Combined Reciprocal Rank Fusion score")
