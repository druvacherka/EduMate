"""Spaced Revision Engine for EduMate.

Implements spaced repetition algorithms (Leitner interval scheduling: 1 -> 3 -> 7 -> 14 -> 30 days)
to reinforce retention of previously learned topics and remediated weak areas.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from backend.database import (
    list_revision_items,
    record_revision_completion,
    get_db_connection,
)
from backend.schemas import RevisionItemSchema, CompleteRevisionRequest


class RevisionEngine:
    """Manages spaced repetition review schedules and topic mastery refresh."""

    def get_revision_items(self, student_id: int = 1, due_only: bool = False) -> List[RevisionItemSchema]:
        """Fetch all or due-only spaced revision items."""
        rows = list_revision_items(student_id=student_id, due_only=due_only)
        return [
            RevisionItemSchema(
                id=r["id"],
                subject=r["subject"],
                topic=r["topic"],
                learned_date=r["learned_date"],
                interval_days=r["interval_days"],
                next_revision_date=r["next_revision_date"],
                last_reviewed_date=r.get("last_reviewed_date"),
                mastery_score=float(r["mastery_score"]),
                mistake_count=r["mistake_count"],
                status=r["status"],
            )
            for r in rows
        ]

    def complete_revision(self, req: CompleteRevisionRequest, student_id: int = 1) -> Optional[RevisionItemSchema]:
        """Record review outcome and advance or reset the spaced interval."""
        row = record_revision_completion(item_id=req.item_id, score=req.score, student_id=student_id)
        if not row:
            return None
        return RevisionItemSchema(
            id=row["id"],
            subject=row["subject"],
            topic=row["topic"],
            learned_date=row["learned_date"],
            interval_days=row["interval_days"],
            next_revision_date=row["next_revision_date"],
            last_reviewed_date=row.get("last_reviewed_date"),
            mastery_score=float(row["mastery_score"]),
            mistake_count=row["mistake_count"],
            status=row["status"],
        )

    def add_topic_to_revision(self, subject: str, topic: str, student_id: int = 1) -> RevisionItemSchema:
        """Add a newly studied topic or identified weak concept to the spaced repetition schedule."""
        today_str = date.today().isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO revision_schedule (
                    student_id, subject, topic, learned_date, interval_days,
                    next_revision_date, last_reviewed_date, mastery_score, mistake_count, status
                ) VALUES (?, ?, ?, ?, 1, ?, ?, 50.0, 1, 'DUE');
            """, (student_id, subject, topic, today_str, today_str, today_str))
            conn.commit()
            new_id = cursor.lastrowid
            cursor.execute("SELECT * FROM revision_schedule WHERE id = ?;", (new_id,))
            row = dict(cursor.fetchone())
            return RevisionItemSchema(
                id=row["id"],
                subject=row["subject"],
                topic=row["topic"],
                learned_date=row["learned_date"],
                interval_days=row["interval_days"],
                next_revision_date=row["next_revision_date"],
                last_reviewed_date=row.get("last_reviewed_date"),
                mastery_score=float(row["mastery_score"]),
                mistake_count=row["mistake_count"],
                status=row["status"],
            )


revision_engine = RevisionEngine()
