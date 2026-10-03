"""Deterministic Adaptive Recommendation Engine for EduMate.

Computes the student's Next Best Learning Action based on current mastery,
active goals, pending spaced revisions, and identified weak concepts from MongoDB.
"""

from typing import Any, Dict, List, Optional
from datetime import date

from database import (
    get_student_profile,
    list_revision_items,
    list_weak_areas,
)
from backend.services.goals_engine import goals_engine


class RecommendationEngine:
    """Calculates deterministic, auditable next learning actions."""

    def get_next_recommendation(self, student_id: int = 1) -> Dict[str, Any]:
        """Determine next priority study activity.

        Priority order:
        1. High-frequency weak areas with mistake_count >= 2 (Urgent Revision).
        2. Spaced repetition topics currently due.
        3. Active goal milestone practice / new concept learning.
        """
        profile = get_student_profile(student_id)
        goals = [g for g in goals_engine.get_goals(student_id=student_id) if g.is_active]

        # 1. Check for prominent weak areas
        weak_rows = list_weak_areas(is_mastered=False, limit=1)
        weak_row = weak_rows[0] if weak_rows else None

        if weak_row and weak_row.get("mistake_count", 0) >= 2:
            return {
                "recommended_action": "REVIEW_MISTAKES",
                "subject": weak_row.get("subject") or profile.get("current_subject") or "Core Subject",
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

        # 3. Next learning action from active goal or current topic
        primary_goal = goals[0] if goals else None
        current_subject = profile.get("current_subject") or (primary_goal.name if primary_goal else "General Learning")
        current_topic = profile.get("current_topic") or "Fundamental Concepts"

        mastery = float(profile.get("mastery_score", 0.0))

        if mastery < 50.0:
            return {
                "recommended_action": "LEARN",
                "subject": current_subject,
                "topic": current_topic,
                "reason": f"Baseline mastery is {round(mastery, 1)}%. Socratic foundational study recommended.",
                "estimated_minutes": 30,
                "priority": "NORMAL",
                "learning_level": "Beginner",
            }
        elif mastery < 75.0:
            return {
                "recommended_action": "PRACTICE",
                "subject": current_subject,
                "topic": current_topic,
                "reason": f"Mastery is progressing ({round(mastery, 1)}%). Adaptive problem-solving recommended.",
                "estimated_minutes": 35,
                "priority": "NORMAL",
                "learning_level": profile.get("level", "Intermediate"),
            }
        else:
            return {
                "recommended_action": "QUIZ",
                "subject": current_subject,
                "topic": current_topic,
                "reason": f"High topic mastery ({round(mastery, 1)}%). Challenge with timed evaluation.",
                "estimated_minutes": 20,
                "priority": "HIGH",
                "learning_level": "Advanced",
            }


recommendation_engine = RecommendationEngine()
