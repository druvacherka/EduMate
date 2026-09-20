"""PyMuPDF (fitz) based PDF text extraction engine for EduMate RAG pipeline."""

import logging
import os
from pathlib import Path
from typing import Optional

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    fitz = None
    FITZ_AVAILABLE = False

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

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file type: {path.suffix}")
            return self._error_document(
                path.name, f"Unsupported file type: {path.suffix}. Only PDF files are accepted."
            )

        if not path.exists():
            logger.error(f"PDF file not found: {file_path}")
            return self._error_document(path.name, f"File not found: {file_path}")

        if not FITZ_AVAILABLE or fitz is None:
            logger.error("PyMuPDF (fitz) library is not installed.")
            return self._error_document(path.name, "PyMuPDF (fitz) library is not installed.")

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
        """Extract and clean text, structural headers, and tables from a single PDF page.

        Args:
            page: PyMuPDF page object.
            page_number: 1-indexed page number.

        Returns:
            PageContent with cleaned text, detected headers, and markdown table snippets.
        """
        raw_text = page.get_text("text")
        cleaned_text = self._normalize_whitespace(raw_text)
        headers = self._extract_headers(page)
        table_snippets = self._extract_table_snippets(page)
        has_tables = len(table_snippets) > 0 or self._detect_tables(page)

        # Append formatted table markdown to page text for context continuity
        if table_snippets:
            tables_combined = "\n\n".join(table_snippets)
            cleaned_text = f"{cleaned_text}\n\n[Extracted Tables]\n{tables_combined}".strip()

        return PageContent(
            page_number=page_number,
            text=cleaned_text,
            has_tables=has_tables,
            table_snippets=table_snippets,
            headers=headers,
            char_count=len(cleaned_text),
        )

    def _extract_headers(self, page: fitz.Page) -> list[str]:
        """Extract structural header candidate strings from PDF page using font/layout cues.

        Args:
            page: PyMuPDF page object.

        Returns:
            List of detected section header titles.
        """
        headers: list[str] = []
        try:
            dehyphenate_flag = getattr(fitz, "TEXT_DEHYPHENATE", 0) if fitz else 0
            page_dict = page.get_text("dict", flags=dehyphenate_flag) if hasattr(page, "get_text") else {}
            if isinstance(page_dict, str):
                page_dict = {}
            blocks = page_dict.get("blocks", [])

            # Compute average font size across spans to identify prominent header fonts
            font_sizes: list[float] = []
            for b in blocks:
                if b.get("type") == 0:  # Text block
                    for line in b.get("lines", []):
                        for span in line.get("spans", []):
                            if span.get("text", "").strip():
                                font_sizes.append(span.get("size", 10.0))

            avg_size = (sum(font_sizes) / len(font_sizes)) if font_sizes else 10.0
            header_threshold = avg_size * 1.15  # Spans 15% larger than average font

            for b in blocks:
                if b.get("type") == 0:
                    for line in b.get("lines", []):
                        line_text = "".join(s.get("text", "") for s in line.get("spans", [])).strip()
                        if not line_text:
                            continue
                        max_span_size = max((s.get("size", 0.0) for s in line.get("spans", [])), default=0.0)
                        is_bold = any(s.get("flags", 0) & 2 for s in line.get("spans", []))

                        if (max_span_size >= header_threshold or is_bold) and len(line_text) <= 120:
                            if line_text not in headers:
                                headers.append(line_text)
        except Exception as exc:
            logger.debug(f"Header extraction fallback: {exc}")

        return headers

    def _extract_table_snippets(self, page: fitz.Page) -> list[str]:
        """Extract table structures from page and format as Markdown tables.

        Args:
            page: PyMuPDF page object.

        Returns:
            List of Markdown formatted table strings.
        """
        table_markdowns: list[str] = []
        try:
            tabs = page.find_tables()
            for tab in tabs.tables:
                data = tab.extract()
                if not data or len(data) < 1:
                    continue

                # Format rows into Markdown syntax
                md_rows: list[str] = []
                headers = [str(cell or "").strip().replace("\n", " ") for cell in data[0]]
                md_rows.append("| " + " | ".join(headers) + " |")
                md_rows.append("| " + " | ".join(["---"] * len(headers)) + " |")

                for row in data[1:]:
                    cells = [str(cell or "").strip().replace("\n", " ") for cell in row]
                    md_rows.append("| " + " | ".join(cells) + " |")

                table_md = "\n".join(md_rows)
                table_markdowns.append(table_md)
        except Exception as exc:
            logger.debug(f"Table markdown extraction fallback: {exc}")

        return table_markdowns

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
