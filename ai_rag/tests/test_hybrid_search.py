"""Unit tests for hybrid vector search & BM25 Reciprocal Rank Fusion (RRF)."""

import pytest
from ai_rag.schemas.vector_schemas import HybridSearchQuery, SearchResult
from ai_rag.vector_store.hybrid_search import BM25Scorer, HybridSearchEngine
from ai_rag.tests.in_memory_vector_store import InMemoryVectorStore


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

    from ai_rag.schemas.chunk_schemas import TextChunk

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
        [0.9] + [0.0] * 767,
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


def test_keyword_search_finds_candidate_outside_dense_results():
    from ai_rag.schemas.chunk_schemas import TextChunk

    store = InMemoryVectorStore()
    engine = HybridSearchEngine(store)
    chunks = [
        TextChunk(
            chunk_id="dense-only",
            text="An unrelated passage about entropy.",
            page_number=1,
            char_count=37,
            token_estimate=9,
        ),
        TextChunk(
            chunk_id="keyword-only",
            text="Newton's laws describe motion and classical mechanics.",
            page_number=2,
            char_count=54,
            token_estimate=14,
        ),
    ]
    store.upsert_chunks(
        chunks=chunks,
        vectors=[[1.0] * 768, [-1.0] * 768],
        document_name="Physics.pdf",
        owner_id=9,
    )

    results = engine.search(
        HybridSearchQuery(
            query_text="Newton motion mechanics",
            query_vector=[1.0] * 768,
            top_k=2,
            score_threshold=0.3,
            owner_id=9,
        )
    )

    keyword_match = next(result for result in results if result.chunk_id == "keyword-only")
    assert keyword_match.bm25_score > 0
    assert keyword_match.dense_score == 0


def test_hybrid_search_filters_dense_only_weak_matches():
    store = InMemoryVectorStore()
    engine = HybridSearchEngine(store)
    from ai_rag.schemas.chunk_schemas import TextChunk

    chunks = [
        TextChunk(
            chunk_id="weak-vector-match",
            text="A passage with unrelated wording and no useful query terms.",
            page_number=1,
            char_count=58,
            token_estimate=14,
        )
    ]
    store.upsert_chunks(
        chunks=chunks,
        vectors=[[0.2, 0.98] + [0.0] * 766],
        document_name="Textbook.pdf",
        owner_id=3,
    )

    results = engine.search(
        HybridSearchQuery(
            query_text="the exact concept requested",
            query_vector=[1.0] + [0.0] * 767,
            top_k=5,
            owner_id=3,
        )
    )

    assert results == []


def test_hybrid_search_can_scope_to_selected_document():
    store = InMemoryVectorStore()
    engine = HybridSearchEngine(store)
    from ai_rag.schemas.chunk_schemas import TextChunk

    for chunk_id, document_id in (("selected", "doc-1"), ("other", "doc-2")):
        chunk = TextChunk(
            chunk_id=chunk_id,
            text="Newton's laws describe motion and force.",
            page_number=1,
            char_count=41,
            token_estimate=10,
        )
        store.upsert_chunks(
            chunks=[chunk],
            vectors=[[1.0] * 768],
            document_name=f"{document_id}.pdf",
            owner_id=7,
            document_id=document_id,
        )

    results = engine.search(
        HybridSearchQuery(
            query_text="Newton's laws describe motion and force",
            query_vector=[1.0] * 768,
            document_id="doc-1",
            owner_id=7,
        )
    )

    assert [result.chunk_id for result in results] == ["selected"]
