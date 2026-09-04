"""Document processing package for EduMate AI RAG Engine.

Provides PDF parsing (PyMuPDF), recursive text chunking, and pipeline orchestration.
"""

from services.ai_rag.document_processing.pdf_parser import PDFParser, pdf_parser
from services.ai_rag.document_processing.text_chunker import TextChunker, text_chunker
from services.ai_rag.document_processing.pipeline import (
    DocumentProcessingPipeline,
    ProcessedDocumentResult,
    pipeline,
)

__all__ = [
    "PDFParser",
    "pdf_parser",
    "TextChunker",
    "text_chunker",
    "DocumentProcessingPipeline",
    "ProcessedDocumentResult",
    "pipeline",
]
