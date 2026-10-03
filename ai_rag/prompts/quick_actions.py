"""Socratic Quick Action Chip Prompt Handlers for EduMate AI Tutor.

Provides specialized prompt generators for interactive follow-up chips:
- "Simplify": Re-explain with simpler language and analogies
- "Give Example": Provide concrete code/problem example
- "Explain Deeper": Deep-dive into technical mechanics
- "Practice Question": Generate a targeted check question
- "Real-World Application": Connect concept to industry software use-cases
"""

import logging
from typing import Dict, Literal, Optional

logger = logging.getLogger(__name__)

QuickActionType = Literal[
    "simplify",
    "give_example",
    "explain_deeper",
    "practice_question",
    "real_world",
]

ACTION_TEMPLATES: Dict[QuickActionType, str] = {
    "simplify": """REFINEMENT INSTRUCTION: SIMPLIFY EXPLANATION
The student clicked the 'Simplify' action chip.
Re-explain the previous concept using even simpler, highly intuitive language.
- Reduce technical jargon.
- Use a vivid, memorable real-world analogy.
- Focus purely on the 'why' and 'how' in 3 short bullet points.
""",
    "give_example": """REFINEMENT INSTRUCTION: PROVIDE CONCRETE EXAMPLE
The student clicked the 'Give Example' action chip.
Provide a clear, concrete, step-by-step example demonstrating the concept.
- If programming: provide a short, executable code snippet with line-by-line commentary.
- If mathematical/algorithmic: walk through a sample input array/tree step by step.
- Highlight common input values and expected outputs.
""",
    "explain_deeper": """REFINEMENT INSTRUCTION: EXPLAIN DEEPER
The student clicked the 'Explain Deeper' action chip.
Provide a deep technical breakdown of the underlying mechanics.
- Detail memory layout, pointer operations, or computational steps.
- Provide Big-O time and space complexity analysis ($$\\mathcal{{O}}(...)$$ format).
- Discuss edge cases, boundary conditions, and performance trade-offs.
""",
    "practice_question": """REFINEMENT INSTRUCTION: GENERATE PRACTICE QUESTION
The student clicked the 'Practice Question' action chip.
Generate ONE engaging, interactive practice question based on the topic.
- Offer 3-4 plausible choices (A, B, C, D) or a short code prediction task.
- Do NOT reveal the correct answer immediately; ask the student to select or type their answer.
""",
    "real_world": """REFINEMENT INSTRUCTION: SHOW REAL-WORLD APPLICATION
The student clicked the 'Real-World Application' action chip.
Explain how this concept is used in modern industrial software systems.
- Mention real software (e.g. database indexing engines, OS schedulers, network routers, browser history engines).
- Explain why tech companies choose this specific approach over simpler alternatives.
""",
}


class QuickActionEngine:
    """Generates prompt instructions for user-triggered Socratic action chips."""

    def build_action_prompt(
        self,
        action_type: QuickActionType,
        previous_response: str,
        topic: str,
        level: str = "Beginner",
    ) -> str:
        """Construct prompt combining action refinement instruction with previous context.

        Args:
            action_type: One of 'simplify', 'give_example', 'explain_deeper', etc.
            previous_response: Text of the previous tutor explanation.
            topic: Active topic context.
            level: Active learning level.

        Returns:
            Formatted prompt string ready for LLM generation.
        """
        template = ACTION_TEMPLATES.get(
            action_type, ACTION_TEMPLATES["simplify"]
        )

        prompt = f"""{template}

ACTIVE TOPIC: {topic}
TARGET LEARNING LEVEL: {level}

PREVIOUS TUTOR RESPONSE REFERENCE:
\"\"\"
{previous_response.strip()}
\"\"\"

Please fulfill the refinement instruction above, referencing the previous explanation directly.
"""
        return prompt.strip()


quick_action_engine = QuickActionEngine()
