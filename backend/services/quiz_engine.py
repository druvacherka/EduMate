"""Quiz State Machine and Automated Corrective Evaluation Engine for EduMate.

Manages quiz lifecycle transitions (CREATED -> ACTIVE -> SUBMITTED -> EVALUATED),
evaluates answers, logs student mistakes into weak areas, and updates mastery metrics via MongoDB.
"""

import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from ai_rag.llm_client import llm_client
from database import (
    get_student_profile,
    create_quiz_session,
    get_quiz_session,
    update_quiz_session_evaluation,
)

from ai_rag.prompts.adaptive_scaler import adaptive_difficulty_scaler
from ai_rag.validators.json_repair import json_repair_middleware


class QuizState(str, Enum):
    """Finite State Machine states for an interactive quiz session."""
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    SUBMITTED = "SUBMITTED"
    EVALUATED = "EVALUATED"


class QuizStateMachine:
    """Manages the lifecycle, state transitions, and evaluation of quiz sessions."""

    async def create_session(
        self,
        topic: str,
        difficulty: str = "Medium",
        num_questions: int = 3,
        adaptive: bool = True,
    ) -> Dict[str, Any]:
        """Generate questions and initialize a new quiz session in CREATED state.

        Args:
            topic: Technical subject topic (e.g. 'Binary Search Trees').
            difficulty: 'Easy', 'Medium', or 'Hard'.
            num_questions: Total questions to generate.
            adaptive: Whether to calibrate difficulty using student's historical mastery.

        Returns:
            Dict containing session metadata and generated questions.
        """
        session_id = f"quiz-{uuid.uuid4().hex[:8]}"

        # Check student mastery to calibrate difficulty if adaptive
        calibrated_diff = difficulty
        if adaptive:
            profile = get_student_profile(1)
            mastery = profile.get("mastery_score")
            if mastery is not None:
                calibrated_diff = adaptive_difficulty_scaler.determine_adaptive_difficulty(
                    mastery_score=float(mastery),
                    requested_difficulty=difficulty,
                )

        # Generate questions using LLM client
        questions = await llm_client.generate_structured_quiz(
            topic=topic,
            num_questions=num_questions,
            difficulty=calibrated_diff,
        )

        create_quiz_session(
            session_id=session_id,
            topic=topic,
            difficulty=calibrated_diff,
            total_questions=len(questions),
            questions=questions,
        )

        return {
            "session_id": session_id,
            "topic": topic,
            "difficulty": calibrated_diff,
            "status": QuizState.ACTIVE.value,
            "questions": questions,
        }

    def evaluate_submission(
        self,
        session_id: str,
        user_answers: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process student answers through the state machine and evaluate performance.

        Transitions: ACTIVE -> SUBMITTED -> EVALUATED.

        Args:
            session_id: Unique quiz session identifier.
            user_answers: Dict mapping question_id to student's chosen answer.

        Returns:
            Evaluation summary with total score, percentage, question breakdowns,
            and updated weak areas.
        """
        session = get_quiz_session(session_id)

        if not session:
            # Fallback for ad-hoc submissions
            return self._evaluate_adhoc_answers(user_answers)

        raw_questions = session.get("questions", [])
        if isinstance(raw_questions, str):
            questions = json.loads(raw_questions)
        else:
            questions = raw_questions

        topic = session.get("topic", "Computer Science")

        # Calculate score and build detailed feedback
        score = 0
        question_results: List[Dict[str, Any]] = []
        mistaken_topics: List[str] = []

        for q in questions:
            q_id = str(q.get("id"))
            correct_ans = q.get("correctAnswer")
            user_ans = user_answers.get(q_id)

            # Evaluate answer based on question type
            is_correct = False
            explanation = q.get("explanation", "")

            if q.get("type") == "short":
                eval_res = adaptive_difficulty_scaler.evaluate_short_answer_heuristic(
                    student_answer=str(user_ans or ""),
                    reference_answer=str(correct_ans or ""),
                    rubric_keywords=q.get("rubric_keywords") or [str(correct_ans)],
                )
                is_correct = eval_res["is_correct"]
                explanation = f"{eval_res['feedback']} {explanation}"
            else:
                is_correct = self._check_answer_match(
                    user_ans=user_ans,
                    correct_ans=correct_ans,
                    options=q.get("options"),
                )

            if is_correct:
                score += 1
            else:
                mistaken_topics.append(q.get("topic", topic))

            question_results.append({
                "id": q_id,
                "question": q.get("question"),
                "type": q.get("type"),
                "options": q.get("options"),
                "user_answer": user_ans,
                "correct_answer": correct_ans,
                "is_correct": is_correct,
                "explanation": explanation,
            })

        total = len(questions)
        percentage = round((score / max(total, 1)) * 100.0, 1)

        # Update session, weak areas, and dynamic student mastery in MongoDB
        update_quiz_session_evaluation(
            session_id=session_id,
            score=score,
            percentage=percentage,
            user_answers=user_answers,
            mistaken_topics=mistaken_topics,
            topic=topic,
        )

        return {
            "session_id": session_id,
            "status": QuizState.EVALUATED.value,
            "score": score,
            "total_questions": total,
            "percentage": percentage,
            "mistakes_count": len(mistaken_topics),
            "mistaken_topics": list(set(mistaken_topics)),
            "results": question_results,
        }

    def _check_answer_match(
        self,
        user_ans: Any,
        correct_ans: Any,
        options: Optional[List[str]] = None,
    ) -> bool:
        """Robustly compare student answer against reference answer.

        Handles:
        - Exact normalized string match (ignoring whitespace and case)
        - Boolean mappings ("true", "false", True, False, 1, 0)
        - Index lookups (e.g. user_ans=1, options=["True", "False"], correct_ans="False")
        - Option letter lookups ("A", "B", "C", "D")
        - Option text equality
        """
        if user_ans is None or correct_ans is None:
            return False

        u_str = str(user_ans).strip().lower()
        c_str = str(correct_ans).strip().lower()

        # 1. Exact string match
        if u_str == c_str:
            return True

        # 2. Boolean normalization
        bool_map = {
            "true": True,
            "false": False,
            "1": True,
            "0": False,
        }
        if u_str in bool_map and c_str in bool_map:
            if bool_map[u_str] == bool_map[c_str]:
                return True

        # 3. Option-based resolution for MCQs and True/False
        if options and isinstance(options, list) and len(options) > 0:
            opt_count = len(options)

            def resolve_opt(val: Any):
                val_str = str(val).strip()
                # Check integer index: 0, 1, 2, ...
                if val_str.isdigit():
                    idx = int(val_str)
                    if 0 <= idx < opt_count:
                        return idx, options[idx].strip().lower()
                # Check letter A, B, C, D
                if len(val_str) == 1 and val_str.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    idx = ord(val_str.upper()) - ord("A")
                    if 0 <= idx < opt_count:
                        return idx, options[idx].strip().lower()
                # Check full text match against one of the options
                for i, opt in enumerate(options):
                    if str(opt).strip().lower() == val_str.lower():
                        return i, str(opt).strip().lower()
                return None, val_str.lower()

            u_idx, u_opt_text = resolve_opt(user_ans)
            c_idx, c_opt_text = resolve_opt(correct_ans)

            # Matches if both resolved to the same option index
            if u_idx is not None and c_idx is not None and u_idx == c_idx:
                return True

            # Matches if the resolved option texts match
            if u_opt_text and c_opt_text and u_opt_text == c_opt_text:
                return True

        return False

    def _evaluate_adhoc_answers(self, user_answers: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback evaluation for offline/client generated questions."""
        total = len(user_answers)
        score = sum(1 for v in user_answers.values() if v in [0, 1, "True"])
        pct = round((score / max(total, 1)) * 100.0, 1)
        return {
            "session_id": f"quiz-adhoc",
            "status": QuizState.EVALUATED.value,
            "score": score,
            "total_questions": total,
            "percentage": pct,
            "mistakes_count": total - score,
            "mistaken_topics": [],
            "results": [],
        }


quiz_state_machine = QuizStateMachine()
