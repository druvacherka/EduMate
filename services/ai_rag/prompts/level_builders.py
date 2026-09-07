"""Intermediate and Advanced Socratic Prompt Engines and Level Factory for EduMate AI Tutor."""

import logging
from typing import List, Optional

from services.ai_rag.prompts.beginner_prompts import beginner_engine

logger = logging.getLogger(__name__)

# System-wide formatting rule enforced across all levels
MATH_FORMATTING_RULE = """
FORMATTING RULE:
- Format mathematical expressions using KaTeX display math blocks: $$\\mathbf{{Complexity:}}\\ \\mathcal{{O}}(n \\log n)$$.
- Format code blocks using syntax tags (e.g. ```cpp, ```python).
"""


class IntermediatePromptEngine:
    """Builds Socratic tutoring prompts for Intermediate students."""

    INTERMEDIATE_SYSTEM_TEMPLATE = """You are EduMate, a precise and engaging AI Personal Tutor.
Target Level: INTERMEDIATE STUDENT

PEDAGOGICAL STRATEGY FOR INTERMEDIATE STUDENTS:
1. Use standard computer science and engineering terminology with technical accuracy.
2. Include formal algorithmic complexity analysis (Big-O notation for Time and Auxiliary Space).
3. Provide clean, well-commented code snippets with appropriate syntax tags (e.g. ```cpp, ```python).
4. Explain algorithmic trade-offs (e.g., iterative vs recursive, array vs linked list).
5. Conclude with a practical problem-solving Socratic check question.

SUBJECT: {subject}
ACTIVE TOPIC: {topic}

{math_rule}
{language_instruction}
{weak_area_scaffolding}
"""

    def build_prompt(
        self,
        subject: str,
        topic: str,
        language: str = "English",
        weak_areas: Optional[List[str]] = None,
    ) -> str:
        """Construct an Intermediate system prompt for Gemini LLM."""
        language_instruction = self._get_language_instruction(language)
        weak_area_scaffolding = self._get_weak_area_scaffolding(weak_areas)

        return self.INTERMEDIATE_SYSTEM_TEMPLATE.format(
            subject=subject,
            topic=topic,
            math_rule=MATH_FORMATTING_RULE,
            language_instruction=language_instruction,
            weak_area_scaffolding=weak_area_scaffolding,
        ).strip()

    @staticmethod
    def _get_language_instruction(language: str) -> str:
        if language == "Hindi":
            return "LANGUAGE: Respond in technical Hindi (Devanagari script), preserving all standard technical terms in English."
        elif language == "Telugu":
            return "LANGUAGE: Respond in technical Telugu (Telugu script), preserving standard engineering terms in English."
        return "LANGUAGE: Respond in clear, precise technical English."

    @staticmethod
    def _get_weak_area_scaffolding(weak_areas: Optional[List[str]]) -> str:
        if not weak_areas:
            return ""
        return f"TARGETED PRACTICE: Address student weakness in: {', '.join(weak_areas)} with specific algorithmic step breakdowns."


class AdvancedPromptEngine:
    """Builds Socratic tutoring prompts for Advanced students."""

    ADVANCED_SYSTEM_TEMPLATE = """You are EduMate, a rigorous AI Personal Tutor for advanced engineering scholars.
Target Level: ADVANCED SCHOLAR

PEDAGOGICAL STRATEGY FOR ADVANCED STUDENTS:
1. Provide deep technical rigor, mathematical formulations, and formal complexity proofs.
2. Examine boundary conditions, edge cases, cache locality, memory management, and hardware trade-offs.
3. Use KaTeX display math formatting ($$<formula>$$) for mathematical proofs and recurrences.
4. Challenge assumptions and compare competing algorithmic approaches or data structure variants.
5. End with an open-ended advanced design or optimization Socratic challenge.

SUBJECT: {subject}
ACTIVE TOPIC: {topic}

{math_rule}
{language_instruction}
{weak_area_scaffolding}
"""

    def build_prompt(
        self,
        subject: str,
        topic: str,
        language: str = "English",
        weak_areas: Optional[List[str]] = None,
    ) -> str:
        """Construct an Advanced system prompt for Gemini LLM."""
        language_instruction = self._get_language_instruction(language)
        weak_area_scaffolding = self._get_weak_area_scaffolding(weak_areas)

        return self.ADVANCED_SYSTEM_TEMPLATE.format(
            subject=subject,
            topic=topic,
            math_rule=MATH_FORMATTING_RULE,
            language_instruction=language_instruction,
            weak_area_scaffolding=weak_area_scaffolding,
        ).strip()

    @staticmethod
    def _get_language_instruction(language: str) -> str:
        if language == "Hindi":
            return "LANGUAGE: Respond in academic Hindi (Devanagari script) with technical English domain terms."
        elif language == "Telugu":
            return "LANGUAGE: Respond in academic Telugu (Telugu script) with technical English domain terms."
        return "LANGUAGE: Respond in rigorous, high-level academic English."

    @staticmethod
    def _get_weak_area_scaffolding(weak_areas: Optional[List[str]]) -> str:
        if not weak_areas:
            return ""
        return f"ADVANCED RECTIFICATION: Challenge the student's edge-case understanding in: {', '.join(weak_areas)}."


class LevelPromptFactory:
    """Factory selecting and executing prompt engines based on learning level."""

    def __init__(self) -> None:
        self.beginner = beginner_engine
        self.intermediate = IntermediatePromptEngine()
        self.advanced = AdvancedPromptEngine()

    def get_system_prompt(
        self,
        level: str = "Beginner",
        subject: str = "Computer Science",
        topic: str = "Data Structures",
        language: str = "English",
        weak_areas: Optional[List[str]] = None,
    ) -> str:
        """Generate level-appropriate system prompt.

        Args:
            level: "Beginner", "Intermediate", or "Advanced".
            subject: Academic subject.
            topic: Active topic context.
            language: Target language.
            weak_areas: List of weak topics.

        Returns:
            Constructed system prompt string.
        """
        lvl_normalized = (level or "Beginner").capitalize()

        if lvl_normalized == "Intermediate":
            return self.intermediate.build_prompt(
                subject=subject, topic=topic, language=language, weak_areas=weak_areas
            )
        elif lvl_normalized == "Advanced":
            return self.advanced.build_prompt(
                subject=subject, topic=topic, language=language, weak_areas=weak_areas
            )
        else:
            return self.beginner.build_prompt(
                subject=subject, topic=topic, language=language, weak_areas=weak_areas
            )


prompt_factory = LevelPromptFactory()
