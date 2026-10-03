"""MongoDB Vector & Chunk Storage Engine for EduMate (Single Unified Database).

Stores text chunks and their 768-d Gemini embeddings in MongoDB collection `study_chunks`,
providing cosine similarity vector search and BM25 hybrid retrieval directly within MongoDB.
"""

import math
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import logging

from database.connection import get_db

logger = logging.getLogger(__name__)


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class MongoVectorStore:
    """Vector database implementation directly backed by MongoDB."""

    def __init__(self, collection_name: str = "study_chunks"):
        self.collection_name = collection_name

    @property
    def collection(self):
        return get_db()[self.collection_name]

    def upsert_chunks(
        self,
        chunks: List[Any],
        vectors: List[List[float]],
        document_name: str,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> int:
        """Store chunk texts with vector embeddings in MongoDB."""
        if not chunks or not vectors:
            return 0

        inserted_count = 0
        now_str = datetime.now(timezone.utc).isoformat()

        for chunk, vec in zip(chunks, vectors):
            chunk_id = getattr(chunk, "chunk_id", str(getattr(chunk, "id", None)))
            doc = {
                "_id": chunk_id,
                "chunk_id": chunk_id,
                "document_name": document_name,
                "page_number": getattr(chunk, "page_number", 1),
                "section_title": getattr(chunk, "section_title", "General"),
                "text_snippet": getattr(chunk, "text", str(chunk)),
                "embedding": vec,
                "subject": subject,
                "topic": topic,
                "created_at": now_str,
            }
            self.collection.update_one({"_id": chunk_id}, {"$set": doc}, upsert=True)
            inserted_count += 1

        logger.info(f"Upserted {inserted_count} vector chunks to MongoDB collection '{self.collection_name}'.")
        return inserted_count

    def search(
        self,
        query_vector: List[float],
        query_text: Optional[str] = None,
        top_k: int = 5,
        subject_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
        score_threshold: float = 0.25,
    ) -> List[Dict[str, Any]]:
        """Perform vector search over stored document chunks in MongoDB."""
        filter_query: Dict[str, Any] = {}
        if subject_filter:
            filter_query["subject"] = {"$regex": subject_filter, "$options": "i"}
        if topic_filter:
            filter_query["topic"] = {"$regex": topic_filter, "$options": "i"}

        docs = list(self.collection.find(filter_query))
        if not docs:
            # Fallback to no filters if filtered search yielded 0 results
            docs = list(self.collection.find())

        scored_results: List[Dict[str, Any]] = []
        q_tokens = set(query_text.lower().split()) if query_text else set()

        for d in docs:
            emb = d.get("embedding", [])
            dense_score = cosine_similarity(query_vector, emb) if emb else 0.0

            # Lightweight keyword/BM25 boost for hybrid scoring
            snippet = d.get("text_snippet", "").lower()
            bm25_matches = sum(1 for token in q_tokens if token in snippet)
            bm25_score = min(1.0, bm25_matches / max(1, len(q_tokens))) if q_tokens else 0.0

            # Hybrid score (70% dense vector + 30% keyword match)
            combined_score = round((0.7 * dense_score) + (0.3 * bm25_score), 4)

            if combined_score >= score_threshold:
                scored_results.append({
                    "chunk_id": d.get("chunk_id", str(d["_id"])),
                    "document_name": d.get("document_name", "Textbook"),
                    "page_number": d.get("page_number", 1),
                    "section_title": d.get("section_title", "Section"),
                    "text_snippet": d.get("text_snippet", ""),
                    "score": combined_score,
                    "dense_score": round(dense_score, 4),
                    "bm25_score": round(bm25_score, 4),
                    "rrf_score": combined_score,
                })

        # Sort by score descending
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]

    def count(self) -> int:
        """Return total chunks count."""
        return self.collection.count_documents({})


mongo_vector_store = MongoVectorStore()
