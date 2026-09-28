"""Unit tests for Month 5 AI Quiz Generation, JSON Repair Middleware, and Adaptive Scaling."""

import pytest
from services.ai_rag.prompts.adaptive_scaler import adaptive_difficulty_scaler
from services.ai_rag.schemas.quiz_schemas import (
    QuizGenerationConfig,
    QuizQuestionModel,
)
from services.ai_rag.validators.json_repair import json_repair_middleware


def test_json_repair_clean_markdown_fences():
    raw_markdown = """```json
    [
      {"id": "q1", "type": "tf", "question": "BST search is O(log n)", "correctAnswer": 0, "explanation": "Balanced tree invariant", "difficulty": "Easy", "topic": "Trees"}
    ]
    ```"""
    parsed = json_repair_middleware.repair_and_parse(raw_markdown)
    assert len(parsed) == 1
    assert parsed[0]["id"] == "q1"


def test_json_repair_trailing_commas_and_wrapper_text():
    messy_llm_output = """Sure! Here are the requested questions:
    [
      {
        "id": "q1",
        "type": "mcq",
        "question": "What is the time complexity of quicksort average case?",
        "options": ["O(N)", "O(N log N)", "O(N^2)"],
        "correctAnswer": 1,
        "explanation": "Partitioning divides the array in logarithmic depth on average.",
        "difficulty": "Medium",
        "topic": "Sorting",
      },
    ]
    Hope this helps your study session!"""

    parsed = json_repair_middleware.repair_and_parse(messy_llm_output)
    assert len(parsed) == 1
    assert parsed[0]["topic"] == "Sorting"
    assert parsed[0]["correctAnswer"] == 1


def test_adaptive_difficulty_scaler():
    # Low mastery score -> Easy
    diff_low = adaptive_difficulty_scaler.determine_adaptive_difficulty(mastery_score=52.0)
    assert diff_low == "Easy"

    # Moderate mastery score -> Medium
    diff_mid = adaptive_difficulty_scaler.determine_adaptive_difficulty(mastery_score=75.0)
    assert diff_mid == "Medium"

    # High mastery score -> Hard
    diff_high = adaptive_difficulty_scaler.determine_adaptive_difficulty(mastery_score=88.0)
    assert diff_high == "Hard"


def test_short_answer_heuristic_evaluation():
    rubric = ["in-order successor", "minimum", "right subtree"]
    student_ans = "Replace the node with its in-order successor, which is the minimum value in the right subtree."

    res = adaptive_difficulty_scaler.evaluate_short_answer_heuristic(
        student_answer=student_ans,
        reference_answer="In-order successor",
        rubric_keywords=rubric,
    )

    assert res["is_correct"] is True
    assert res["score_percentage"] == 100.0
    assert len(res["missing_keywords"]) == 0
