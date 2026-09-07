"""Pydantic v2 schemas for text chunking configuration and output."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChunkingConfig(BaseModel):
    """Configuration parameters for the text chunking engine."""

    chunk_size: int = Field(
        800, ge=100, le=4000, description="Target chunk size in characters"
    )
    chunk_overlap: int = Field(
        100, ge=0, le=500, description="Overlap between consecutive chunks in characters"
    )
    separators: List[str] = Field(
        default_factory=lambda: ["\n\n", "\n", ". ", " "],
        description="Ordered list of separators for recursive splitting",
    )


class TextChunk(BaseModel):
    """A single text chunk produced by the chunking engine."""

    chunk_id: str = Field(
        ..., description="Unique identifier: '{document_name}_chunk_{index}'"
    )
    text: str = Field(..., min_length=1, description="Chunk text content")
    page_number: int = Field(..., ge=1, description="Source page number (1-indexed)")
    section_title: Optional[str] = Field(
        None, description="Detected section heading if available"
    )
    char_count: int = Field(..., ge=0, description="Character count of chunk text")
    token_estimate: int = Field(
        ..., ge=0, description="Estimated token count (chars / 4 heuristic)"
    )


class ChunkedDocument(BaseModel):
    """Complete chunked representation of a parsed PDF document."""

    document_name: str = Field(..., description="Source PDF filename")
    total_chunks: int = Field(..., ge=0, description="Total number of chunks produced")
    chunks: List[TextChunk] = Field(
        default_factory=list, description="Ordered list of text chunks"
    )
    chunking_config: ChunkingConfig = Field(
        default_factory=ChunkingConfig, description="Configuration used for chunking"
    )
