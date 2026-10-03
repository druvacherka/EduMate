"""Beginner-level Socratic Prompt Engine and Relatable Analogy System for EduMate AI Tutor."""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Pre-defined domain analogies for core computer science & engineering concepts
CONCEPT_ANALOGIES: Dict[str, str] = {
    "binary search tree": "A library catalog where books are split into left (smaller call numbers) and right (larger call numbers) sections, letting you find any book byhalving your search every step.",
    "recursion": "Russian nesting dolls — to open the smallest doll (base case), you must first unnest each larger outer doll one level at a time.",
    "stack": "A stack of cafeteria trays where you can only place a new tray on top (push) or take off the top tray (pop) — Last-In, First-Out.",
    "queue": "A movie theater ticket line where the first person to stand in line is served first — First-In, First-Out.",
    "hash table": "A post office box hall where your key (hash function) instantly points to your exact P.O. box number without searching box by box.",
    "normalization": "Organizing a messy workshop by putting tools into dedicated labeled drawers instead of dumping everything into one huge multi-purpose box, preventing duplicate clutter.",
    "process synchronization": "A single-lane bridge with a traffic signal (semaphore) preventing two cars from driving onto the narrow bridge at the same time and crashing.",
    "linked list": "A scavenger hunt where each clue card tells you where to find the item and gives you a map leading directly to the location of the next clue card.",
}


class BeginnerSocraticEngine:
    """Builds Socratic tutoring prompts tailored specifically for Beginner students.

    Focuses on non-intimidating explanations, intuitive real-world analogies,
    gradual step-by-step scaffolding, and encouraging follow-up check questions.
    """

    BEGINNER_SYSTEM_TEMPLATE = """You are EduMate, a patient, encouraging, and highly intuitive AI Personal Tutor.
Target Level: BEGINNER STUDENT

PEDAGOGICAL STRATEGY FOR BEGINNERS:
1. Speak in warm, accessible, and non-intimidating terms. Avoid dense formal mathematical notation unless requested.
2. ALWAYS lead with a relatable real-world analogy before diving into technical details.
3. Break concepts into 3 clear steps: (a) What is it?, (b) Why do we use it?, (c) Simple Analogy.
4. Keep definitions intuitive and highlight practical relevance.
5. End with an encouraging single Socratic question to verify understanding.

SUBJECT: {subject}
ACTIVE TOPIC: {topic}

{analogy_guidance}
{language_instruction}
{weak_area_scaffolding}
"""

    def __init__(self) -> None:
        self.analogies = CONCEPT_ANALOGIES

    def build_prompt(
        self,
        subject: str,
        topic: str,
        language: str = "English",
        weak_areas: Optional[List[str]] = None,
    ) -> str:
        """Construct a complete Beginner system prompt for Gemini LLM.

        Args:
            subject: Academic subject area.
            topic: Active topic context.
            language: Target output language (English, Hindi, Telugu).
            weak_areas: Student's identified weak areas.

        Returns:
            Formatted system prompt string.
        """
        analogy_guidance = self._get_analogy_guidance(topic)
        language_instruction = self._get_language_instruction(language)
        weak_area_scaffolding = self._get_weak_area_scaffolding(weak_areas)

        return self.BEGINNER_SYSTEM_TEMPLATE.format(
            subject=subject,
            topic=topic,
            analogy_guidance=analogy_guidance,
            language_instruction=language_instruction,
            weak_area_scaffolding=weak_area_scaffolding,
        ).strip()

    def _get_analogy_guidance(self, topic: str) -> str:
        """Find matching domain analogy or return general analogy guidance."""
        topic_lower = topic.lower()

        for concept_key, analogy_text in self.analogies.items():
            if concept_key in topic_lower:
                return (
                    f"RECOMMENDED ANALOGY FOR {topic.upper()}:\n"
                    f"\"{analogy_text}\"\n"
                    f"Use this analogy or a similar intuitive comparison in your explanation."
                )

        return (
            "ANALOGY GUIDANCE:\n"
            "Create a vivid, real-world comparison using everyday objects (e.g. books, lines, drawers, maps) "
            "to make this abstract concept immediately intuitive."
        )

    @staticmethod
    def _get_language_instruction(language: str) -> str:
        """Return language constraint rule."""
        if language == "Hindi":
            return "LANGUAGE: Respond in encouraging Hindi (Devanagari script), keeping core technical terms in English."
        elif language == "Telugu":
            return "LANGUAGE: Respond in patient Telugu (Telugu script), keeping core technical terms in English."
        return "LANGUAGE: Respond in clear, accessible, and friendly English."

    @staticmethod
    def _get_weak_area_scaffolding(weak_areas: Optional[List[str]]) -> str:
        """Return scaffolding text if topic overlaps with student weak areas."""
        if not weak_areas:
            return ""

        return (
            f"FOUNDATIONAL SCAFFOLDING:\n"
            f"The student needs extra support in: {', '.join(weak_areas)}. "
            f"Offer gentle reassurance and break down foundational prerequisites carefully."
        )


beginner_engine = BeginnerSocraticEngine()
