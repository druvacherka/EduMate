"""Student Mastery Analytics and Weak Area Engine for EduMate.

Aggregates quiz performance records, identifies weak topics requiring reinforcement,
and computes dynamic student mastery metrics.
"""

from typing import Any, Dict, List
from backend.database import get_db_connection, get_student_profile


class AnalyticsEngine:
    """Computes real-time student analytics, subject progress, and weak areas."""

    def get_full_profile(self) -> Dict[str, Any]:
        """Aggregate full student mastery profile including dynamic weak/strong areas.

        Returns:
            Dict matching AnalyticsProfileResponse schema.
        """
        profile = get_student_profile()

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Fetch active weak areas
            cursor.execute("""
                SELECT topic, mistake_count FROM weak_areas
                WHERE is_mastered = 0
                ORDER BY mistake_count DESC;
            """)
            weak_rows = cursor.fetchall()
            weak_areas = [r["topic"] for r in weak_rows]

            # Fetch strong areas
            cursor.execute("""
                SELECT topic FROM strong_areas
                ORDER BY success_count DESC;
            """)
            strong_rows = cursor.fetchall()
            strong_areas = [r["topic"] for r in strong_rows]

            # Fetch subject progress
            cursor.execute("""
                SELECT subject_name, progress, topics_completed, total_topics, status
                FROM subject_progress
                ORDER BY progress DESC;
            """)
            progress_rows = cursor.fetchall()
            subject_progress = [
                {
                    "name": r["subject_name"],
                    "progress": r["progress"],
                    "topicsCompleted": r["topics_completed"],
                    "totalTopics": r["total_topics"],
                    "status": r["status"],
                }
                for r in progress_rows
            ]

            # Count active goals
            cursor.execute("SELECT COUNT(*) AS cnt FROM student_goals WHERE is_active = 1;")
            goals_cnt = cursor.fetchone()["cnt"]

        return {
            "name": profile.get("name", "Student"),
            "email": profile.get("email", ""),
            "level": profile.get("level", "Beginner"),
            "language": profile.get("language", "English"),
            "currentSubject": profile.get("current_subject", ""),
            "currentTopic": profile.get("current_topic", ""),
            "masteryScore": round(profile.get("mastery_score", 0.0), 1),
            "studyStreakDays": profile.get("study_streak_days", 0),
            "weakAreas": weak_areas,
            "strongAreas": strong_areas,
            "subjectProgress": subject_progress,
            "educationLevel": profile.get("education_level", "B.Tech / Engineering"),
            "institution": profile.get("institution", ""),
            "streamBranch": profile.get("stream_branch", "Computer Science & Engineering"),
            "academicYearSemester": profile.get("academic_year_semester", "3rd Year / 5th Sem"),
            "dailyStudyHours": profile.get("daily_study_hours", 2.0),
            "onboardingCompleted": bool(profile.get("onboarding_completed", 1)),
            "activeGoalsCount": goals_cnt,
        }


analytics_engine = AnalyticsEngine()
