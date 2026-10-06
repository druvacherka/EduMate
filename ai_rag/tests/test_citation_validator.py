"""Unit tests for Citation Validator, source mapping, and grounding verification."""

import pytest
from ai_rag.schemas.vector_schemas import SearchResult
from ai_rag.validators.citation_validator import CitationValidator


def test_extract_inline_citations():
    validator = CitationValidator()
    text = (
        "Matrix multiplication requires matching inner dimensions [Doc: Linear_Algebra.pdf, Page 12]. "
        "The determinant indicates invertibility [Doc: Linear_Algebra.pdf, Page 15]."
    )

    citations = validator.extract_citations(text)
    assert len(citations) == 2
    assert citations[0].document_name == "Linear_Algebra.pdf"
    assert citations[0].page_number == 12
    assert citations[1].page_number == 15


def test_validate_and_format_grounded():
    validator = CitationValidator()
    context = [
        SearchResult(
            chunk_id="c1",
            score=0.9,
            document_name="Physics.pdf",
            page_number=5,
            text_snippet="Kinematic equations describe motion under constant acceleration.",
        )
    ]

    llm_output = (
        "Kinematic equations are used for motion under constant acceleration [Doc: Physics.pdf, Page 5]."
    )

    res = validator.validate_and_format(llm_output, context)
    assert res.is_grounded is True
    assert res.fallback_triggered is False
    assert res.confidence_score == 1.0
    assert "### 📖 Verified Study Material References" in res.formatted_response
    assert "**Physics.pdf** (Page 5)" in res.formatted_response


def test_validate_and_format_fallback_triggered():
    validator = CitationValidator()
    context = [
        SearchResult(
            chunk_id="c1",
            score=0.3,
            document_name="Chemistry.pdf",
            page_number=2,
            text_snippet="Organic chemistry covers carbon compounds.",
        )
    ]

    llm_output = "Information not found in study material. Would you like me to explain this using general domain knowledge instead?"

    res = validator.validate_and_format(llm_output, context)
    assert res.is_grounded is False
    assert res.fallback_triggered is True
    assert res.confidence_score == 0.0


def test_validate_and_format_rejects_uncited_answer_with_context():
    validator = CitationValidator()
    context = [
        SearchResult(
            chunk_id="c1",
            score=0.9,
            document_name="Physics.pdf",
            page_number=5,
            text_snippet="Kinematic equations describe motion under constant acceleration.",
        )
    ]

    result = validator.validate_and_format("Kinematic equations describe motion.", context)

    assert result.is_grounded is False
    assert result.fallback_triggered is True
    assert result.parsed_citations == []


def test_validate_and_format_removes_citation_not_in_retrieved_context():
    validator = CitationValidator()
    context = [
        SearchResult(
            chunk_id="c1",
            score=0.9,
            document_name="Physics.pdf",
            page_number=5,
            text_snippet="Kinematic equations describe motion under constant acceleration.",
        )
    ]

    result = validator.validate_and_format(
        "Motion is described here [Doc: Unknown.pdf, Page 99].",
        context,
    )

    assert result.fallback_triggered is True
    assert result.parsed_citations == []
    assert "Unknown.pdf" not in result.formatted_response
