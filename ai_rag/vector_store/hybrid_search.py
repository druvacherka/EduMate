"""Hybrid search combining PostgreSQL dense-vector search with BM25 keyword scoring.

Uses Reciprocal Rank Fusion (RRF) to merge dense vector similarity results and keyword matching scores.
"""

import math
import re
from typing import Any, Dict, List, Optional, Set
from ai_rag.schemas.vector_schemas import HybridSearchQuery, HybridSearchResult, SearchResult

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
        keyword_results: Optional[List[SearchResult]] = None,
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
        chunk_map: Dict[str, SearchResult] = {
            result.chunk_id: result for result in dense_results
        }
        keyword_map = {
            result.chunk_id: result for result in (keyword_results or [])
        }

        dense_ranks: Dict[str, int] = {
            res.chunk_id: rank + 1 for rank, res in enumerate(dense_results)
        }

        keyword_scores = {
            result.chunk_id: result.score for result in (keyword_results or [])
        }
        lexical_candidate_ids = {
            chunk_id for chunk_id, score in bm25_scores.items() if score > 0
        } | {
            chunk_id for chunk_id, score in keyword_scores.items() if score > 0
        }
        sorted_bm25_ids = sorted(
            lexical_candidate_ids,
            key=lambda chunk_id: (
                -bm25_scores.get(chunk_id, 0.0),
                -keyword_scores.get(chunk_id, 0.0),
                chunk_id,
            ),
        )
        bm25_ranks = {
            chunk_id: rank + 1
            for rank, chunk_id in enumerate(sorted_bm25_ids)
        }

        bm25_weight = 1.0 - dense_weight
        all_chunk_ids: Set[str] = (
            set(dense_ranks) | set(bm25_ranks) | set(keyword_map)
        )

        hybrid_results: List[HybridSearchResult] = []

        for chunk_id in all_chunk_ids:
            dense_res = chunk_map.get(chunk_id)
            keyword_res = keyword_map.get(chunk_id)
            result = dense_res or keyword_res
            if result is None:
                continue

            dense_rrf = (
                dense_weight / (self.rrf_k + dense_ranks[chunk_id])
                if chunk_id in dense_ranks
                else 0.0
            )
            bm25_rrf = (
                bm25_weight / (self.rrf_k + bm25_ranks[chunk_id])
                if chunk_id in bm25_ranks
                else 0.0
            )
            rrf_score = dense_rrf + bm25_rrf
            normalized_score = min(1.0, rrf_score * (self.rrf_k + 1))

            if normalized_score >= score_threshold:
                hybrid_results.append(
                    HybridSearchResult(
                        chunk_id=chunk_id,
                        score=round(normalized_score, 4),
                        document_name=result.document_name,
                        page_number=result.page_number,
                        text_snippet=result.text_snippet,
                        section_title=result.section_title,
                        dense_score=round(dense_res.score, 4) if dense_res else 0.0,
                        bm25_score=round(bm25_scores.get(chunk_id, 0.0), 4),
                        rrf_score=round(rrf_score, 6),
                    )
                )

        hybrid_results.sort(key=lambda result: (-result.rrf_score, result.chunk_id))
        return hybrid_results[:top_k]

    def search(self, query: HybridSearchQuery) -> List[HybridSearchResult]:
        """Execute hybrid search using query vector and text query.

        Args:
            query: HybridSearchQuery object.

        Returns:
            List of HybridSearchResult items.
        """
        # 1. Fetch dense candidates from the configured vector store
        from ai_rag.schemas.vector_schemas import SearchQuery

        dense_query = SearchQuery(
            query_vector=query.query_vector,
            top_k=min(50, query.top_k * 3),  # Over-fetch for rank fusion candidate pool
            score_threshold=query.min_dense_score,
            subject_filter=query.subject_filter,
            topic_filter=query.topic_filter,
            document_id=query.document_id,
            owner_id=query.owner_id,
        )
        dense_results = self.vector_store.search_similar(dense_query)

        search_keyword_candidates = getattr(
            self.vector_store, "search_keyword_candidates", None
        )
        if search_keyword_candidates is not None:
            keyword_results = search_keyword_candidates(
                query_text=query.query_text,
                owner_id=query.owner_id,
                top_k=max(50, query.top_k * 10),
                subject_filter=query.subject_filter,
                topic_filter=query.topic_filter,
                document_id=query.document_id,
            )
        else:
            keyword_results = dense_results

        if not dense_results and not keyword_results:
            return []

        # Score lexical candidates independently of the dense-vector result set.
        candidate_by_id = {
            result.chunk_id: result
            for result in [*dense_results, *keyword_results]
        }
        docs_for_bm25 = [
            {"id": result.chunk_id, "text": result.text_snippet}
            for result in candidate_by_id.values()
        ]
        bm25_scores = self.bm25_scorer.compute_scores(query.query_text, docs_for_bm25)

        return self.reciprocal_rank_fusion(
            dense_results=dense_results,
            bm25_scores=bm25_scores,
            keyword_results=keyword_results,
            dense_weight=query.dense_weight,
            top_k=query.top_k,
            score_threshold=query.score_threshold,
        )
