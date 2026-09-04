"""PyMuPDF (fitz) based PDF text extraction engine for EduMate RAG pipeline."""

import logging
import os
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from services.ai_rag.schemas.pdf_schemas import (
    PageContent,
    PDFMetadata,
    ParsedDocument,
)

logger = logging.getLogger(__name__)


class PDFParser:
    """Extracts text, metadata, and table indicators from PDF documents using PyMuPDF.

    Designed as the first stage of the RAG document processing pipeline.
    Produces structured ParsedDocument objects ready for downstream chunking.
    """

    SUPPORTED_EXTENSIONS: set[str] = {".pdf"}

    def parse_document(self, file_path: str) -> ParsedDocument:
        """Parse a PDF file and extract text content page by page.

        Args:
            file_path: Absolute or relative path to the PDF file.

        Returns:
            ParsedDocument with extracted pages, metadata, and validation status.
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"PDF file not found: {file_path}")
            return self._error_document(path.name, f"File not found: {file_path}")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file type: {path.suffix}")
            return self._error_document(
                path.name, f"Unsupported file type: {path.suffix}. Only PDF files are accepted."
            )

        try:
            doc = fitz.open(str(path))
        except Exception as exc:
            logger.error(f"Failed to open PDF '{file_path}': {exc}")
            return self._error_document(path.name, f"Failed to open PDF: {exc}")

        if doc.is_encrypted:
            doc.close()
            logger.warning(f"PDF is password-protected: {file_path}")
            return self._error_document(
                path.name, "PDF is password-protected and cannot be parsed."
            )

        try:
            metadata = self._extract_metadata(doc, path)
            pages = self._extract_all_pages(doc)
            total_chars = sum(page.char_count for page in pages)

            if total_chars == 0:
                logger.warning(f"PDF contains no extractable text: {file_path}")

            logger.info(
                f"Parsed '{path.name}': {metadata.total_pages} pages, "
                f"{total_chars} chars, {sum(1 for p in pages if p.has_tables)} pages with tables"
            )

            return ParsedDocument(
                metadata=metadata,
                pages=pages,
                total_chars=total_chars,
                is_valid=True,
            )
        except Exception as exc:
            logger.error(f"Error parsing PDF content '{file_path}': {exc}")
            return self._error_document(path.name, f"Error during text extraction: {exc}")
        finally:
            doc.close()

    def _extract_metadata(self, doc: fitz.Document, path: Path) -> PDFMetadata:
        """Extract document-level metadata from the PDF."""
        pdf_meta = doc.metadata or {}
        file_size = os.path.getsize(str(path))

        return PDFMetadata(
            file_name=path.name,
            title=pdf_meta.get("title") or None,
            author=pdf_meta.get("author") or None,
            total_pages=doc.page_count,
            file_size_bytes=file_size,
            creation_date=pdf_meta.get("creationDate") or None,
        )

    def _extract_all_pages(self, doc: fitz.Document) -> list[PageContent]:
        """Extract text content from every page in the document."""
        pages: list[PageContent] = []

        for page_idx in range(doc.page_count):
            page = doc.load_page(page_idx)
            page_content = self._extract_page_text(page, page_idx + 1)
            pages.append(page_content)

        return pages

    def _extract_page_text(self, page: fitz.Page, page_number: int) -> PageContent:
        """Extract and clean text from a single PDF page.

        Args:
            page: PyMuPDF page object.
            page_number: 1-indexed page number.

        Returns:
            PageContent with cleaned text and table detection flag.
        """
        raw_text = page.get_text("text")
        cleaned_text = self._normalize_whitespace(raw_text)
        has_tables = self._detect_tables(page)

        return PageContent(
            page_number=page_number,
            text=cleaned_text,
            has_tables=has_tables,
            char_count=len(cleaned_text),
        )

    def _detect_tables(self, page: fitz.Page) -> bool:
        """Detect whether a page contains table structures.

        Uses PyMuPDF's built-in table finder for reliable detection.

        Args:
            page: PyMuPDF page object.

        Returns:
            True if at least one table region was detected.
        """
        try:
            tables = page.find_tables()
            return len(tables.tables) > 0
        except Exception:
            # Table detection is best-effort; don't fail the entire parse
            return False

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """Clean extracted text by normalizing whitespace and removing artifacts.

        Args:
            text: Raw text extracted from PyMuPDF.

        Returns:
            Cleaned text with normalized spacing and line breaks.
        """
        if not text:
            return ""

        # Collapse multiple blank lines into double newlines (paragraph breaks)
        lines = text.splitlines()
        cleaned_lines: list[str] = []
        prev_blank = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if not prev_blank:
                    cleaned_lines.append("")
                prev_blank = True
            else:
                # Normalize internal whitespace within a line
                normalized = " ".join(stripped.split())
                cleaned_lines.append(normalized)
                prev_blank = False

        return "\n".join(cleaned_lines).strip()

    @staticmethod
    def _error_document(file_name: str, error_msg: str) -> ParsedDocument:
        """Create a ParsedDocument representing a failed parse attempt."""
        return ParsedDocument(
            metadata=PDFMetadata(
                file_name=file_name,
                total_pages=0,
                file_size_bytes=0,
            ),
            pages=[],
            total_chars=0,
            is_valid=False,
            error_message=error_msg,
        )


pdf_parser = PDFParser()
