import json

import pytest

from backend import database
from ai_rag.schemas.chunk_schemas import TextChunk
from ai_rag.schemas.vector_schemas import SearchQuery
from ai_rag.vector_store.postgres_vector_store import PostgresVectorStore


class FakeResult:
    rowcount = 1

    def __init__(self, rows=None):
        self._rows = rows or []

    def mappings(self):
        return self

    def all(self):
        return self._rows


class FakeConnection:
    def __init__(self, result=None):
        self.result = result or FakeResult()
        self.statement = None
        self.parameters = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, statement, parameters):
        self.statement = str(statement)
        self.parameters = parameters
        return self.result


class FakeEngine:
    def __init__(self, result=None):
        self.connection = FakeConnection(result)

    def begin(self):
        return self.connection

    def connect(self):
        return self.connection


def test_upsert_persists_vector_as_pgvector_and_owner(monkeypatch):
    engine = FakeEngine()
    monkeypatch.setattr(database, "IS_POSTGRES", True)
    monkeypatch.setattr(database, "engine", engine)

    chunk = TextChunk(
        chunk_id="chunk-1",
        text="Vectors are stored in PostgreSQL.",
        page_number=1,
        section_hierarchy=["Chapter 2", "Vector storage"],
        char_count=34,
        token_estimate=8,
    )
    vector = [0.0] * 768
    vector[0] = 1.0

    count = PostgresVectorStore().upsert_chunks(
        chunks=[chunk],
        vectors=[vector],
        document_name="vectors.pdf",
        owner_id=42,
        document_id="doc-1",
    )

    assert count == 1
    assert "CAST(:embedding AS vector)" in engine.connection.statement
    row = engine.connection.parameters[0]
    assert row["student_id"] == 42
    assert row["document_id"] == "doc-1"
    assert row["section_title"] == "Chapter 2 > Vector storage"
    assert json.loads(row["embedding"]) == vector


def test_search_filters_by_authenticated_student(monkeypatch):
    engine = FakeEngine(
        FakeResult(
            [
                {
                    "chunk_id": "chunk-1",
                    "document_name": "vectors.pdf",
                    "page_number": 1,
                    "content": "Vectors are stored in PostgreSQL.",
                    "section_title": None,
                    "score": 0.9,
                }
            ]
        )
    )
    monkeypatch.setattr(database, "IS_POSTGRES", True)
    monkeypatch.setattr(database, "engine", engine)

    results = PostgresVectorStore().search_similar(
        SearchQuery(
            query_vector=[0.0] * 768,
            owner_id=42,
            subject_filter="Math",
            document_id="doc-1",
        )
    )

    assert len(results) == 1
    assert results[0].score == 0.9
    assert "student_id = :owner_id" in engine.connection.statement
    assert "subject = :subject" in engine.connection.statement
    assert "document_id = :document_id" in engine.connection.statement
    assert engine.connection.parameters["owner_id"] == 42
    assert engine.connection.parameters["subject"] == "Math"
    assert engine.connection.parameters["document_id"] == "doc-1"


def test_keyword_search_is_full_collection_and_owner_scoped(monkeypatch):
    engine = FakeEngine(
        FakeResult(
            [
                {
                    "chunk_id": "chunk-1",
                    "document_name": "vectors.pdf",
                    "page_number": 1,
                    "content": "A vector is a mathematical object.",
                    "section_title": "Vectors",
                    "score": 0.75,
                }
            ]
        )
    )
    monkeypatch.setattr(database, "IS_POSTGRES", True)
    monkeypatch.setattr(database, "engine", engine)

    results = PostgresVectorStore().search_keyword_candidates(
        query_text="mathematical vector",
        owner_id=42,
        top_k=50,
        subject_filter="Math",
        document_id="doc-1",
    )

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-1"
    assert "plainto_tsquery('simple', :query_text) AS all_terms" in engine.connection.statement
    assert "phraseto_tsquery('simple', :query_text) AS phrase_terms" in engine.connection.statement
    assert "to_tsquery('simple', :any_terms) AS any_terms" in engine.connection.statement
    assert "strpos(lower(content), lower(:query_text)) > 0" in engine.connection.statement
    assert "to_tsvector('simple', coalesce(section_title, ''))" in engine.connection.statement
    assert "to_tsvector('simple', content) @@ search_terms.any_terms" in engine.connection.statement
    assert "student_id = :owner_id" in engine.connection.statement
    assert engine.connection.parameters["owner_id"] == 42
    assert engine.connection.parameters["top_k"] == 50
    assert engine.connection.parameters["subject"] == "Math"
    assert engine.connection.parameters["document_id"] == "doc-1"
    assert engine.connection.parameters["any_terms"] == "mathematical | vector"


def test_keyword_search_skips_queries_without_searchable_terms(monkeypatch):
    monkeypatch.setattr(database, "IS_POSTGRES", True)
    monkeypatch.setattr(database, "engine", FakeEngine())

    results = PostgresVectorStore().search_keyword_candidates(
        query_text="?!",
        owner_id=42,
        top_k=10,
    )

    assert results == []


def test_search_rejects_missing_owner(monkeypatch):
    monkeypatch.setattr(database, "IS_POSTGRES", True)
    monkeypatch.setattr(database, "engine", FakeEngine())
    with pytest.raises(ValueError, match="student profile ID"):
        PostgresVectorStore().search_similar(SearchQuery(query_vector=[0.0] * 768))
