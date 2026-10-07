"""Deterministic Adaptive Recommendation Engine for EduMate.

Computes the student's Next Best Learning Action based on current mastery,
active goals, pending spaced revisions, and identified weak concepts.
"""

from typing import Any, Dict, List, Optional

from backend.database import (
    get_student_profile,
    list_revision_items,
    get_db_connection,
)


class RecommendationEngine:
    """Calculates deterministic, auditable next learning actions."""

    def get_next_recommendation(self, student_id: int = 1) -> Optional[Dict[str, Any]]:
        """Determine next priority study activity.

        Priority order:
        1. High-frequency weak areas with mistake_count >= 2 (Urgent Revision).
        2. Spaced repetition topics currently due.
        """
        profile = get_student_profile(student_id)

        # 1. Check for prominent weak areas
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT topic, subject, mistake_count FROM weak_areas
                WHERE student_id = ? AND is_mastered = 0
                ORDER BY mistake_count DESC, last_mistake_date DESC
                LIMIT 1;
            """, (student_id,))
            weak_row = cursor.fetchone()

        if weak_row and weak_row["mistake_count"] >= 2:
            return {
                "recommended_action": "REVIEW_MISTAKES",
                "subject": weak_row["subject"] or profile.get("current_subject") or "",
                "topic": weak_row["topic"],
                "reason": f"High mistake frequency ({weak_row['mistake_count']} errors recorded). Requires targeted reinforcement.",
                "estimated_minutes": 25,
                "priority": "HIGH",
                "learning_level": profile.get("level", "Beginner"),
            }

        # 2. Check for overdue spaced revision
        due_revisions = list_revision_items(student_id=student_id, due_only=True)
        if due_revisions:
            top_rev = due_revisions[0]
            return {
                "recommended_action": "REVISE",
                "subject": top_rev["subject"],
                "topic": top_rev["topic"],
                "reason": f"Scheduled spaced repetition due for long-term retention (Interval: {top_rev['interval_days']} days).",
                "estimated_minutes": 20,
                "priority": "HIGH",
                "learning_level": profile.get("level", "Beginner"),
            }

        return None


recommendation_engine = RecommendationEngine()
