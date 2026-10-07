"""Pydantic v2 schemas for Structured Quiz Generation and Multi-format Evaluation."""

from typing import Any, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

QuestionType = Literal["mcq", "tf", "short"]
DifficultyLevel = Literal["Easy", "Medium", "Hard"]


class QuizQuestionModel(BaseModel):
    """Schema for a single multi-format AI quiz question."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(..., description="Unique question ID")
    type: QuestionType = Field(..., description="Question format: mcq, tf, or short")
    question: str = Field(..., min_length=5, description="Question stem text")
    options: Optional[List[str]] = Field(None, description="Choices for MCQ questions")
    correct_answer: Any = Field(
        ...,
        alias="correctAnswer",
        description="Target answer index or key text",
    )
    explanation: str = Field(..., min_length=10, description="Step-by-step corrective reasoning")
    difficulty: DifficultyLevel = Field("Medium", description="Question difficulty rating")
    topic: str = Field(..., description="Academic topic tested")
    rubric_keywords: Optional[List[str]] = Field(
        default_factory=list,
        description="Key conceptual tokens required for short answer evaluation",
    )


class QuizGenerationConfig(BaseModel):
    """Parameters for adaptive quiz generation."""

    topic: str = Field(..., description="Target technical topic")
    num_questions: int = Field(7, ge=1, le=10, description="Number of questions")
    difficulty: DifficultyLevel = Field("Medium", description="Target difficulty")
    mastery_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Current student mastery percentage")
    allowed_types: List[QuestionType] = Field(
        default_factory=lambda: ["mcq", "tf", "short"],
        description="Allowed question types",
    )


class ShortAnswerEvaluationResult(BaseModel):
    """Evaluation result for open-ended short answer questions."""

    question_id: str
    is_correct: bool
    score_percentage: float = Field(..., ge=0.0, le=100.0)
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    corrective_explanation: str
