"""Small deterministic vector-store fake for isolated RAG search tests."""

import math
from typing import List, Optional

from ai_rag.schemas.chunk_schemas import TextChunk
from ai_rag.schemas.vector_schemas import SearchQuery, SearchResult


class InMemoryVectorStore:
    def __init__(self):
        self.records = []

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
        for chunk, vector in zip(chunks, vectors):
            resolved_document_id = document_id or document_name
            self.records.append((chunk, vector, document_name, subject, topic, owner_id, resolved_document_id))
        return len(chunks)

    def search_similar(self, query: SearchQuery) -> List[SearchResult]:
        if query.owner_id is None and any(record[5] is not None for record in self.records):
            return []
        query_norm = math.sqrt(sum(value * value for value in query.query_vector)) or 1.0
        matches = []
        for chunk, vector, document_name, subject, topic, owner_id, document_id in self.records:
            if query.owner_id is not None and owner_id != query.owner_id:
                continue
            if query.subject_filter and subject != query.subject_filter:
                continue
            if query.topic_filter and topic != query.topic_filter:
                continue
            if query.document_id and document_id != query.document_id:
                continue
            vector_norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            score = sum(a * b for a, b in zip(query.query_vector, vector)) / (query_norm * vector_norm)
            if score >= query.score_threshold:
                matches.append(
                    SearchResult(
                        chunk_id=chunk.chunk_id,
                        score=score,
                        document_name=document_name,
                        page_number=chunk.page_number,
                        text_snippet=chunk.text,
                        section_title=chunk.section_title,
                    )
                )
        matches.sort(key=lambda result: result.score, reverse=True)
        return matches[:query.top_k]

    def search_keyword_candidates(
        self,
        query_text: str,
        owner_id: int,
        top_k: int,
        subject_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> List[SearchResult]:
        from ai_rag.vector_store.hybrid_search import BM25Scorer

        owned_records = [
            record
            for record in self.records
            if record[5] == owner_id
            and (not subject_filter or record[3] == subject_filter)
            and (not topic_filter or record[4] == topic_filter)
            and (not document_id or record[6] == document_id)
        ]
        documents = [
            {"id": chunk.chunk_id, "text": chunk.text}
            for chunk, *_ in owned_records
        ]
        scores = BM25Scorer().compute_scores(query_text, documents)
        records_by_id = {
            record[0].chunk_id: record
            for record in owned_records
        }
        matching = sorted(
            (
                (chunk_id, score)
                for chunk_id, score in scores.items()
                if score > 0
            ),
            key=lambda item: (-item[1], item[0]),
        )[:top_k]
        return [
            SearchResult(
                chunk_id=chunk_id,
                score=score,
                document_name=records_by_id[chunk_id][2],
                page_number=records_by_id[chunk_id][0].page_number,
                text_snippet=records_by_id[chunk_id][0].text,
                section_title=records_by_id[chunk_id][0].section_title,
            )
            for chunk_id, score in matching
        ]
