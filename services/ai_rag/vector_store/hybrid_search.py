"""Hybrid search combining PostgreSQL dense-vector search with BM25 keyword scoring.

Uses Reciprocal Rank Fusion (RRF) to merge dense vector similarity results and keyword matching scores.
"""

import math
import re
from typing import Any, Dict, List, Optional, Set
from services.ai_rag.schemas.vector_schemas import HybridSearchQuery, HybridSearchResult, SearchResult

class BM25Scorer:
    """Lightweight in-memory BM25 tokenizer and ranker for text chunks."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into lowercase alphanumeric term tokens."""
        return re.findall(r"\w+", text.lower())

    def compute_scores(self, query_text: str, documents: List[Dict[str, str]]) -> Dict[str, float]:
        """Compute BM25 scores for a collection of documents against query text.

        Args:
            query_text: Search query string.
            documents: List of dicts with keys 'id' and 'text'.

        Returns:
            Dict mapping document ID to BM25 float score.
        """
        query_terms = self.tokenize(query_text)
        if not query_terms or not documents:
            return {doc["id"]: 0.0 for doc in documents}

        doc_tokens = {doc["id"]: self.tokenize(doc["text"]) for doc in documents}
        doc_lens = {doc_id: len(tokens) for doc_id, tokens in doc_tokens.items()}
        avg_doc_len = sum(doc_lens.values()) / max(len(documents), 1)

        # Document frequency (DF)
        df: Dict[str, int] = {}
        for term in set(query_terms):
            df[term] = sum(1 for tokens in doc_tokens.values() if term in set(tokens))

        num_docs = len(documents)
        scores: Dict[str, float] = {}

        for doc_id, tokens in doc_tokens.items():
            doc_len = doc_lens[doc_id]
            score = 0.0
            term_counts: Dict[str, int] = {}
            for t in tokens:
                term_counts[t] = term_counts.get(t, 0) + 1

            for term in query_terms:
                if term in term_counts:
                    tf = term_counts[term]
                    doc_freq = df.get(term, 0)
                    # Inverse document frequency
                    idf = math.log((num_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / max(avg_doc_len, 1.0)))
                    score += idf * (tf * (self.k1 + 1.0)) / max(denom, 1e-6)

            scores[doc_id] = score

        return scores


class HybridSearchEngine:
    """Orchestrates hybrid dense + BM25 search over the configured vector store."""

    def __init__(self, vector_store: Any, rrf_k: int = 60) -> None:
        self.vector_store = vector_store
        self.rrf_k = rrf_k
        self.bm25_scorer = BM25Scorer()

    def reciprocal_rank_fusion(
        self,
        dense_results: List[SearchResult],
        bm25_scores: Dict[str, float],
        dense_weight: float = 0.6,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[HybridSearchResult]:
        """Combine dense similarity and BM25 scores using Reciprocal Rank Fusion (RRF).

        RRF_score = dense_weight * (1 / (rrf_k + dense_rank)) + (1 - dense_weight) * (1 / (rrf_k + bm25_rank))

        Args:
            dense_results: List of SearchResult from the configured vector store.
            bm25_scores: Dict mapping chunk_id to BM25 score.
            dense_weight: Weight given to dense vector ranking (0.0 to 1.0).
            top_k: Max results to return.
            score_threshold: Minimum RRF combined score threshold.

        Returns:
            Sorted list of HybridSearchResult.
        """
        # Map chunk_id to dense result
        chunk_map: Dict[str, SearchResult] = {res.chunk_id: res for res in dense_results}

        # Rank dense results (1-indexed)
        dense_ranks: Dict[str, int] = {
            res.chunk_id: rank + 1 for rank, res in enumerate(dense_results)
        }

        # Rank BM25 results (1-indexed, sorted by BM25 score descending)
        sorted_bm25 = sorted(bm25_scores.items(), key=lambda x: x[1], reverse=True)
        bm25_ranks: Dict[str, int] = {
            chunk_id: rank + 1 for rank, (chunk_id, score) in enumerate(sorted_bm25) if score > 0
        }

        bm25_weight = 1.0 - dense_weight
        all_chunk_ids: Set[str] = set(dense_ranks.keys()).union(set(bm25_ranks.keys()))

        hybrid_results: List[HybridSearchResult] = []

        for chunk_id in all_chunk_ids:
            dense_res = chunk_map.get(chunk_id)
            if not dense_res:
                continue

            d_rank = dense_ranks.get(chunk_id, 1000)
            b_rank = bm25_ranks.get(chunk_id, 1000)

            # RRF calculation
            dense_rrf = 1.0 / (self.rrf_k + d_rank)
            bm25_rrf = 1.0 / (self.rrf_k + b_rank)
            rrf_score = (dense_weight * dense_rrf) + (bm25_weight * bm25_rrf)

            # Normalized combined score (0.0 - 1.0 scale approx)
            normalized_score = min(1.0, rrf_score * (self.rrf_k + 1))

            if normalized_score >= score_threshold:
                hybrid_results.append(
                    HybridSearchResult(
                        chunk_id=chunk_id,
                        score=round(normalized_score, 4),
                        document_name=dense_res.document_name,
                        page_number=dense_res.page_number,
                        text_snippet=dense_res.text_snippet,
                        section_title=dense_res.section_title,
                        dense_score=round(dense_res.score, 4),
                        bm25_score=round(bm25_scores.get(chunk_id, 0.0), 4),
                        rrf_score=round(rrf_score, 6),
                    )
                )

        # Sort by RRF score descending
        hybrid_results.sort(key=lambda x: x.rrf_score, reverse=True)
        return hybrid_results[:top_k]

    def search(self, query: HybridSearchQuery) -> List[HybridSearchResult]:
        """Execute hybrid search using query vector and text query.

        Args:
            query: HybridSearchQuery object.

        Returns:
            List of HybridSearchResult items.
        """
        # 1. Fetch dense candidates from the configured vector store
        from services.ai_rag.schemas.vector_schemas import SearchQuery

        dense_query = SearchQuery(
            query_vector=query.query_vector,
            top_k=query.top_k * 3,  # Over-fetch for rank fusion candidate pool
            score_threshold=0.0,
            subject_filter=query.subject_filter,
            topic_filter=query.topic_filter,
            owner_id=query.owner_id,
        )
        dense_results = self.vector_store.search_similar(dense_query)

        if not dense_results:
            return []

        # 2. Compute BM25 scores across retrieved dense candidates
        docs_for_bm25 = [
            {"id": res.chunk_id, "text": res.text_snippet} for res in dense_results
        ]
        bm25_scores = self.bm25_scorer.compute_scores(query.query_text, docs_for_bm25)

        # 3. Perform Reciprocal Rank Fusion
        return self.reciprocal_rank_fusion(
            dense_results=dense_results,
            bm25_scores=bm25_scores,
            dense_weight=query.dense_weight,
            top_k=query.top_k,
            score_threshold=query.score_threshold,
        )
