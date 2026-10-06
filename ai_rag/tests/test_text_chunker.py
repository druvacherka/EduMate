"""Unit tests for recursive section-aware TextChunker in EduMate RAG engine."""

import pytest

from ai_rag.document_processing.text_chunker import TextChunker, text_chunker
from ai_rag.schemas.chunk_schemas import ChunkedDocument, TextChunk
from ai_rag.schemas.pdf_schemas import PageContent, PDFMetadata, ParsedDocument


def test_chunk_document_basic():
    parsed_doc = ParsedDocument(
        metadata=PDFMetadata(
            file_name="ds_notes.pdf",
            total_pages=1,
            file_size_bytes=1024,
        ),
        pages=[
            PageContent(
                page_number=1,
                text=(
                    "Chapter 1: Binary Search Trees\n\n"
                    "A Binary Search Tree (BST) is a node-based binary tree data structure. "
                    "The left subtree of a node contains only nodes with keys lesser than the node's key. "
                    "The right subtree of a node contains only nodes with keys greater than the node's key."
                ),
                has_tables=False,
                headers=["Chapter 1: Binary Search Trees"],
                char_count=280,
            )
        ],
        total_chars=280,
        is_valid=True,
    )

    chunker = TextChunker(chunk_size=150, chunk_overlap=30)
    chunked_doc = chunker.chunk_document(parsed_doc)

    assert isinstance(chunked_doc, ChunkedDocument)
    assert chunked_doc.document_name == "ds_notes.pdf"
    assert chunked_doc.total_chunks > 1

    first_chunk = chunked_doc.chunks[0]
    assert isinstance(first_chunk, TextChunk)
    assert first_chunk.page_number == 1
    assert "Chapter 1: Binary Search Trees" in first_chunk.section_hierarchy


def test_section_hierarchy_retention():
    parsed_doc = ParsedDocument(
        metadata=PDFMetadata(
            file_name="algorithms.pdf",
            total_pages=2,
            file_size_bytes=2048,
        ),
        pages=[
            PageContent(
                page_number=1,
                text="Chapter 2: Sorting Algorithms\n\nSection 2.1 Quick Sort is a divide and conquer algorithm.",
                has_tables=False,
                headers=["Chapter 2: Sorting Algorithms", "Section 2.1 Quick Sort"],
                char_count=85,
            ),
            PageContent(
                page_number=2,
                text="Section 2.2 Merge Sort is an O(n log n) comparison-based sorting algorithm.",
                has_tables=False,
                headers=["Section 2.2 Merge Sort"],
                char_count=82,
            ),
        ],
        total_chars=167,
        is_valid=True,
    )

    chunker = TextChunker(chunk_size=300, chunk_overlap=50)
    chunked_doc = chunker.chunk_document(parsed_doc)

    assert chunked_doc.total_chunks == 2
    page1_chunk = chunked_doc.chunks[0]
    page2_chunk = chunked_doc.chunks[1]

    assert "Chapter 2: Sorting Algorithms" in page1_chunk.section_hierarchy
    assert "Section 2.1 Quick Sort" in page1_chunk.section_hierarchy
    assert "Section 2.2 Merge Sort" in page2_chunk.section_hierarchy


def test_table_detection_in_chunk():
    table_text = (
        "Here is the time complexity comparison:\n\n"
        "[Extracted Tables]\n"
        "| Algorithm | Average | Worst |\n"
        "| --- | --- | --- |\n"
        "| QuickSort | O(n log n) | O(n^2) |"
    )

    parsed_doc = ParsedDocument(
        metadata=PDFMetadata(
            file_name="complexity.pdf",
            total_pages=1,
            file_size_bytes=512,
        ),
        pages=[
            PageContent(
                page_number=1,
                text=table_text,
                has_tables=True,
                table_snippets=["| Algorithm | Average | Worst |\n| --- | --- | --- |\n| QuickSort | O(n log n) | O(n^2) |"],
                headers=[],
                char_count=len(table_text),
            )
        ],
        total_chars=len(table_text),
        is_valid=True,
    )

    chunker = TextChunker(chunk_size=500, chunk_overlap=50)
    chunked_doc = chunker.chunk_document(parsed_doc)

    assert chunked_doc.total_chunks == 1
    chunk = chunked_doc.chunks[0]
    assert chunk.has_table is True


def test_chunker_preserves_sentence_and_paragraph_separators():
    parsed_doc = ParsedDocument(
        metadata=PDFMetadata(file_name="separators.pdf", total_pages=1, file_size_bytes=128),
        pages=[
            PageContent(
                page_number=1,
                text=(
                    "First sentence explains the source. Second sentence preserves its ending. "
                    "Third sentence remains intact.\n\nA separate paragraph keeps its boundary."
                ),
                char_count=149,
            )
        ],
        total_chars=149,
    )

    chunker = TextChunker(chunk_size=100, chunk_overlap=0)
    chunks = chunker._recursive_split(parsed_doc.pages[0].text)

    assert len(chunks) > 1
    assert "".join(chunks) == parsed_doc.pages[0].text
