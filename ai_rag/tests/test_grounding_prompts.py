"""Unit tests for Document Grounding Prompt Builder and fallback alert pipeline."""

import pytest
from ai_rag.prompts.grounding_prompts import (
    GroundedPromptBuilder,
)
from ai_rag.schemas.vector_schemas import SearchResult


def test_grounded_system_prompt_builder():
    builder = GroundedPromptBuilder()
    sys_prompt = builder.build_system_prompt(user_level="Beginner")

    assert "EduMate" in sys_prompt
    assert "When Study Material Context is provided" in sys_prompt
    assert "general knowledge" in sys_prompt
    assert "[Doc: <document_name>, Page <page_number>]" in sys_prompt
    assert "Target Learning Level: Beginner" in sys_prompt


def test_build_context_block_with_chunks():
    builder = GroundedPromptBuilder()
    chunks = [
        SearchResult(
            chunk_id="c1",
            score=0.91,
            document_name="Data_Structures.pdf",
            page_number=14,
            text_snippet="Binary search trees maintain sorted node keys.",
            section_title="BST Overview",
        ),
        SearchResult(
            chunk_id="c2",
            score=0.88,
            document_name="Data_Structures.pdf",
            page_number=15,
            text_snippet="Tree insertion operates in O(log n) time average.",
            section_title="BST Operations",
        ),
    ]

    context_str = builder.build_context_block(chunks)
    assert "=== STUDY MATERIAL CONTEXT ===" in context_str
    assert "Document: Data_Structures.pdf | Page: 14 | Section: BST Overview" in context_str
    assert "Binary search trees maintain sorted node keys." in context_str


def test_build_context_block_empty():
    builder = GroundedPromptBuilder()
    context_str = builder.build_context_block([])
    assert "None available" in context_str


def test_assemble_grounded_prompt():
    builder = GroundedPromptBuilder()
    chunks = [
        SearchResult(
            chunk_id="c1",
            score=0.95,
            document_name="Algorithms.pdf",
            page_number=42,
            text_snippet="Dijkstra's algorithm finds shortest paths in non-negative weighted graphs.",
            section_title="Graph Algorithms",
        )
    ]

    prompt = builder.assemble_grounded_prompt(
        user_query="How does Dijkstra's algorithm work?",
        context_chunks=chunks,
        user_level="Advanced",
    )

    assert "Document: Algorithms.pdf | Page: 42" in prompt
    assert "How does Dijkstra's algorithm work?" in prompt
    assert "Provide a grounded, step-by-step Socratic answer with inline citations" in prompt
