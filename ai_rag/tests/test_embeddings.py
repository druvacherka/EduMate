"""Unit tests for Gemini text-embedding-004 generator and batch pipeline."""

import math
import pytest

from ai_rag.document_processing.pipeline import DocumentProcessingPipeline
from ai_rag.embeddings.gemini_embedder import GeminiEmbedder, gemini_embedder
from ai_rag.schemas.chunk_schemas import ChunkedDocument, TextChunk
from ai_rag.schemas.embedding_schemas import BatchEmbeddingResult, EmbeddingConfig
from ai_rag.schemas.pdf_schemas import PageContent, PDFMetadata, ParsedDocument
from ai_rag.tests.in_memory_vector_store import InMemoryVectorStore


def test_embed_text_dimensionality():
    embedder = GeminiEmbedder(config=EmbeddingConfig(allow_fallback=True))
    embedder._client = None
    vec = embedder.embed_text("Data structures and algorithms in Python")

    assert isinstance(vec, list)
    assert len(vec) == 768
    assert all(isinstance(val, float) for val in vec)

    # Check L2 norm unit length (~1.0)
    l2_norm = math.sqrt(sum(v * v for v in vec))
    assert abs(l2_norm - 1.0) < 1e-4


def test_embed_chunks_batch():
    embedder = GeminiEmbedder(
        config=EmbeddingConfig(batch_size=2, allow_fallback=True)
    )
    embedder._client = None

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

    vector_store = InMemoryVectorStore()
    pipeline = DocumentProcessingPipeline(
        vector_store=vector_store,
        embedder=GeminiEmbedder(config=EmbeddingConfig(allow_fallback=True)),
    )
    pipeline.embedder._client = None

    # Directly run chunker, embedder, and vector_store pipeline stages
    chunked = pipeline.chunker.chunk_document(mock_parsed_doc)
    embedding_result = pipeline.embedder.embed_chunks(chunked.chunks)
    upsert_count = vector_store.upsert_chunks(
        chunks=chunked.chunks,
        vectors=embedding_result.vectors,
        document_name=chunked.document_name,
        owner_id=1,
    )

    assert chunked.total_chunks > 0
    assert len(embedding_result.vectors) == chunked.total_chunks
    assert upsert_count == chunked.total_chunks


def test_gemini_embedder_uses_retrieval_task_and_configured_dimensions():
    from types import SimpleNamespace

    class FakeModels:
        def __init__(self):
            self.calls = []

        def embed_content(self, **kwargs):
            self.calls.append(kwargs)
            return SimpleNamespace(
                embeddings=[SimpleNamespace(values=[0.25] * 768)]
            )

    embedder = GeminiEmbedder(
        api_key="test-key",
        config=EmbeddingConfig(model_name="gemini-embedding-001"),
    )
    models = FakeModels()
    embedder._client = SimpleNamespace(models=models)

    embedder.embed_chunks(
        [
            TextChunk(
                chunk_id="chunk_1",
                text="Indexed study text.",
                page_number=1,
                char_count=19,
                token_estimate=4,
            )
        ]
    )
    embedder.embed_query("Find related study text.")

    document_config = models.calls[0]["config"]
    query_config = models.calls[1]["config"]
    assert models.calls[0]["model"] == "gemini-embedding-001"
    assert document_config.task_type == "RETRIEVAL_DOCUMENT"
    assert document_config.output_dimensionality == 768
    assert query_config.task_type == "RETRIEVAL_QUERY"
    assert query_config.output_dimensionality == 768
    query_vector = embedder.embed_query("Find related study text.")
    assert abs(math.sqrt(sum(value * value for value in query_vector)) - 1.0) < 1e-4


def test_gemini_document_embeddings_include_section_hierarchy():
    from types import SimpleNamespace

    class FakeModels:
        def __init__(self):
            self.calls = []

        def embed_content(self, **kwargs):
            self.calls.append(kwargs)
            return SimpleNamespace(
                embeddings=[SimpleNamespace(values=[0.25] * 768)]
            )

    embedder = GeminiEmbedder(api_key="test-key")
    models = FakeModels()
    embedder._client = SimpleNamespace(models=models)
    chunk = TextChunk(
        chunk_id="chunk-section",
        text="The source describes a precise concept.",
        page_number=2,
        section_title="Specific Definition",
        section_hierarchy=["Chapter 4", "Section 4.2"],
        char_count=40,
        token_estimate=10,
    )

    embedder.embed_chunks([chunk])

    embedded_text = models.calls[0]["contents"]
    assert embedded_text.startswith("Section: Chapter 4 > Section 4.2 > Specific Definition")
    assert "The source describes a precise concept." in embedded_text


def test_gemini_embedder_does_not_silently_use_fallback_by_default():
    embedder = GeminiEmbedder(
        api_key=None,
        config=EmbeddingConfig(allow_fallback=False),
    )
    embedder._client = None

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        embedder.embed_query("Find a study note.")
