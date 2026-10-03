"""Dynamic Scoped Context Builder for EduMate Socratic Tutor & AI Engines.

Constructs lean, scoped student pedagogical context avoiding token bloat and
ensuring the AI tutor tailors examples, terminology, and analogies to the student's
education level and active goals using MongoDB data.
"""

from typing import Any, Dict, List, Optional
from database import get_student_profile, list_weak_areas
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
        profile = get_student_profile(student_id)
        goals = [g for g in goals_engine.get_goals(student_id=student_id) if g.is_active]
        active_goal = goals[0] if goals else None

        weak_rows = list_weak_areas(is_mastered=False, limit=2)
        weak_topics = [f"{r.get('topic', '')} ({r.get('mistake_count', 1)} errors)" for r in weak_rows if r.get('topic')]

        context_dict = {
            "student_name": profile.get("name", "Student"),
            "education_level": profile.get("education_level", "B.Tech / Engineering"),
            "stream_branch": profile.get("stream_branch", "Computer Science & Engineering"),
            "active_goal": active_goal.name if active_goal else "Curriculum Mastery",
            "target_exam": active_goal.target_exam if active_goal and active_goal.target_exam else "Academic Examination",
            "current_subject": query_subject or profile.get("current_subject") or "General Science & Technology",
            "current_topic": query_topic or profile.get("current_topic") or "Core Concepts",
            "mastery_score": f"{float(profile.get('mastery_score', 50.0)):.1f}%",
            "weak_areas": weak_topics if weak_topics else ["None recorded"],
            "preferred_language": profile.get("language", "English"),
            "learning_level": profile.get("level", "Beginner"),
        }

        return context_dict

    def format_tutor_context_prompt(self, ctx: Dict[str, Any]) -> str:
        """Format dictionary into concise system instruction string."""
        weak_str = ", ".join(ctx.get("weak_areas", []))
        return (
            f"STUDENT PROFILE CONTEXT:\n"
            f"- Student: {ctx.get('student_name')} | Education Level: {ctx.get('education_level')} ({ctx.get('stream_branch')})\n"
            f"- Active Goal: {ctx.get('active_goal')} (Target: {ctx.get('target_exam')})\n"
            f"- Current Mastery: {ctx.get('mastery_score')} | Learning Tier: {ctx.get('learning_level')}\n"
            f"- Known Weak Concepts to Reinforce: {weak_str}\n"
            f"- Preferred Language: {ctx.get('preferred_language')}"
        )


context_builder = ContextBuilder()
