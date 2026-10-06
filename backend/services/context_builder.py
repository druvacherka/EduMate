"""Dynamic Scoped Context Builder for EduMate Socratic Tutor & AI Engines.

Constructs lean, scoped student pedagogical context avoiding token bloat and
ensuring the AI tutor tailors examples, terminology, and analogies to the student's
education level and active goals.
"""

from typing import Any, Dict, List, Optional
from backend.database import get_student_profile, get_db_connection
from backend.services.goals_engine import goals_engine


class ContextBuilder:
    """Builds targeted, student-specific prompt context slices."""

    def build_tutor_context(
        self,
        student_id: int = 1,
        query_subject: Optional[str] = None,
        query_topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate structured context block for LLM prompt grounding."""
        profile = get_student_profile()
        goals = [g for g in goals_engine.get_goals(student_id=student_id) if g.is_active]
        active_goal = goals[0] if goals else None

        # Fetch relevant weak areas matching subject if possible
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if query_subject:
                cursor.execute("""
                    SELECT topic, mistake_count FROM weak_areas
                    WHERE is_mastered = 0 AND subject LIKE ?
                    ORDER BY mistake_count DESC LIMIT 2;
                """, (f"%{query_subject}%",))
            else:
                cursor.execute("""
                    SELECT topic, mistake_count FROM weak_areas
                    WHERE is_mastered = 0
                    ORDER BY mistake_count DESC LIMIT 2;
                """)
            weak_rows = cursor.fetchall()
            weak_topics = [f"{r['topic']} ({r['mistake_count']} errors)" for r in weak_rows]

        context_dict = {
            "student_name": profile.get("name", "Student"),
            "education_level": profile.get("education_level") or "Not set",
            "stream_branch": profile.get("stream_branch") or "Not set",
            "active_goal": active_goal.name if active_goal else "Not set",
            "target_exam": active_goal.target_exam if active_goal and active_goal.target_exam else "Not set",
            "current_subject": query_subject or profile.get("current_subject") or "Not set",
            "current_topic": query_topic or profile.get("current_topic") or "Not set",
            "mastery_score": f"{profile.get('mastery_score', 0.0):.1f}%",
            "weak_areas": weak_topics if weak_topics else ["None recorded"],
            "preferred_language": profile.get("language", "English"),
            "learning_level": profile.get("level", "Beginner"),
        }

        return context_dict

    def format_tutor_context_prompt(self, context: Dict[str, Any]) -> str:
        """Format the context block as a compact, structured prompt segment."""
        return (
            f"[Student Profile Context]\n"
            f"• Education Level: {context['education_level']} ({context['stream_branch']})\n"
            f"• Active Target: {context['active_goal']} (Exam: {context['target_exam']})\n"
            f"• Subject / Topic: {context['current_subject']} → {context['current_topic']}\n"
            f"• Mastery Level: {context['mastery_score']} | Tutoring Depth: {context['learning_level']}\n"
            f"• Prior Weak Concepts: {', '.join(context['weak_areas'])}\n"
            f"• Pedagogical Guideline: Calibrate examples and analogies to match {context['education_level']} students."
        )


context_builder = ContextBuilder()
