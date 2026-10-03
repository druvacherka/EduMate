"""Adaptive Difficulty Scaler and Multi-Format Quiz Prompt Generator for EduMate.

Calibrates question difficulty and Bloom's cognitive taxonomy depth based on student mastery score,
and builds prompts for MCQ, True/False, and Short Answer question generation.
"""

from typing import Any, Dict, List, Optional
from ai_rag.schemas.quiz_schemas import (
    DifficultyLevel,
    QuestionType,
    QuizGenerationConfig,
)


class AdaptiveDifficultyScaler:
    """Scales quiz question difficulty and cognitive depth according to student mastery history."""

    def determine_adaptive_difficulty(self, mastery_score: Optional[float], requested_difficulty: DifficultyLevel = "Medium") -> DifficultyLevel:
        """Derive target difficulty based on student mastery score.

        Args:
            mastery_score: Student overall mastery score (0 - 100).
            requested_difficulty: Default if mastery_score is None.

        Returns:
            Calibrated DifficultyLevel ('Easy', 'Medium', or 'Hard').
        """
        if mastery_score is None:
            return requested_difficulty

        if mastery_score < 60.0:
            return "Easy"
        elif mastery_score > 82.0:
            return "Hard"
        else:
            return "Medium"

    def get_cognitive_focus(self, difficulty: DifficultyLevel) -> str:
        """Return Bloom's taxonomy focus instruction for prompt generation."""
        if difficulty == "Easy":
            return "Focus on Foundational Recall, Definition Invariants, and Intuitive Concept Checks."
        elif difficulty == "Hard":
            return "Focus on Edge Cases, Worst-Case Complexity Trade-offs, and Structural Violations."
        else:
            return "Focus on Step-by-Step Execution Traces, Operation Invariants, and Practical Applications."

    def build_quiz_generation_prompt(self, config: QuizGenerationConfig) -> str:
        """Construct structured JSON prompt for generating multi-format questions.

        Args:
            config: QuizGenerationConfig object.

        Returns:
            Prompt instructing Gemini to output valid structured JSON array.
        """
        calibrated_diff = self.determine_adaptive_difficulty(config.mastery_score, config.difficulty)
        cognitive_focus = self.get_cognitive_focus(calibrated_diff)

        types_desc = ", ".join(config.allowed_types)

        prompt = f"""Generate an academic assessment quiz for B.Tech engineering students on the topic: '{config.topic}'.

CONFIGURATION:
- Number of Questions: {config.num_questions}
- Target Difficulty: {calibrated_diff}
- Pedagogical Focus: {cognitive_focus}
- Allowed Formats: {types_desc}

OUTPUT FORMAT RULES:
Return ONLY a valid JSON array of question objects (no markdown fences, no conversational filler).
Each object MUST have the following schema:
{{
  "id": "q1",
  "type": "mcq" | "tf" | "short",
  "question": "Question text...",
  "options": ["Option A", "Option B", "Option C", "Option D"], // Required for mcq; for tf use ["True", "False"]; omit for short
  "correctAnswer": 0, // Integer 0-3 for mcq, 0 or 1 for tf, or concise reference answer string for short
  "explanation": "Detailed step-by-step corrective pedagogical explanation...",
  "difficulty": "{calibrated_diff}",
  "topic": "{config.topic}",
  "rubric_keywords": ["keyword1", "keyword2"] // For short answer key concept evaluation
}}
"""
        return prompt

    def evaluate_short_answer_heuristic(
        self,
        student_answer: str,
        reference_answer: str,
        rubric_keywords: List[str],
    ) -> Dict[str, Any]:
        """Evaluate a student's open-ended short answer against rubric keywords.

        Args:
            student_answer: Text entered by the student.
            reference_answer: Model reference answer.
            rubric_keywords: Key technical tokens required for credit.

        Returns:
            Dict containing is_correct, score_percentage, matched and missing keywords.
        """
        if not student_answer or not student_answer.strip():
            return {
                "is_correct": False,
                "score_percentage": 0.0,
                "matched_keywords": [],
                "missing_keywords": rubric_keywords,
                "feedback": "No answer provided.",
            }

        student_lower = student_answer.lower()
        matched = [k for k in rubric_keywords if k.lower() in student_lower]
        missing = [k for k in rubric_keywords if k.lower() not in student_lower]

        match_ratio = len(matched) / max(len(rubric_keywords), 1)
        score_pct = round(match_ratio * 100.0, 1)
        is_correct = score_pct >= 60.0

        return {
            "is_correct": is_correct,
            "score_percentage": score_pct,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "feedback": (
                "Great conceptual coverage!"
                if is_correct
                else f"Consider incorporating missing core concepts: {', '.join(missing)}."
            ),
        }


adaptive_difficulty_scaler = AdaptiveDifficultyScaler()
