"""PostgreSQL vector store package for EduMate RAG Knowledge Engine."""

from services.ai_rag.vector_store.postgres_vector_store import PostgresVectorStore, postgres_vector_store

__all__ = ["PostgresVectorStore", "postgres_vector_store"]
