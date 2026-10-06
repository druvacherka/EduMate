"""PostgreSQL/pgvector-backed storage for private EduMate study embeddings."""

import json
import math
from typing import List, Optional

from sqlalchemy import text

from backend import database
from ai_rag.schemas.chunk_schemas import TextChunk
from ai_rag.schemas.vector_schemas import SearchQuery, SearchResult


class PostgresVectorStore:
    """Persists embeddings in PostgreSQL and runs account-scoped cosine search."""

    def upsert_chunks(
        self,
        chunks: List[TextChunk],
        vectors: List[List[float]],
        document_name: str,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        owner_id: Optional[int] = None,
        document_id: Optional[str] = None,
    ) -> int:
        if not database.IS_POSTGRES or database.engine is None:
            raise RuntimeError("RAG vector storage requires a configured PostgreSQL database.")
        if owner_id is None:
            raise ValueError("An authenticated student profile ID is required to store embeddings.")
        if len(chunks) != len(vectors):
            raise ValueError(f"Mismatch between chunks count ({len(chunks)}) and vectors count ({len(vectors)}).")

        resolved_document_id = document_id or document_name
        rows = []
        for chunk, vector in zip(chunks, vectors):
            if len(vector) != 768 or not all(math.isfinite(value) for value in vector):
                raise ValueError(f"Chunk {chunk.chunk_id!r} has an invalid embedding; expected 768 finite values.")
            rows.append(
                {
                    "student_id": owner_id,
                    "document_id": resolved_document_id,
                    "chunk_id": chunk.chunk_id,
                    "document_name": document_name,
                    "page_number": chunk.page_number,
                    "content": chunk.text,
                    "section_title": chunk.section_title,
                    "subject": subject,
                    "topic": topic,
                    "char_count": chunk.char_count,
                    "embedding": json.dumps(vector, separators=(",", ":")),
                }
            )
        if not rows:
            return 0

        statement = text(
            """
            INSERT INTO study_embeddings (
                student_id, document_id, chunk_id, document_name, page_number,
                content, section_title, subject, topic, char_count, embedding
            ) VALUES (
                :student_id, :document_id, :chunk_id, :document_name, :page_number,
                :content, :section_title, :subject, :topic, :char_count,
                CAST(:embedding AS vector)
            )
            ON CONFLICT (student_id, document_id, chunk_id) DO UPDATE SET
                document_name = EXCLUDED.document_name,
                page_number = EXCLUDED.page_number,
                content = EXCLUDED.content,
                section_title = EXCLUDED.section_title,
                subject = EXCLUDED.subject,
                topic = EXCLUDED.topic,
                char_count = EXCLUDED.char_count,
                embedding = EXCLUDED.embedding
            """
        )
        with database.engine.begin() as connection:
            connection.execute(statement, rows)
        return len(rows)

    def search_similar(self, query: SearchQuery) -> List[SearchResult]:
        if not database.IS_POSTGRES or database.engine is None:
            raise RuntimeError("RAG vector search requires a configured PostgreSQL database.")
        if query.owner_id is None:
            raise ValueError("An authenticated student profile ID is required to search embeddings.")
        if len(query.query_vector) != 768 or not all(math.isfinite(value) for value in query.query_vector):
            raise ValueError("The query embedding must contain 768 finite values.")

        conditions = ["student_id = :owner_id"]
        parameters = {
            "owner_id": query.owner_id,
            "query_vector": json.dumps(query.query_vector, separators=(",", ":")),
            "top_k": query.top_k,
            "score_threshold": query.score_threshold,
        }
        if query.subject_filter:
            conditions.append("subject = :subject")
            parameters["subject"] = query.subject_filter
        if query.topic_filter:
            conditions.append("topic = :topic")
            parameters["topic"] = query.topic_filter

        statement = text(
            f"""
            SELECT chunk_id, document_name, page_number, content, section_title,
                   1 - (embedding <=> CAST(:query_vector AS vector)) AS score
            FROM study_embeddings
            WHERE {" AND ".join(conditions)}
              AND 1 - (embedding <=> CAST(:query_vector AS vector)) >= :score_threshold
            ORDER BY embedding <=> CAST(:query_vector AS vector)
            LIMIT :top_k
            """
        )
        with database.engine.connect() as connection:
            rows = connection.execute(statement, parameters).mappings().all()

        return [
            SearchResult(
                chunk_id=row["chunk_id"],
                score=float(row["score"]),
                document_name=row["document_name"],
                page_number=row["page_number"],
                text_snippet=row["content"],
                section_title=row["section_title"],
            )
            for row in rows
        ]

    def search_keyword_candidates(
        self,
        query_text: str,
        owner_id: int,
        top_k: int,
        subject_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        """Find lexical candidates across the owner's full document collection."""
        if not database.IS_POSTGRES or database.engine is None:
            raise RuntimeError("RAG keyword search requires a configured PostgreSQL database.")
        if not query_text.strip():
            return []

        conditions = [
            "student_id = :owner_id",
            "to_tsvector('simple', content) @@ search_terms.terms",
        ]
        parameters = {
            "owner_id": owner_id,
            "query_text": query_text,
            "top_k": top_k,
        }
        if subject_filter:
            conditions.append("subject = :subject")
            parameters["subject"] = subject_filter
        if topic_filter:
            conditions.append("topic = :topic")
            parameters["topic"] = topic_filter

        statement = text(
            f"""
            WITH search_terms AS (
                SELECT plainto_tsquery('simple', :query_text) AS terms
            )
            SELECT chunk_id, document_name, page_number, content, section_title,
                   ts_rank_cd(to_tsvector('simple', content), search_terms.terms) AS score
            FROM study_embeddings
            CROSS JOIN search_terms
            WHERE {" AND ".join(conditions)}
            ORDER BY score DESC
            LIMIT :top_k
            """
        )
        with database.engine.connect() as connection:
            rows = connection.execute(statement, parameters).mappings().all()

        return [
            SearchResult(
                chunk_id=row["chunk_id"],
                score=float(row["score"]),
                document_name=row["document_name"],
                page_number=row["page_number"],
                text_snippet=row["content"],
                section_title=row["section_title"],
            )
            for row in rows
        ]

    def delete_document(self, document_id: str, owner_id: int) -> int:
        if not database.IS_POSTGRES or database.engine is None:
            raise RuntimeError("RAG vector storage requires a configured PostgreSQL database.")
        with database.engine.begin() as connection:
            result = connection.execute(
                text("DELETE FROM study_embeddings WHERE student_id = :owner_id AND document_id = :document_id"),
                {"owner_id": owner_id, "document_id": document_id},
            )
        return int(result.rowcount or 0)


postgres_vector_store = PostgresVectorStore()
