"""Quiz State Machine and Automated Corrective Evaluation Engine for EduMate.

Manages quiz lifecycle transitions (CREATED -> ACTIVE -> SUBMITTED -> EVALUATED),
evaluates answers, logs student mistakes into weak areas, and updates mastery metrics.
"""

import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from ai_rag.llm_client import llm_client
from backend.database import get_db_connection, get_student_profile


from ai_rag.prompts.adaptive_scaler import adaptive_difficulty_scaler


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
        student_id: int,
        difficulty: str = "Medium",
        num_questions: int = 7,
        source_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate questions and initialize a new quiz session in CREATED state.

        Args:
            topic: Technical subject topic (e.g. 'Binary Search Trees').
            difficulty: 'Easy', 'Medium', or 'Hard'.
            num_questions: Total questions to generate.

        Returns:
            Dict containing session metadata and generated questions.
        """
        session_id = f"quiz-{uuid.uuid4().hex[:8]}"

        # Generate questions using LLM client
        generation_inputs = {
            "topic": topic,
            "num_questions": num_questions,
            "difficulty": difficulty,
        }
        if source_context:
            generation_inputs["source_context"] = source_context
        questions = await llm_client.generate_structured_quiz(**generation_inputs)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quiz_sessions (
                    id, student_id, topic, difficulty, total_questions, score, percentage,
                    status, questions_json, created_at
                ) VALUES (?, ?, ?, ?, ?, 0, 0.0, ?, ?, ?);
            """, (
                session_id,
                student_id,
                topic,
                difficulty,
                len(questions),
                QuizState.ACTIVE.value,
                json.dumps(questions),
                datetime.now(timezone.utc).isoformat(),
            ))
            conn.commit()

        return {
            "session_id": session_id,
            "topic": topic,
            "difficulty": difficulty,
            "status": QuizState.ACTIVE.value,
            "questions": [
                {
                    key: value
                    for key, value in question.items()
                    if key not in {"correctAnswer", "correct_answer", "rubric_keywords"}
                }
                for question in questions
            ],
        }

    def evaluate_submission(
        self,
        session_id: str,
        user_answers: Dict[str, Any],
        student_id: int,
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
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quiz_sessions WHERE id = ? AND student_id = ?;", (session_id, student_id))
            session = cursor.fetchone()

            if not session:
                raise LookupError("Quiz session was not found.")

            questions = json.loads(session["questions_json"])
            topic = session["topic"]

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
                normalized_user_answer = str(user_ans).strip().casefold() if user_ans is not None else ""
                normalized_correct_answer = str(correct_ans).strip().casefold() if correct_ans is not None else ""
                answers_match = bool(normalized_correct_answer) and normalized_user_answer == normalized_correct_answer

                if answers_match:
                    is_correct = True
                elif q.get("type") == "short":
                    eval_res = adaptive_difficulty_scaler.evaluate_short_answer_heuristic(
                        student_answer=str(user_ans) if user_ans is not None else "",
                        reference_answer=str(correct_ans) if correct_ans is not None else "",
                        rubric_keywords=q.get("rubric_keywords") or [str(correct_ans)],
                    )
                    is_correct = eval_res["is_correct"]
                    explanation = f"{eval_res['feedback']} {explanation}"

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

            # Update session in DB
            completed_at = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                UPDATE quiz_sessions
                SET score = ?, percentage = ?, status = ?, user_answers_json = ?, completed_at = ?
                WHERE id = ? AND student_id = ?;
            """, (score, percentage, QuizState.EVALUATED.value, json.dumps(user_answers), completed_at, session_id, student_id))

            profile = get_student_profile(student_id)
            subject = profile.get("current_subject") or session["topic"]

            # Update Weak Areas and Strong Areas
            for m_topic in set(mistaken_topics):
                cursor.execute("""
                    INSERT INTO weak_areas (student_id, topic, subject, mistake_count, last_mistake_date)
                    VALUES (?, ?, ?, 1, ?)
                    ON CONFLICT(student_id, topic) DO UPDATE SET
                        mistake_count = weak_areas.mistake_count + 1,
                        last_mistake_date = ?;
                """, (student_id, m_topic, subject, completed_at, completed_at))

            if percentage >= 70:
                cursor.execute("""
                    INSERT INTO strong_areas (student_id, topic, subject, success_count)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(student_id, topic) DO UPDATE SET
                        success_count = strong_areas.success_count + 1;
                """, (student_id, topic, subject))

            # Adjust student mastery score dynamically
            delta = 2.5 if percentage >= 70 else -1.5
            cursor.execute("""
                UPDATE student_profile
                SET mastery_score = CASE
                    WHEN mastery_score + ? < 10.0 THEN 10.0
                    WHEN mastery_score + ? > 100.0 THEN 100.0
                    ELSE mastery_score + ?
                END
                WHERE id = ?;
            """, (delta, delta, delta, student_id))

            conn.commit()

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

quiz_state_machine = QuizStateMachine()
