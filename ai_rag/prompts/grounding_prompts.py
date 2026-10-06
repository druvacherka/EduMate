"""Document Grounding Prompt Builder and Citation Fallback Handler for EduMate RAG.

Enforces strict factual grounding on retrieved PDF study materials, inline citation rules,
and fallback alert mechanisms when queries cannot be answered from context.
"""

from typing import List, Optional
from ai_rag.schemas.vector_schemas import SearchResult


GROUNDED_SYSTEM_PROMPT_TEMPLATE = """You are EduMate, an AI study assistant that prioritizes the student's uploaded study materials when available.

YOUR GROUNDING & CITATION RULES:
1. Treat retrieved study material as the source of truth for questions about uploaded documents. Read all supplied passages before answering; combine relevant passages when needed.
2. Answer the learner's question directly and clearly using the source. When useful, quote the exact relevant sentence or phrase verbatim, preserving its meaning, and then explain it in plain language. Do not turn a direct question into an unrelated Socratic dialogue.
3. Cite each source-based statement using exactly [Doc: <document_name>, Page <page_number>]. Only cite document names and page numbers present in the supplied context.
4. Never claim a passage says something it does not. Do not fill gaps with guesses or outside facts. If the requested answer is absent, say that it was not found in the supplied material.
5. If the learner explicitly selected a document and no relevant passage was retrieved, say you could not find the answer in that document. Do not substitute a general-knowledge answer.
6. Use prior conversation only to understand follow-up references; earlier assistant messages are not evidence and must not override the current retrieved passages.
7. Explain the evidence clearly and directly before adding optional teaching guidance. Acknowledge uncertainty rather than overstating what the source supports.
8. Format mathematical formulas using LaTeX ($...$ for inline, $$...$$ for display blocks).
"""


class GroundedPromptBuilder:
    """Builds grounded system prompts and context payload for RAG tutoring sessions."""

    def __init__(self, system_template: str = GROUNDED_SYSTEM_PROMPT_TEMPLATE) -> None:
        self.system_template = system_template

    def build_system_prompt(
        self,
        user_level: str = "Intermediate",
        response_language: Optional[str] = None,
    ) -> str:
        """Construct the grounded system prompt tailored to user learning level.

        Args:
            user_level: Beginner, Intermediate, or Advanced.

        Returns:
            Formatted system prompt string.
        """
        level_instruction = f"Target Learning Level: {user_level}. Adjust terminology depth accordingly."
        language_instruction = (
            f"Answer in {response_language}, while keeping important technical terms "
            "in English in parentheses."
            if response_language in ("Hindi", "Telugu")
            else ""
        )
        return "\n\n".join(
            part for part in (self.system_template, level_instruction, language_instruction) if part
        )

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
        document_scoped: bool = False,
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
            if document_scoped:
                return (
                    "The learner selected a specific uploaded document, but no relevant "
                    "passage was retrieved from it. Say that the answer was not found in "
                    "that document. Do not answer from general knowledge.\n\n"
                    f"User Question: {user_query}"
                )
            return (
                f"User Question: {user_query}\n\n"
                "No relevant uploaded study-material passages were retrieved. If the "
                "question asks about a document, be transparent that it cannot be verified "
                "from the uploaded material; otherwise answer from general knowledge "
                "without implying it came from a document."
            )

        context_str = self.build_context_block(context_chunks)
        return (
            f"{context_str}\n\n"
            f"User Question: {user_query}\n\n"
            "Answer directly from the supplied passages. Include brief exact quotations when useful, "
            "then explain the answer in clear language. Cite source-based claims as "
            "[Doc: <name>, Page <num>]:"
        )
