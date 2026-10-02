"""Unit tests for PyMuPDF PDFParser in EduMate RAG engine."""

import os
from unittest.mock import MagicMock, patch

import pytest

from services.ai_rag.document_processing.pdf_parser import PDFParser, pdf_parser
from services.ai_rag.schemas.pdf_schemas import ParsedDocument


def test_parse_missing_file():
    parser = PDFParser()
    result = parser.parse_document("non_existent_file.pdf")

    assert isinstance(result, ParsedDocument)
    assert not result.is_valid
    assert "File not found" in (result.error_message or "")


def test_parse_invalid_extension():
    parser = PDFParser()
    result = parser.parse_document("document.txt")

    assert isinstance(result, ParsedDocument)
    assert not result.is_valid
    assert "Unsupported file type" in (result.error_message or "")


def test_normalize_whitespace():
    raw_text = "  Chapter 1:  Data  Structures   \n\n\n\n  Section 1.1   Arrays   "
    cleaned = PDFParser._normalize_whitespace(raw_text)

    assert "Chapter 1: Data Structures" in cleaned
    assert "Section 1.1 Arrays" in cleaned
    assert "\n\n" in cleaned  # Preserves paragraph break


def test_extract_table_snippets_mock():
    parser = PDFParser()
    mock_page = MagicMock()

    # Mock table finder output
    mock_table = MagicMock()
    mock_table.extract.return_value = [
        ["Header A", "Header B"],
        ["Val 1", "Val 2"],
    ]
    mock_tabs = MagicMock()
    mock_tabs.tables = [mock_table]
    mock_page.find_tables.return_value = mock_tabs

    snippets = parser._extract_table_snippets(mock_page)

    assert len(snippets) == 1
    assert "| Header A | Header B |" in snippets[0]
    assert "| --- | --- |" in snippets[0]
    assert "| Val 1 | Val 2 |" in snippets[0]


def test_extract_headers_mock():
    parser = PDFParser()
    mock_page = MagicMock()

    # Mock get_text("dict", ...) output with prominent font size
    dict_output = {
        "blocks": [
            {
                "type": 0,
                "lines": [
                    {
                        "spans": [
                            {"text": "CHAPTER 1: BINARY TREES", "size": 18.0, "flags": 2}
                        ]
                    }
                ],
            },
            {
                "type": 0,
                "lines": [
                    {
                        "spans": [
                            {"text": "This is standard body paragraph text.", "size": 10.0, "flags": 0}
                        ]
                    }
                ],
            },
        ]
    }
    mock_page.get_text.side_effect = lambda *args, **kwargs: dict_output if args and args[0] == "dict" else ""

    headers = parser._extract_headers(mock_page)

    assert len(headers) == 1
    assert headers[0] == "CHAPTER 1: BINARY TREES"
