"""Qdrant Vector Store package for EduMate RAG Knowledge Engine."""

from services.ai_rag.vector_store.qdrant_client import QdrantVectorStore, qdrant_store

__all__ = ["QdrantVectorStore", "qdrant_store"]
