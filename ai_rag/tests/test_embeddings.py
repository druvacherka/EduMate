"""Unit tests for Gemini text-embedding-004 generator and batch pipeline."""

import math
import pytest

from ai_rag.document_processing.pipeline import DocumentProcessingPipeline
from ai_rag.embeddings.gemini_embedder import GeminiEmbedder, gemini_embedder
from ai_rag.schemas.chunk_schemas import ChunkedDocument, TextChunk
from ai_rag.schemas.embedding_schemas import BatchEmbeddingResult, EmbeddingConfig
from ai_rag.schemas.pdf_schemas import PageContent, PDFMetadata, ParsedDocument
from ai_rag.vector_store.qdrant_client import QdrantVectorStore


def test_embed_text_dimensionality():
    embedder = GeminiEmbedder()
    vec = embedder.embed_text("Data structures and algorithms in Python")

    assert isinstance(vec, list)
    assert len(vec) == 768
    assert all(isinstance(val, float) for val in vec)

    # Check L2 norm unit length (~1.0)
    l2_norm = math.sqrt(sum(v * v for v in vec))
    assert abs(l2_norm - 1.0) < 1e-4


def test_embed_chunks_batch():
    embedder = GeminiEmbedder(config=EmbeddingConfig(batch_size=2))

    chunks = [
        TextChunk(
            chunk_id="chunk_001",
            text="Binary trees have left and right child nodes.",
            page_number=1,
            char_count=44,
            token_estimate=11,
        ),
        TextChunk(
            chunk_id="chunk_002",
            text="AVL trees are self-balancing binary search trees.",
            page_number=1,
            char_count=49,
            token_estimate=12,
        ),
        TextChunk(
            chunk_id="chunk_003",
            text="Red-black trees maintain O(log n) height invariant.",
            page_number=2,
            char_count=51,
            token_estimate=13,
        ),
    ]

    result = embedder.embed_chunks(chunks)

    assert isinstance(result, BatchEmbeddingResult)
    assert result.total_chunks == 3
    assert len(result.vectors) == 3
    assert len(result.vectors[0]) == 768


def test_pipeline_integration():
    mock_parsed_doc = ParsedDocument(
        metadata=PDFMetadata(file_name="trees.pdf", total_pages=1, file_size_bytes=512),
        pages=[
            PageContent(
                page_number=1,
                text="Binary Search Tree operations include insertion, deletion, and search.",
                has_tables=False,
                headers=["Binary Search Trees"],
                char_count=70,
            )
        ],
        total_chars=70,
        is_valid=True,
    )

    vector_store = QdrantVectorStore(location=":memory:")
    pipeline = DocumentProcessingPipeline(vector_store=vector_store)

    # Directly run chunker, embedder, and vector_store pipeline stages
    chunked = pipeline.chunker.chunk_document(mock_parsed_doc)
    embedding_result = pipeline.embedder.embed_chunks(chunked.chunks)
    upsert_count = vector_store.upsert_chunks(
        chunks=chunked.chunks,
        vectors=embedding_result.vectors,
        document_name=chunked.document_name,
    )

    from ai_rag.vector_store.qdrant_client import QDRANT_AVAILABLE

    assert chunked.total_chunks > 0
    assert len(embedding_result.vectors) == chunked.total_chunks
    if QDRANT_AVAILABLE:
        assert upsert_count == chunked.total_chunks
    else:
        assert upsert_count == 0
