"""Document Grounding Prompt Builder and Citation Fallback Handler for EduMate RAG.

Enforces strict factual grounding on retrieved PDF study materials, inline citation rules,
and fallback alert mechanisms when queries cannot be answered from context.
"""

from typing import List, Optional
from ai_rag.schemas.vector_schemas import SearchResult


GROUNDED_SYSTEM_PROMPT_TEMPLATE = """You are EduMate, an AI Socratic Tutor that prioritizes the student's uploaded study materials when available.

YOUR GROUNDING & CITATION RULES:
1. When Study Material Context is provided, ground factual claims in it and append inline citations in the exact format: [Doc: <document_name>, Page <page_number>].
2. When no relevant Study Material Context is provided, answer the student's question using your general knowledge, and do not invent study-material citations.
3. Be accurate, acknowledge uncertainty, and distinguish general knowledge from information found in uploaded material.
4. Maintain an encouraging Socratic tone that guides the student to think critically.
5. Format mathematical formulas using LaTeX ($...$ for inline, $$...$$ for display blocks).
"""


class GroundedPromptBuilder:
    """Builds grounded system prompts and context payload for RAG tutoring sessions."""

    def __init__(self, system_template: str = GROUNDED_SYSTEM_PROMPT_TEMPLATE) -> None:
        self.system_template = system_template

    def build_system_prompt(self, user_level: str = "Intermediate") -> str:
        """Construct the grounded system prompt tailored to user learning level.

        Args:
            user_level: Beginner, Intermediate, or Advanced.

        Returns:
            Formatted system prompt string.
        """
        level_instruction = f"Target Learning Level: {user_level}. Adjust terminology depth accordingly."
        return f"{self.system_template}\n\n{level_instruction}"

    def build_context_block(self, context_chunks: List[SearchResult]) -> str:
        """Format retrieved search result chunks into a structured context string.

        Args:
            context_chunks: List of SearchResult objects from RAG vector/hybrid search.

        Returns:
            Formatted context block string with document metadata header tags.
        """
        if not context_chunks:
            return "STUDY MATERIAL CONTEXT: None available."

        formatted_blocks = ["=== STUDY MATERIAL CONTEXT ==="]
        for idx, chunk in enumerate(context_chunks, start=1):
            sec_header = f" | Section: {chunk.section_title}" if chunk.section_title else ""
            block_meta = f"[{idx}] Document: {chunk.document_name} | Page: {chunk.page_number}{sec_header}"
            formatted_blocks.append(f"{block_meta}\n{chunk.text_snippet.strip()}\n")

        formatted_blocks.append("==============================")
        return "\n".join(formatted_blocks)

    def assemble_grounded_prompt(
        self,
        user_query: str,
        context_chunks: List[SearchResult],
        user_level: str = "Intermediate",
    ) -> str:
        """Assemble complete grounded prompt including system rules, context, and query.

        Args:
            user_query: Student input question.
            context_chunks: Retrieved document snippet chunks.
            user_level: Student proficiency level.

        Returns:
            Complete prompt string for LLM completion.
        """
        if not context_chunks:
            # Fallback path when no grounded context is retrieved
            return f"User Question: {user_query}\n\nNote: No relevant study material context was retrieved."

        context_str = self.build_context_block(context_chunks)
        return (
            f"{context_str}\n\n"
            f"User Question: {user_query}\n\n"
            "Provide a grounded, step-by-step Socratic answer with inline citations [Doc: <name>, Page <num>]:"
        )
