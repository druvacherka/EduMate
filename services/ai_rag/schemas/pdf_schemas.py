"""Pydantic v2 schemas for PDF document parsing and text extraction."""

from typing import List, Optional
from pydantic import BaseModel, Field


class PageContent(BaseModel):
    """Extracted content from a single PDF page."""

    page_number: int = Field(..., ge=1, description="1-indexed page number")
    text: str = Field(..., description="Extracted plain text from the page")
    has_tables: bool = Field(False, description="Whether tables were detected on this page")
    table_snippets: List[str] = Field(
        default_factory=list, description="Markdown formatted table snippets extracted from the page"
    )
    headers: List[str] = Field(
        default_factory=list, description="Structural headings detected on this page"
    )
    char_count: int = Field(..., ge=0, description="Character count of extracted text")


class PDFMetadata(BaseModel):
    """Document-level metadata extracted from the PDF file."""

    file_name: str = Field(..., description="Original filename of the uploaded PDF")
    title: Optional[str] = Field(None, description="PDF metadata title field")
    author: Optional[str] = Field(None, description="PDF metadata author field")
    total_pages: int = Field(0, ge=0, description="Total number of pages in the PDF")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")
    creation_date: Optional[str] = Field(None, description="PDF creation date if available")


class ParsedDocument(BaseModel):
    """Complete parsed representation of a PDF document."""

    metadata: PDFMetadata = Field(..., description="Document-level metadata")
    pages: List[PageContent] = Field(
        default_factory=list, description="Extracted content for each page"
    )
    total_chars: int = Field(0, ge=0, description="Total character count across all pages")
    is_valid: bool = Field(True, description="False if parsing encountered critical errors")
    error_message: Optional[str] = Field(
        None, description="Error description if parsing failed"
    )
