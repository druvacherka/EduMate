"""Small deterministic vector-store fake for isolated RAG search tests."""

import math
from typing import List, Optional

from services.ai_rag.schemas.chunk_schemas import TextChunk
from services.ai_rag.schemas.vector_schemas import SearchQuery, SearchResult


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
            self.records.append((chunk, vector, document_name, subject, topic, owner_id))
        return len(chunks)

    def search_similar(self, query: SearchQuery) -> List[SearchResult]:
        if query.owner_id is None and any(record[5] is not None for record in self.records):
            return []
        query_norm = math.sqrt(sum(value * value for value in query.query_vector)) or 1.0
        matches = []
        for chunk, vector, document_name, subject, topic, owner_id in self.records:
            if query.owner_id is not None and owner_id != query.owner_id:
                continue
            if query.subject_filter and subject != query.subject_filter:
                continue
            if query.topic_filter and topic != query.topic_filter:
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
