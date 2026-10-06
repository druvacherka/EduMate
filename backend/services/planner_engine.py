"""EduMate Adaptive Study Planner and Daily Task Scheduler.

Generates structured multi-week study plans and dynamically updates daily study tasks
based on student available hours, active goals, and retention status.
"""

from datetime import date, datetime
import math
from typing import Any, Dict, List, Optional
import uuid

from backend.database import (
    get_student_profile,
    list_daily_tasks,
    toggle_daily_task,
    get_db_connection,
    list_student_goals,
)
from backend.schemas import (
    DailyDashboardResponse,
    DailyTaskSchema,
    StudyPlanSchema,
    StudyPlanItemSchema,
    GeneratePlanRequest,
)
from backend.services.goals_engine import goals_engine
from backend.services.recommendation_engine import recommendation_engine
from services.ai_rag.llm_client import llm_client


class PlannerEngine:
    """Orchestrates long-term adaptive roadmaps and daily execution tasks."""

    def get_or_generate_today_tasks(self, student_id: int = 1) -> List[DailyTaskSchema]:
        """Fetch existing daily tasks for today without creating placeholder work."""
        today_str = date.today().isoformat()
        existing = list_daily_tasks(student_id=student_id, target_date=today_str)
        return [
            DailyTaskSchema(
                id=t["id"],
                title=t["title"],
                subject=t["subject"],
                topic=t["topic"],
                task_type=t["task_type"],
                estimated_minutes=t["estimated_minutes"],
                is_completed=bool(t["is_completed"]),
                priority=t["priority"],
                reason=t.get("reason"),
                date_scheduled=t["date_scheduled"],
                plan_id=t.get("plan_id"),
            )
            for t in existing
        ]

    def toggle_task(self, task_id: str, student_id: int = 1) -> Optional[DailyTaskSchema]:
        """Mark task completed or incomplete."""
        row = toggle_daily_task(task_id=task_id, student_id=student_id)
        if not row:
            return None
        return DailyTaskSchema(
            id=row["id"],
            title=row["title"],
            subject=row["subject"],
            topic=row["topic"],
            task_type=row["task_type"],
            estimated_minutes=row["estimated_minutes"],
            is_completed=bool(row["is_completed"]),
            priority=row["priority"],
            reason=row.get("reason"),
            date_scheduled=row["date_scheduled"],
            plan_id=row.get("plan_id"),
        )

    def get_daily_dashboard(self, student_id: int = 1) -> DailyDashboardResponse:
        """Construct full daily study dashboard with greeting, tasks, and progress."""
        profile = get_student_profile(student_id)
        goals = goals_engine.get_goals(student_id=student_id)
        active_goals = [g for g in goals if g.is_active]
        today_tasks = self.get_or_generate_today_tasks(student_id=student_id)

        # Dynamic greeting based on time of day
        curr_hour = datetime.now().hour
        if curr_hour < 12:
            time_greet = "Good morning"
        elif curr_hour < 17:
            time_greet = "Good afternoon"
        else:
            time_greet = "Good evening"

        greeting = f"{time_greet}, {profile.get('name', 'Student')}!"

        completed_count = sum(1 for t in today_tasks if t.is_completed)
        total_count = len(today_tasks)
        remaining_minutes = sum(t.estimated_minutes for t in today_tasks if not t.is_completed)

        # Fetch weak areas
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT topic FROM weak_areas WHERE student_id = ? AND is_mastered = 0 ORDER BY mistake_count DESC LIMIT 4;",
                (student_id,),
            )
            weak_rows = cursor.fetchall()
            priority_weaks = [r["topic"] for r in weak_rows]

        rec = None
        if priority_weaks or active_goals or profile.get("current_topic"):
            rec = recommendation_engine.get_next_recommendation(student_id=student_id)

        return DailyDashboardResponse(
            greeting=greeting,
            student_name=profile.get("name", "Student"),
            education_level=profile.get("education_level", ""),
            stream_branch=profile.get("stream_branch", ""),
            available_hours_today=profile.get("daily_study_hours", 0.0),
            study_streak_days=profile.get("study_streak_days", 0),
            overall_mastery=profile.get("mastery_score", 0.0),
            active_goals=active_goals,
            today_tasks=today_tasks,
            total_tasks_count=total_count,
            completed_tasks_count=completed_count,
            estimated_time_remaining_minutes=remaining_minutes,
            priority_weak_areas=priority_weaks,
            recent_recommendation=rec,
        )

    async def generate_adaptive_plan(
        self,
        req: GeneratePlanRequest,
        student_id: int = 1,
    ) -> StudyPlanSchema:
        """Generate and persist a Gemini roadmap using this student's goal and progress."""
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        today = date.today()
        profile = get_student_profile(student_id)
        goals = list_student_goals(student_id=student_id)
        goal = next((item for item in goals if item["id"] == req.goal_id), None) if req.goal_id else None
        if req.goal_id and goal is None:
            raise LookupError("The selected goal was not found.")

        goal_name = goal["name"] if goal else req.goal_name.strip()
        target_date = (
            req.target_date
            if req.target_date is not None
            else (goal.get("target_date") if goal else None)
        )
        target_date = target_date or None
        hours_per_day = req.available_hours_per_day
        current_level = (
            req.current_level
            or (goal.get("current_level") if goal else None)
            or profile.get("level")
            or "Beginner"
        )
        target_level = (
            req.target_level
            or (goal.get("target_level") if goal else None)
            or "Advanced"
        )

        if target_date:
            try:
                target_dt = date.fromisoformat(target_date)
            except ValueError as exc:
                raise ValueError("Target date must use YYYY-MM-DD format.") from exc
            days_until_target = (target_dt - today).days
            if days_until_target <= 0:
                raise ValueError("Target date must be in the future.")
            num_weeks = min(16, max(1, math.ceil(days_until_target / 7)))
        else:
            num_weeks = 6

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT topic FROM weak_areas
                WHERE student_id = ? AND is_mastered = 0
                ORDER BY mistake_count DESC, last_mistake_date DESC
                LIMIT 5;
                """,
                (student_id,),
            )
            weak_areas = [row["topic"] for row in cursor.fetchall()]

        generated_weeks = await llm_client.generate_adaptive_study_plan(
            goal_name=goal_name,
            target_date=target_date,
            available_hours_per_day=hours_per_day,
            current_level=current_level,
            target_level=target_level,
            education_level=profile.get("education_level", ""),
            subject=profile.get("current_subject", ""),
            weak_areas=weak_areas,
            mastery_score=float(profile.get("mastery_score", 0.0)),
            num_weeks=num_weeks,
        )
        if len(generated_weeks) != num_weeks:
            raise ValueError(
                f"Gemini returned {len(generated_weeks)} weeks; expected {num_weeks}."
            )
        if [week["week_number"] for week in generated_weeks] != list(range(1, num_weeks + 1)):
            raise ValueError("Gemini returned an invalid adaptive plan week sequence.")

        weekly_hours = round(hours_per_day * 5, 1)
        weekly_items = [
            StudyPlanItemSchema(
                week_number=week["week_number"],
                theme=week["theme"],
                focus_topics=week["focus_topics"],
                target_milestone=week["target_milestone"],
                estimated_hours=weekly_hours,
            )
            for week in generated_weeks
        ]
        total_hours = round(sum(item.estimated_hours for item in weekly_items), 1)
        title = f"Adaptive Plan: {goal_name}"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            if req.goal_id:
                cursor.execute(
                    """
                    UPDATE study_plans SET status = 'SUPERSEDED'
                    WHERE student_id = ? AND goal_id = ? AND status = 'ACTIVE';
                    """,
                    (student_id, req.goal_id),
                )
            cursor.execute("""
                INSERT OR REPLACE INTO study_plans (id, student_id, goal_id, title, target_date, total_hours_planned, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?);
            """, (plan_id, student_id, req.goal_id, title, target_date, total_hours, today.isoformat()))
            conn.commit()

        return StudyPlanSchema(
            id=plan_id,
            goal_id=req.goal_id,
            title=title,
            target_date=target_date,
            total_hours_planned=total_hours,
            status="ACTIVE",
            weekly_breakdown=weekly_items,
        )


planner_engine = PlannerEngine()
