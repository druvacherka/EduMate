"""Document processing pipeline orchestrator for EduMate RAG engine.

Integrates PDF parsing (PDFParser) and text chunking (TextChunker) into a
unified pipeline for processing single files or entire study material directories.
"""

import logging
import time
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from services.ai_rag.document_processing.pdf_parser import PDFParser, pdf_parser
from services.ai_rag.document_processing.text_chunker import TextChunker, text_chunker
from services.ai_rag.embeddings.gemini_embedder import GeminiEmbedder, gemini_embedder
from services.ai_rag.schemas.chunk_schemas import ChunkedDocument
from services.ai_rag.schemas.pdf_schemas import ParsedDocument
from services.ai_rag.vector_store.postgres_vector_store import PostgresVectorStore, postgres_vector_store

logger = logging.getLogger(__name__)


class ProcessedDocumentResult(BaseModel):
    """Result container for a single document processing pipeline run."""

    file_path: str = Field(..., description="Path to input PDF document")
    parsed_doc: ParsedDocument = Field(..., description="Page-level parsed PDF output")
    chunked_doc: ChunkedDocument = Field(..., description="Chunked text output")
    indexed_vectors_count: int = Field(
        0, ge=0, description="Number of vector embeddings stored in PostgreSQL"
    )
    processing_time_seconds: float = Field(
        ..., ge=0.0, description="Pipeline processing duration"
    )
    is_success: bool = Field(True, description="True if both parsing and chunking succeeded")


class DocumentProcessingPipeline:
    """Orchestrates PDF parsing, text chunking, embedding, and vector indexing.

    Attributes:
        parser: PDFParser instance.
        chunker: TextChunker instance.
        embedder: GeminiEmbedder instance.
        vector_store: PostgreSQL vector store instance.
    """

    def __init__(
        self,
        parser: Optional[PDFParser] = None,
        chunker: Optional[TextChunker] = None,
        embedder: Optional[GeminiEmbedder] = None,
        vector_store: Optional[PostgresVectorStore] = None,
    ) -> None:
        self.parser = parser or pdf_parser
        self.chunker = chunker or text_chunker
        self.embedder = embedder or gemini_embedder
        self.vector_store = vector_store or postgres_vector_store

    def process_pdf(self, file_path: str, owner_id: int) -> ProcessedDocumentResult:
        """Process a single PDF document through parsing and chunking stages.

        Args:
            file_path: Absolute or relative path to the PDF file.

        Returns:
            ProcessedDocumentResult containing parsed pages, chunks, and timing metadata.
        """
        start_time = time.perf_counter()
        logger.info(f"Starting pipeline execution for '{file_path}'")

        # Stage 1: Parse PDF text and metadata
        parsed_doc = self.parser.parse_document(file_path)

        if not parsed_doc.is_valid:
            duration = time.perf_counter() - start_time
            logger.error(
                f"Parsing failed for '{file_path}': {parsed_doc.error_message}"
            )
            return ProcessedDocumentResult(
                file_path=file_path,
                parsed_doc=parsed_doc,
                chunked_doc=ChunkedDocument(
                    document_name=Path(file_path).name,
                    total_chunks=0,
                    chunks=[],
                ),
                processing_time_seconds=duration,
                is_success=False,
            )

        # Stage 2: Recursive text chunking with overlap
        chunked_doc = self.chunker.chunk_document(parsed_doc)

        # Stage 3: Generate 768-dim Gemini embeddings
        indexed_count = 0
        if chunked_doc.chunks:
            embedding_batch = self.embedder.embed_chunks(chunked_doc.chunks)
            if self.vector_store and embedding_batch.vectors:
                # Stage 4: Index vectors in PostgreSQL
                indexed_count = self.vector_store.upsert_chunks(
                    chunks=chunked_doc.chunks,
                    vectors=embedding_batch.vectors,
                    document_name=chunked_doc.document_name,
                    owner_id=owner_id,
                )

        duration = time.perf_counter() - start_time
        logger.info(
            f"Pipeline complete for '{Path(file_path).name}': "
            f"{parsed_doc.metadata.total_pages} pages -> {chunked_doc.total_chunks} chunks -> "
            f"{indexed_count} indexed vectors in {duration:.3f}s"
        )

        return ProcessedDocumentResult(
            file_path=file_path,
            parsed_doc=parsed_doc,
            chunked_doc=chunked_doc,
            indexed_vectors_count=indexed_count,
            processing_time_seconds=duration,
            is_success=True,
        )

    def process_directory(self, dir_path: str, owner_id: int) -> List[ProcessedDocumentResult]:
        """Batch process all PDF files in a specified directory.

        Args:
            dir_path: Path to directory containing PDF study materials.

        Returns:
            List of ProcessedDocumentResult objects for each PDF found.
        """
        directory = Path(dir_path)

        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found or invalid: {dir_path}")
            return []

        pdf_files = list(directory.glob("*.pdf")) + list(directory.glob("*.PDF"))
        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {dir_path}")
            return []

        logger.info(
            f"Batch processing {len(pdf_files)} PDF documents in '{dir_path}'"
        )
        results: List[ProcessedDocumentResult] = []

        for pdf_file in pdf_files:
            result = self.process_pdf(str(pdf_file), owner_id=owner_id)
            results.append(result)

        successful = sum(1 for r in results if r.is_success)
        logger.info(
            f"Batch pipeline complete: {successful}/{len(results)} PDFs processed successfully"
        )

        return results


pipeline = DocumentProcessingPipeline()
