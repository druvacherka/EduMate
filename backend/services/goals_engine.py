"""Student Multi-Goal Lifecycle Engine for EduMate.

Supports multiple concurrent goals (Semester Academics, Entrance Exams, Placements,
Competitive exams, Skill development) with priority and time allocation.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
import uuid

from backend.database import (
    list_student_goals,
    insert_student_goal,
    delete_student_goal,
    toggle_student_goal,
    select_active_goal,
)
from backend.schemas import StudentGoalSchema, CreateGoalRequest, UpdateGoalRequest


class GoalsEngine:
    """Manages creation, prioritization, time budgeting, and tracking of student goals."""

    def get_goals(self, student_id: int = 1) -> List[StudentGoalSchema]:
        """Fetch all goals formatted as Pydantic schemas."""
        rows = list_student_goals(student_id=student_id)
        return [
            StudentGoalSchema(
                id=r["id"],
                name=r["name"],
                goal_type=r["goal_type"],
                target_exam=r["target_exam"],
                target_date=r["target_date"],
                priority=r["priority"],
                available_hours_per_day=float(r["available_hours_per_day"]),
                current_level=r["current_level"],
                target_level=r["target_level"],
                is_active=bool(r["is_active"]),
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def create_goal(self, req: CreateGoalRequest, student_id: int = 1) -> StudentGoalSchema:
        """Create and store a new goal."""
        goal_id = f"goal-{uuid.uuid4().hex[:8]}"
        res = insert_student_goal(
            goal_id=goal_id,
            name=req.name,
            goal_type=req.goal_type,
            target_exam=req.target_exam,
            target_date=req.target_date,
            priority=req.priority,
            available_hours_per_day=req.available_hours_per_day,
            current_level=req.current_level,
            target_level=req.target_level,
            is_active=1,
            student_id=student_id,
        )
        return StudentGoalSchema(**res)

    def delete_goal(self, goal_id: str, student_id: int = 1) -> bool:
        """Delete an existing goal."""
        return delete_student_goal(goal_id=goal_id, student_id=student_id)

    def toggle_goal(self, goal_id: str, student_id: int = 1) -> Optional[StudentGoalSchema]:
        """Toggle active/inactive state of a goal."""
        row = toggle_student_goal(goal_id=goal_id, student_id=student_id)
        if not row:
            return None
        return StudentGoalSchema(
            id=row["id"],
            name=row["name"],
            goal_type=row["goal_type"],
            target_exam=row["target_exam"],
            target_date=row["target_date"],
            priority=row["priority"],
            available_hours_per_day=float(row["available_hours_per_day"]),
            current_level=row["current_level"],
            target_level=row["target_level"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )

    def select_goal(self, goal_id: str, student_id: int = 1) -> Optional[StudentGoalSchema]:
        """Select a single goal as primary active goal and adapt focus and daily tasks."""
        row = select_active_goal(goal_id=goal_id, student_id=student_id)
        if not row:
            return None
        return StudentGoalSchema(
            id=row["id"],
            name=row["name"],
            goal_type=row["goal_type"],
            target_exam=row["target_exam"],
            target_date=row["target_date"],
            priority=row["priority"],
            available_hours_per_day=float(row["available_hours_per_day"]),
            current_level=row["current_level"],
            target_level=row["target_level"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )

    def compute_daily_hours_budget(self, student_id: int = 1) -> float:
        """Compute sum of daily allocated hours across all active goals."""
        goals = self.get_goals(student_id=student_id)
        active_goals = [g for g in goals if g.is_active]
        if not active_goals:
            return 2.0
        return sum(g.available_hours_per_day for g in active_goals)


goals_engine = GoalsEngine()
