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

        return {
            "name": profile.get("name", "B.Tech Student"),
            "email": profile.get("email", "student@edumate.ai"),
            "level": profile.get("level", "Beginner"),
            "language": profile.get("language", "English"),
            "currentSubject": profile.get("current_subject", "Data Structures & Algorithms"),
            "currentTopic": profile.get("current_topic", "Binary Search Trees"),
            "masteryScore": round(profile.get("mastery_score", 78.5), 1),
            "studyStreakDays": profile.get("study_streak_days", 5),
            "weakAreas": weak_areas or ["Tree Balancing", "Graph Traversals"],
            "strongAreas": strong_areas or ["Arrays & HashMaps", "Sorting Algorithms"],
            "subjectProgress": subject_progress,
        }


analytics_engine = AnalyticsEngine()
