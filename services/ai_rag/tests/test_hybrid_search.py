"""Unit tests for hybrid vector search & BM25 Reciprocal Rank Fusion (RRF)."""

import pytest
from services.ai_rag.schemas.vector_schemas import HybridSearchQuery, SearchResult
from services.ai_rag.vector_store.hybrid_search import BM25Scorer, HybridSearchEngine
from services.ai_rag.tests.in_memory_vector_store import InMemoryVectorStore


def test_bm25_tokenizer_and_scoring():
    scorer = BM25Scorer()
    docs = [
        {"id": "c1", "text": "Linear algebra includes vector spaces and matrices."},
        {"id": "c2", "text": "Calculus focuses on derivatives and integrals of functions."},
        {"id": "c3", "text": "Vectors and linear transformations in vector space."},
    ]

    scores = scorer.compute_scores("vector spaces linear", docs)
    assert scores["c1"] > scores["c2"]
    assert scores["c3"] > scores["c2"]
    assert scores["c2"] == 0.0 or scores["c2"] < scores["c1"]


def test_reciprocal_rank_fusion():
    store = InMemoryVectorStore()
    engine = HybridSearchEngine(store)

    dense_results = [
        SearchResult(
            chunk_id="chunk_1",
            score=0.92,
            document_name="Math.pdf",
            page_number=5,
            text_snippet="Linear algebra vector space definitions.",
            section_title="Vectors",
        ),
        SearchResult(
            chunk_id="chunk_2",
            score=0.85,
            document_name="Math.pdf",
            page_number=12,
            text_snippet="Calculus derivatives and integrals.",
            section_title="Calculus",
        ),
    ]

    bm25_scores = {"chunk_1": 4.5, "chunk_2": 0.0}

    fused = engine.reciprocal_rank_fusion(
        dense_results=dense_results,
        bm25_scores=bm25_scores,
        dense_weight=0.6,
        top_k=2,
        score_threshold=0.0,
    )

    assert len(fused) == 2
    assert fused[0].chunk_id == "chunk_1"
    assert fused[0].dense_score == 0.92
    assert fused[0].bm25_score == 4.5
    assert fused[0].rrf_score > fused[1].rrf_score


def test_hybrid_search_end_to_end():
    store = InMemoryVectorStore()
    engine = HybridSearchEngine(store)

    from services.ai_rag.schemas.chunk_schemas import TextChunk

    chunks = [
        TextChunk(
            chunk_id="chunk_a",
            text="Newton's laws of motion describe classical mechanics.",
            page_number=1,
            section_title="Mechanics",
            char_count=50,
            token_estimate=12,
        ),
        TextChunk(
            chunk_id="chunk_b",
            text="Thermodynamics covers heat, energy, and entropy.",
            page_number=3,
            section_title="Thermodynamics",
            char_count=48,
            token_estimate=12,
        ),
    ]

    fake_vectors = [
        [0.1] * 768,
        [0.9] * 768,
    ]

    store.upsert_chunks(chunks=chunks, vectors=fake_vectors, document_name="Physics.pdf", owner_id=1)

    query = HybridSearchQuery(
        query_text="Newton mechanics motion",
        query_vector=[0.1] * 768,
        top_k=2,
        dense_weight=0.7,
        score_threshold=0.0,
        owner_id=1,
    )

    results = engine.search(query)
    assert len(results) >= 1
    assert results[0].chunk_id == "chunk_a"
