"""Recursive text chunking engine for EduMate RAG pipeline.

Splits extracted PDF text into overlapping, section-aware chunks suitable
for embedding and vector store ingestion.
"""

import logging
import re
from typing import Optional

from services.ai_rag.schemas.chunk_schemas import (
    ChunkedDocument,
    ChunkingConfig,
    TextChunk,
)
from services.ai_rag.schemas.pdf_schemas import ParsedDocument

logger = logging.getLogger(__name__)

# Regex patterns for detecting section headings
_HEADING_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^#{1,4}\s+.+"),                           # Markdown headings
    re.compile(r"^\d+\.\d*\s+[A-Z]"),                      # Numbered sections (1.2 Title)
    re.compile(r"^(?:Chapter|Section|Part)\s+\d+", re.I),  # Chapter/Section labels
    re.compile(r"^[A-Z][A-Z\s]{4,}$"),                     # ALL-CAPS titles (min 5 chars)
]


class TextChunker:
    """Splits parsed PDF documents into overlapping text chunks for RAG embedding.

    Uses recursive splitting: tries larger separators first (paragraph breaks),
    then falls back to smaller ones (sentences, words) to maintain semantic
    coherence within each chunk.

    Attributes:
        config: Chunking configuration (chunk_size, overlap, separators).
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ) -> None:
        self.config = ChunkingConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk_document(self, parsed_doc: ParsedDocument) -> ChunkedDocument:
        """Split all pages of a parsed document into overlapping text chunks.

        Args:
            parsed_doc: Output from PDFParser.parse_document().

        Returns:
            ChunkedDocument containing ordered chunks with metadata.
        """
        if not parsed_doc.is_valid:
            logger.warning(
                f"Skipping invalid document: {parsed_doc.metadata.file_name}"
            )
            return ChunkedDocument(
                document_name=parsed_doc.metadata.file_name,
                total_chunks=0,
                chunks=[],
                chunking_config=self.config,
            )

        doc_name = parsed_doc.metadata.file_name
        all_chunks: list[TextChunk] = []
        chunk_index = 0

        for page in parsed_doc.pages:
            if not page.text.strip():
                continue

            page_chunks = self._split_page_text(
                text=page.text,
                page_number=page.page_number,
                doc_name=doc_name,
                start_index=chunk_index,
            )
            all_chunks.extend(page_chunks)
            chunk_index += len(page_chunks)

        logger.info(
            f"Chunked '{doc_name}': {len(all_chunks)} chunks from "
            f"{parsed_doc.metadata.total_pages} pages "
            f"(chunk_size={self.config.chunk_size}, overlap={self.config.chunk_overlap})"
        )

        return ChunkedDocument(
            document_name=doc_name,
            total_chunks=len(all_chunks),
            chunks=all_chunks,
            chunking_config=self.config,
        )

    def _split_page_text(
        self,
        text: str,
        page_number: int,
        doc_name: str,
        start_index: int,
    ) -> list[TextChunk]:
        """Split a single page's text into chunks with overlap.

        Args:
            text: Full text of the page.
            page_number: 1-indexed page number.
            doc_name: Document filename for chunk ID generation.
            start_index: Global chunk index offset.

        Returns:
            List of TextChunk objects for this page.
        """
        raw_segments = self._recursive_split(text, separator_index=0)
        return self._merge_with_overlap(
            segments=raw_segments,
            page_number=page_number,
            doc_name=doc_name,
            start_index=start_index,
        )

    def _recursive_split(self, text: str, separator_index: int = 0) -> list[str]:
        """Recursively split text using hierarchical separators.

        Tries the largest separator first (paragraph breaks). If any resulting
        segment still exceeds chunk_size, recursively splits it with the next
        finer separator.

        Args:
            text: Text to split.
            separator_index: Current index into self.config.separators.

        Returns:
            List of text segments, each at or below chunk_size.
        """
        if not text.strip():
            return []

        if len(text) <= self.config.chunk_size:
            return [text.strip()] if text.strip() else []

        # If we've exhausted all separators, force-split by chunk_size
        if separator_index >= len(self.config.separators):
            return self._force_split(text)

        separator = self.config.separators[separator_index]
        parts = text.split(separator)

        segments: list[str] = []
        for part in parts:
            stripped = part.strip()
            if not stripped:
                continue

            if len(stripped) <= self.config.chunk_size:
                segments.append(stripped)
            else:
                # Recursively split with next finer separator
                sub_segments = self._recursive_split(stripped, separator_index + 1)
                segments.extend(sub_segments)

        return segments

    def _force_split(self, text: str) -> list[str]:
        """Force-split text into fixed-size segments as a last resort.

        Args:
            text: Text that couldn't be split by any separator.

        Returns:
            List of segments, each at most chunk_size characters.
        """
        segments: list[str] = []
        for i in range(0, len(text), self.config.chunk_size):
            segment = text[i : i + self.config.chunk_size].strip()
            if segment:
                segments.append(segment)
        return segments

    def _merge_with_overlap(
        self,
        segments: list[str],
        page_number: int,
        doc_name: str,
        start_index: int,
    ) -> list[TextChunk]:
        """Merge small segments into chunks and apply overlap between them.

        Greedily combines consecutive segments until adding the next would
        exceed chunk_size, then starts a new chunk with overlap from the
        tail of the previous one.

        Args:
            segments: Pre-split text segments.
            page_number: Source page number.
            doc_name: Document filename.
            start_index: Global chunk index offset.

        Returns:
            List of TextChunk objects with overlap applied.
        """
        if not segments:
            return []

        chunks: list[TextChunk] = []
        current_parts: list[str] = []
        current_len = 0

        for segment in segments:
            seg_len = len(segment)

            # If adding this segment would exceed chunk_size, finalize current chunk
            if current_parts and (current_len + seg_len + 1) > self.config.chunk_size:
                chunk_text = " ".join(current_parts)
                section = self._detect_section_title(chunk_text)
                chunk_idx = start_index + len(chunks)

                chunks.append(
                    TextChunk(
                        chunk_id=f"{doc_name}_chunk_{chunk_idx:04d}",
                        text=chunk_text,
                        page_number=page_number,
                        section_title=section,
                        char_count=len(chunk_text),
                        token_estimate=len(chunk_text) // 4,
                    )
                )

                # Start new chunk with overlap from tail of previous
                overlap_parts = self._get_overlap_parts(current_parts)
                current_parts = overlap_parts
                current_len = sum(len(p) for p in current_parts) + max(
                    0, len(current_parts) - 1
                )

            current_parts.append(segment)
            current_len += seg_len + (1 if len(current_parts) > 1 else 0)

        # Finalize the last chunk
        if current_parts:
            chunk_text = " ".join(current_parts)
            section = self._detect_section_title(chunk_text)
            chunk_idx = start_index + len(chunks)

            chunks.append(
                TextChunk(
                    chunk_id=f"{doc_name}_chunk_{chunk_idx:04d}",
                    text=chunk_text,
                    page_number=page_number,
                    section_title=section,
                    char_count=len(chunk_text),
                    token_estimate=len(chunk_text) // 4,
                )
            )

        return chunks

    def _get_overlap_parts(self, parts: list[str]) -> list[str]:
        """Extract trailing parts from the previous chunk for overlap.

        Takes segments from the tail until their combined length reaches
        the configured overlap size.

        Args:
            parts: Segments of the previous chunk.

        Returns:
            Subset of trailing segments for overlap.
        """
        if self.config.chunk_overlap <= 0:
            return []

        overlap_parts: list[str] = []
        overlap_len = 0

        for part in reversed(parts):
            if overlap_len + len(part) > self.config.chunk_overlap:
                break
            overlap_parts.insert(0, part)
            overlap_len += len(part)

        return overlap_parts

    @staticmethod
    def _detect_section_title(text: str) -> Optional[str]:
        """Detect if the chunk begins with a section heading.

        Checks the first line of the chunk against known heading patterns
        (Markdown headings, numbered sections, chapter labels, ALL-CAPS titles).

        Args:
            text: Full chunk text.

        Returns:
            Detected section title string, or None.
        """
        first_line = text.split("\n", maxsplit=1)[0].strip()
        if not first_line:
            return None

        for pattern in _HEADING_PATTERNS:
            if pattern.match(first_line):
                # Strip markdown heading markers for clean title
                clean_title = re.sub(r"^#{1,4}\s+", "", first_line).strip()
                return clean_title

        return None


text_chunker = TextChunker()
