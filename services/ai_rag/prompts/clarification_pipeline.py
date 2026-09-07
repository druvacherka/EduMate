"""Socratic Follow-up Clarification Prompt Pipeline for EduMate AI Tutor.

Evaluates student responses to tutor follow-up questions, assesses mastery/confusion,
and generates adaptive Socratic responses to guide the student to full understanding.
"""

import logging
from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

MasteryLevel = Literal["correct", "partial", "confused", "question"]


class ClarificationEvaluation(BaseModel):
    """Evaluation output schema for student response analysis."""

    mastery_level: MasteryLevel = Field(
        ..., description="Assessed understanding level of student response"
    )
    feedback_summary: str = Field(
        ..., description="Brief summary of why this mastery level was assigned"
    )
    suggested_action: str = Field(
        ..., description="Recommended pedagogical next step"
    )


class ClarificationPipeline:
    """Orchestrates multi-turn Socratic check dialogues.

    Analyzes student answers, reinforces correct reasoning, gently corrects
    misconceptions without giving away direct answers, and maintains momentum.
    """

    EVALUATION_PROMPT_TEMPLATE = """SYSTEM INSTRUCTION: SOCRATIC CLARIFICATION EVALUATOR
You are analyzing a student's answer to a Socratic check question.

ACTIVE TOPIC: {topic}
TARGET LEARNING LEVEL: {level}

PREVIOUS TUTOR QUESTION:
\"{previous_question}\"

STUDENT RESPONSE:
\"{student_response}\"

EVALUATION GOAL:
Determine the student's mastery level:
- 'correct': Student demonstrated accurate understanding.
- 'partial': Student got part of it right but missed key details or edge cases.
- 'confused': Student gave an incorrect answer or expressed confusion ('I don't know').
- 'question': Student answered with a clarifying question of their own.
"""

    RESPONSE_PROMPTS: Dict[MasteryLevel, str] = {
        "correct": """PEDAGOGICAL INSTRUCTION: REINFORCE & ADVANCE
The student answered CORRECTLY!
1. Praise their correct reasoning specifically.
2. Briefly summarize why their logic is sound.
3. Introduce the next logical sub-topic or offer a slightly more challenging follow-up question.
""",
        "partial": """PEDAGOGICAL INSTRUCTION: GENTLE GUIDANCE
The student showed PARTIAL understanding.
1. Acknowledge and validate the correct parts of their response.
2. Highlight the missing detail or minor mistake using a subtle hint.
3. Ask a targeted guiding question to help them self-correct. Do NOT give the full answer immediately.
""",
        "confused": """PEDAGOGICAL INSTRUCTION: SUPPORTIVE RE-SCAFFOLDING
The student is CONFUSED or answered incorrectly.
1. Reassure them warmly — mistakes are essential steps in learning!
2. Break the concept down into a smaller, simpler component.
3. Provide a simpler mini-question or hint to build back up.
""",
        "question": """PEDAGOGICAL INSTRUCTION: DIRECT CLARIFICATION & SOCRATIC CHECK
The student asked a clarifying question.
1. Answer their question directly with high clarity.
2. Provide a brief visual or code example if relevant.
3. Follow up with a simple check to ensure the clarification landed.
""",
    }

    def build_clarification_response_prompt(
        self,
        mastery_level: MasteryLevel,
        student_response: str,
        topic: str,
        level: str = "Beginner",
    ) -> str:
        """Construct prompt guiding the LLM's response to the student's answer.

        Args:
            mastery_level: 'correct', 'partial', 'confused', or 'question'.
            student_response: Text of student's answer.
            topic: Active topic context.
            level: Active learning level.

        Returns:
            Formatted Socratic response prompt string.
        """
        instruction = self.RESPONSE_PROMPTS.get(
            mastery_level, self.RESPONSE_PROMPTS["partial"]
        )

        return f"""{instruction}

ACTIVE TOPIC: {topic}
TARGET LEARNING LEVEL: {level}

STUDENT'S ANSWER TO EVALUATE:
\"{student_response.strip()}\"

Respond to the student following the pedagogical instruction above.
""".strip()


clarification_pipeline = ClarificationPipeline()
