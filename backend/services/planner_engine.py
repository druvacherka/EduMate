"""EduMate Adaptive Study Planner and Daily Task Scheduler.

Generates structured multi-week study plans and dynamically updates daily study tasks
based on student available hours, active goals, and retention status.
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
import uuid

from backend.database import (
    get_student_profile,
    list_daily_tasks,
    insert_daily_task,
    toggle_daily_task,
    get_db_connection,
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
from backend.services.curriculum_engine import curriculum_engine


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

    def generate_adaptive_plan(self, req: GeneratePlanRequest, student_id: int = 1) -> StudyPlanSchema:
        """Generate dynamic multi-week adaptive roadmap based on goal and target date."""
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        hours_per_day = req.available_hours_per_day or 2.0

        # Calculate weeks
        today = date.today()
        if req.target_date:
            try:
                target_dt = date.fromisoformat(req.target_date)
                delta_days = max(14, (target_dt - today).days)
                num_weeks = min(16, max(4, delta_days // 7))
            except Exception:
                num_weeks = 6
        else:
            num_weeks = 6

        weekly_items = []
        themes = [
            ("Foundational Concepts & Invariants", ["Core Principles", "Standard Definitions", "Basic Syntax"]),
            ("Intermediate Problem Solving & Applications", ["Classic Algorithms", "Edge Cases", "Implementation"]),
            ("Advanced Architecture & Complex Problems", ["Performance Bottlenecks", "System Design", "Complex Datasets"]),
            ("Integrated Multi-Topic Applications", ["Cross-Topic Questions", "Synthesis Problems", "Analytical Reasoning"]),
            ("Exam Simulations & Speed Optimization", ["Timed Practice", "Previous Year Papers", "Shortcuts"]),
            ("Comprehensive Weak-Area Review & Refinement", ["Error Log Deep-Dive", "High-Weightage Formulas", "Final Readiness"]),
        ]

        total_hours = 0.0
        for i in range(num_weeks):
            theme_idx = i % len(themes)
            theme_title, topics = themes[theme_idx]
            week_hrs = round(hours_per_day * 5, 1)  # 5 study days per week
            total_hours += week_hrs
            weekly_items.append(
                StudyPlanItemSchema(
                    week_number=i + 1,
                    theme=f"Week {i + 1}: {theme_title}",
                    focus_topics=[f"{req.goal_name} - {t}" for t in topics],
                    target_milestone=f"Achieve >={min(90, 60 + i * 5)}% mastery on {topics[0]}.",
                    estimated_hours=week_hrs,
                )
            )

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO study_plans (id, student_id, goal_id, title, target_date, total_hours_planned, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?);
            """, (plan_id, student_id, req.goal_id, f"Adaptive Plan: {req.goal_name}", req.target_date, total_hours, today.isoformat()))
            conn.commit()

        return StudyPlanSchema(
            id=plan_id,
            goal_id=req.goal_id,
            title=f"Adaptive Plan: {req.goal_name}",
            target_date=req.target_date,
            total_hours_planned=total_hours,
            status="ACTIVE",
            weekly_breakdown=weekly_items,
        )


planner_engine = PlannerEngine()
