"""Student Mastery Analytics and Weak Area Engine for EduMate.

Aggregates quiz performance records, identifies weak topics requiring reinforcement,
and computes dynamic student mastery metrics from MongoDB.
"""

from typing import Any, Dict, List
from database import (
    get_student_profile,
    list_weak_areas,
    list_strong_areas,
    list_subject_progress,
    list_student_goals,
)


class AnalyticsEngine:
    """Computes real-time student analytics, subject progress, and weak areas."""

    def get_full_profile(self) -> Dict[str, Any]:
        """Aggregate full student mastery profile including dynamic weak/strong areas.

        Returns:
            Dict matching AnalyticsProfileResponse schema.
        """
        profile = get_student_profile(1)

        # Fetch active weak areas
        weak_rows = list_weak_areas(is_mastered=False)
        weak_areas = [r["topic"] for r in weak_rows]

        # Fetch strong areas
        strong_rows = list_strong_areas()
        strong_areas = [r["topic"] for r in strong_rows]

        # Fetch subject progress
        progress_rows = list_subject_progress()
        subject_progress = [
            {
                "name": r.get("subject_name", ""),
                "progress": r.get("progress", 0),
                "topicsCompleted": r.get("topics_completed", 0),
                "totalTopics": r.get("total_topics", 10),
                "status": r.get("status", "In Progress"),
            }
            for r in progress_rows
        ]

        # Count active goals
        active_goals = [g for g in list_student_goals(1) if g.get("is_active")]
        goals_cnt = len(active_goals)

        return {
            "name": profile.get("name", "Student"),
            "email": profile.get("email", ""),
            "level": profile.get("level", "Beginner"),
            "language": profile.get("language", "English"),
            "currentSubject": profile.get("current_subject", ""),
            "currentTopic": profile.get("current_topic", ""),
            "masteryScore": round(float(profile.get("mastery_score", 0.0)), 1),
            "studyStreakDays": int(profile.get("study_streak_days", 0)),
            "weakAreas": weak_areas,
            "strongAreas": strong_areas,
            "subjectProgress": subject_progress,
            "educationLevel": profile.get("education_level", "B.Tech / Engineering"),
            "institution": profile.get("institution", ""),
            "streamBranch": profile.get("stream_branch", "Computer Science & Engineering"),
            "academicYearSemester": profile.get("academic_year_semester", "3rd Year / 5th Sem"),
            "dailyStudyHours": float(profile.get("daily_study_hours", 2.0)),
            "onboardingCompleted": bool(profile.get("onboarding_completed", 1)),
            "activeGoalsCount": goals_cnt,
        }


analytics_engine = AnalyticsEngine()
