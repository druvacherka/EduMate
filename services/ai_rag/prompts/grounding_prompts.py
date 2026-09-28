"""Document Grounding Prompt Builder and Citation Fallback Handler for EduMate RAG.

Enforces strict factual grounding on retrieved PDF study materials, inline citation rules,
and fallback alert mechanisms when queries cannot be answered from context.
"""

from typing import List, Optional
from services.ai_rag.schemas.vector_schemas import SearchResult


GROUNDED_SYSTEM_PROMPT_TEMPLATE = """You are EduMate, an AI Socratic Tutor grounded strictly in the provided study material context.

YOUR GROUNDING & CITATION RULES:
1. Base your answer EXCLUSIVELY on the provided Study Material Context below.
2. For EVERY statement, fact, theorem, or explanation derived from the text, you MUST append an inline citation in the exact format: [Doc: <document_name>, Page <page_number>].
3. If the user's question CANNOT be answered using the provided Study Material Context, reply with the EXACT statement:
   "Information not found in study material. Would you like me to explain this using general domain knowledge instead?"
4. Do NOT make up facts, hallucinate, or reference external information unless explicitly requested by the user.
5. Maintain an encouraging Socratic tone, encouraging critical thinking while adhering to the study material.
6. Format mathematical formulas using LaTeX ($...$ for inline, $$...$$ for display blocks).
"""

FALLBACK_UNGROUNDED_MESSAGE = (
    "Information not found in study material. "
    "Would you like me to explain this using general domain knowledge instead?"
)


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
