"""SQLite Database layer for EduMate Backend & Analytics Engine.

Provides persistent storage for study materials, quiz sessions, student profiles,
weak area tracking, and subject progress.
"""

import os
import sqlite3
import json
from datetime import datetime, date
from typing import Any, Dict, List, Optional

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "edumate.db")


def get_db_connection() -> sqlite3.Connection:
    """Create or return SQLite connection with dictionary row factory."""
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize SQLite database tables and seed baseline student profile."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Student Profile Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profile (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT 'Beginner',
                language TEXT NOT NULL DEFAULT 'English',
                current_subject TEXT NOT NULL DEFAULT '',
                current_topic TEXT NOT NULL DEFAULT '',
                mastery_score REAL NOT NULL DEFAULT 0.0,
                study_streak_days INTEGER NOT NULL DEFAULT 0,
                last_active_date TEXT NOT NULL
            );
        """)

        # 2. Study Materials Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_materials (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                upload_date TEXT NOT NULL,
                size_str TEXT NOT NULL,
                pages INTEGER NOT NULL DEFAULT 1,
                chunks INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'Ready'
            );
        """)

        # 3. Quiz Sessions & State Machine Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                percentage REAL NOT NULL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'CREATED',
                questions_json TEXT NOT NULL,
                user_answers_json TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            );
        """)

        # 4. Weak Areas Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weak_areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL UNIQUE,
                subject TEXT NOT NULL,
                mistake_count INTEGER NOT NULL DEFAULT 1,
                last_mistake_date TEXT NOT NULL,
                is_mastered INTEGER NOT NULL DEFAULT 0
            );
        """)

        # 5. Strong Areas Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strong_areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL UNIQUE,
                subject TEXT NOT NULL,
                success_count INTEGER NOT NULL DEFAULT 1
            );
        """)

        # 6. Subject Progress Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subject_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL UNIQUE,
                progress INTEGER NOT NULL DEFAULT 0,
                topics_completed INTEGER NOT NULL DEFAULT 0,
                total_topics INTEGER NOT NULL DEFAULT 10,
                status TEXT NOT NULL DEFAULT 'In Progress'
            );
        """)

        # 7. Student Goals Table (Supports multiple simultaneous goals)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_goals (
                id TEXT PRIMARY KEY,
                student_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                goal_type TEXT NOT NULL DEFAULT 'academic',
                target_exam TEXT,
                target_date TEXT,
                priority TEXT NOT NULL DEFAULT 'HIGH',
                available_hours_per_day REAL NOT NULL DEFAULT 2.0,
                current_level TEXT NOT NULL DEFAULT 'Beginner',
                target_level TEXT NOT NULL DEFAULT 'Advanced',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );
        """)

        # 8. Adaptive Study Plans Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_plans (
                id TEXT PRIMARY KEY,
                student_id INTEGER NOT NULL DEFAULT 1,
                goal_id TEXT,
                title TEXT NOT NULL,
                target_date TEXT,
                total_hours_planned REAL NOT NULL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL
            );
        """)

        # 9. Daily Study Tasks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_study_tasks (
                id TEXT PRIMARY KEY,
                plan_id TEXT,
                student_id INTEGER NOT NULL DEFAULT 1,
                task_type TEXT NOT NULL,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                estimated_minutes INTEGER NOT NULL DEFAULT 30,
                is_completed INTEGER NOT NULL DEFAULT 0,
                priority TEXT NOT NULL DEFAULT 'NORMAL',
                reason TEXT,
                date_scheduled TEXT NOT NULL
            );
        """)

        # 10. Spaced Revision Schedule Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revision_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL DEFAULT 1,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                learned_date TEXT NOT NULL,
                interval_days INTEGER NOT NULL DEFAULT 1,
                next_revision_date TEXT NOT NULL,
                last_reviewed_date TEXT,
                mastery_score REAL NOT NULL DEFAULT 50.0,
                mistake_count INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'DUE'
            );
        """)

        # 11. Voice Tutoring Sessions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_sessions (
                id TEXT PRIMARY KEY,
                student_id INTEGER NOT NULL DEFAULT 1,
                language TEXT NOT NULL DEFAULT 'English',
                topic TEXT,
                goal_id TEXT,
                duration_seconds INTEGER NOT NULL DEFAULT 0,
                transcript_summary TEXT,
                created_at TEXT NOT NULL
            );
        """)

        # Safe Column Additions for Student Profile Evolution
        cursor.execute("PRAGMA table_info(student_profile);")
        profile_columns = [col["name"] for col in cursor.fetchall()]

        new_columns = [
            ("education_level", "TEXT NOT NULL DEFAULT ''"),
            ("institution", "TEXT NOT NULL DEFAULT ''"),
            ("stream_branch", "TEXT NOT NULL DEFAULT ''"),
            ("academic_year_semester", "TEXT NOT NULL DEFAULT ''"),
            ("daily_study_hours", "REAL NOT NULL DEFAULT 0.0"),
            ("onboarding_completed", "INTEGER NOT NULL DEFAULT 0"),
            ("active_goal_id", "TEXT NOT NULL DEFAULT ''"),
        ]

        for col_name, col_def in new_columns:
            if col_name not in profile_columns:
                cursor.execute(f"ALTER TABLE student_profile ADD COLUMN {col_name} {col_def};")

        # Safe Column Additions for Study Materials Scoping
        cursor.execute("PRAGMA table_info(study_materials);")
        mat_columns = [col["name"] for col in cursor.fetchall()]
        mat_new_columns = [
            ("education_level", "TEXT DEFAULT 'All'"),
            ("curriculum", "TEXT DEFAULT 'General'"),
            ("goal_id", "TEXT DEFAULT ''"),
        ]
        for col_name, col_def in mat_new_columns:
            if col_name not in mat_columns:
                cursor.execute(f"ALTER TABLE study_materials ADD COLUMN {col_name} {col_def};")

        # Initialize default profile if empty
        cursor.execute("SELECT COUNT(*) AS cnt FROM student_profile;")
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute("""
                INSERT INTO student_profile (
                    id, name, email, level, language, current_subject, current_topic,
                    mastery_score, study_streak_days, last_active_date,
                    education_level, institution, stream_branch, academic_year_semester,
                    daily_study_hours, onboarding_completed, active_goal_id
                ) VALUES (
                    1, 'Student', '', 'Beginner', 'English',
                    '', '', 0.0, 0, ?,
                    '', '', '', '',
                    0.0, 0, ''
                );
            """, (date.today().isoformat(),))

        conn.commit()


def select_active_goal(goal_id: str, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Select the specified goal as active without fabricating study data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE student_goals SET is_active = 0 WHERE student_id = ?;", (student_id,))
        cursor.execute("UPDATE student_goals SET is_active = 1 WHERE id = ? AND student_id = ?;", (goal_id, student_id))
        cursor.execute("UPDATE student_profile SET active_goal_id = ? WHERE id = ?;", (goal_id, student_id))
        cursor.execute("SELECT * FROM student_goals WHERE id = ? AND student_id = ?;", (goal_id, student_id))
        row = cursor.fetchone()
        if not row:
            conn.commit()
            return None
        goal_data = dict(row)

        conn.commit()
        return goal_data


# Database Access Helpers

def get_student_profile() -> Dict[str, Any]:
    """Retrieve current student profile with live mastery and streak."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_profile WHERE id = 1;")
        row = cursor.fetchone()
        if not row:
            init_db()
            return get_student_profile()
        return dict(row)


def update_student_settings(
    level: Optional[str] = None,
    language: Optional[str] = None,
    current_subject: Optional[str] = None,
    current_topic: Optional[str] = None,
    name: Optional[str] = None,
    education_level: Optional[str] = None,
    institution: Optional[str] = None,
    stream_branch: Optional[str] = None,
    academic_year_semester: Optional[str] = None,
    daily_study_hours: Optional[float] = None,
    onboarding_completed: Optional[int] = None,
) -> Dict[str, Any]:
    """Update student learning settings and return updated profile."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if level is not None:
            cursor.execute("UPDATE student_profile SET level = ? WHERE id = 1;", (level,))
        if language is not None:
            cursor.execute("UPDATE student_profile SET language = ? WHERE id = 1;", (language,))
        if current_subject is not None:
            cursor.execute("UPDATE student_profile SET current_subject = ? WHERE id = 1;", (current_subject,))
        if current_topic is not None:
            cursor.execute("UPDATE student_profile SET current_topic = ? WHERE id = 1;", (current_topic,))
        if name is not None:
            cursor.execute("UPDATE student_profile SET name = ? WHERE id = 1;", (name,))
        if education_level is not None:
            cursor.execute("UPDATE student_profile SET education_level = ? WHERE id = 1;", (education_level,))
        if institution is not None:
            cursor.execute("UPDATE student_profile SET institution = ? WHERE id = 1;", (institution,))
        if stream_branch is not None:
            cursor.execute("UPDATE student_profile SET stream_branch = ? WHERE id = 1;", (stream_branch,))
        if academic_year_semester is not None:
            cursor.execute("UPDATE student_profile SET academic_year_semester = ? WHERE id = 1;", (academic_year_semester,))
        if daily_study_hours is not None:
            cursor.execute("UPDATE student_profile SET daily_study_hours = ? WHERE id = 1;", (daily_study_hours,))
        if onboarding_completed is not None:
            cursor.execute("UPDATE student_profile SET onboarding_completed = ? WHERE id = 1;", (onboarding_completed,))
        conn.commit()
    return get_student_profile()


# Student Goals Management Helpers

def list_student_goals(student_id: int = 1) -> List[Dict[str, Any]]:
    """List all goals for a student ordered by priority and creation."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM student_goals
            WHERE student_id = ?
            ORDER BY is_active DESC, 
                     CASE priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END ASC,
                     created_at DESC;
        """, (student_id,))
        return [dict(r) for r in cursor.fetchall()]


def insert_student_goal(
    goal_id: str,
    name: str,
    goal_type: str = "academic",
    target_exam: Optional[str] = None,
    target_date: Optional[str] = None,
    priority: str = "HIGH",
    available_hours_per_day: float = 2.0,
    current_level: str = "Beginner",
    target_level: str = "Advanced",
    is_active: int = 1,
    student_id: int = 1,
) -> Dict[str, Any]:
    """Insert or update a student goal."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        created_at = date.today().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO student_goals (
                id, student_id, name, goal_type, target_exam, target_date,
                priority, available_hours_per_day, current_level, target_level, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            goal_id, student_id, name, goal_type, target_exam, target_date,
            priority, available_hours_per_day, current_level, target_level, is_active, created_at
        ))
        conn.commit()
    return {
        "id": goal_id,
        "name": name,
        "goal_type": goal_type,
        "target_exam": target_exam,
        "target_date": target_date,
        "priority": priority,
        "available_hours_per_day": available_hours_per_day,
        "current_level": current_level,
        "target_level": target_level,
        "is_active": is_active,
        "created_at": created_at,
    }


def delete_student_goal(goal_id: str, student_id: int = 1) -> bool:
    """Delete a student goal by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student_goals WHERE id = ? AND student_id = ?;", (goal_id, student_id))
        conn.commit()
        return cursor.rowcount > 0


def toggle_student_goal(goal_id: str, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Toggle a goal active/inactive."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM student_goals WHERE id = ? AND student_id = ?;", (goal_id, student_id))
        row = cursor.fetchone()
        if not row:
            return None
        new_status = 0 if row["is_active"] == 1 else 1
        cursor.execute("UPDATE student_goals SET is_active = ? WHERE id = ? AND student_id = ?;", (new_status, goal_id, student_id))
        conn.commit()
        cursor.execute("SELECT * FROM student_goals WHERE id = ?;", (goal_id,))
        return dict(cursor.fetchone())


# Daily Tasks & Planner Helpers

def list_daily_tasks(student_id: int = 1, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch daily study tasks for a given date."""
    query_date = target_date or date.today().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM daily_study_tasks
            WHERE student_id = ? AND date_scheduled = ?
            ORDER BY is_completed ASC, 
                     CASE priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END ASC;
        """, (student_id, query_date))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def insert_daily_task(
    task_id: str,
    title: str,
    subject: str,
    topic: str,
    task_type: str = "LEARN",
    estimated_minutes: int = 30,
    priority: str = "NORMAL",
    reason: Optional[str] = None,
    plan_id: Optional[str] = None,
    date_scheduled: Optional[str] = None,
    student_id: int = 1,
) -> Dict[str, Any]:
    """Insert a daily study task."""
    sched_date = date_scheduled or date.today().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO daily_study_tasks (
                id, plan_id, student_id, task_type, title, subject, topic,
                estimated_minutes, is_completed, priority, reason, date_scheduled
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?);
        """, (
            task_id, plan_id, student_id, task_type, title, subject, topic,
            estimated_minutes, priority, reason, sched_date
        ))
        conn.commit()
    return {
        "id": task_id,
        "title": title,
        "subject": subject,
        "topic": topic,
        "task_type": task_type,
        "estimated_minutes": estimated_minutes,
        "is_completed": False,
        "priority": priority,
        "reason": reason,
        "date_scheduled": sched_date,
    }


def toggle_daily_task(task_id: str, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Toggle completion status of a daily task."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_completed FROM daily_study_tasks WHERE id = ? AND student_id = ?;", (task_id, student_id))
        row = cursor.fetchone()
        if not row:
            return None
        new_completed = 0 if row["is_completed"] == 1 else 1
        cursor.execute("UPDATE daily_study_tasks SET is_completed = ? WHERE id = ? AND student_id = ?;", (new_completed, task_id, student_id))
        
        # Increment streak if completing a task
        if new_completed == 1:
            cursor.execute("UPDATE student_profile SET study_streak_days = study_streak_days + 1 WHERE id = 1;")
        conn.commit()
        cursor.execute("SELECT * FROM daily_study_tasks WHERE id = ?;", (task_id,))
        return dict(cursor.fetchone())


# Spaced Revision Schedule Helpers

def list_revision_items(student_id: int = 1, due_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieve spaced repetition revision items."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        today_str = date.today().isoformat()
        if due_only:
            cursor.execute("""
                SELECT * FROM revision_schedule
                WHERE student_id = ? AND (next_revision_date <= ? OR status = 'DUE')
                ORDER BY mistake_count DESC, next_revision_date ASC;
            """, (student_id, today_str))
        else:
            cursor.execute("""
                SELECT * FROM revision_schedule
                WHERE student_id = ?
                ORDER BY next_revision_date ASC;
            """, (student_id,))
        return [dict(r) for r in cursor.fetchall()]


def record_revision_completion(item_id: int, score: float, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Update spaced revision item after completion using Leitner spacing."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM revision_schedule WHERE id = ? AND student_id = ?;", (item_id, student_id))
        row = cursor.fetchone()
        if not row:
            return None
        
        curr_interval = row["interval_days"]
        today = date.today()
        today_str = today.isoformat()
        
        if score >= 75.0:
            new_interval = max(3, curr_interval * 2)
            new_status = "COMPLETED"
        else:
            new_interval = 1
            new_status = "DUE"
            
        from datetime import timedelta
        next_date = (today + timedelta(days=new_interval)).isoformat()
        
        cursor.execute("""
            UPDATE revision_schedule
            SET interval_days = ?, next_revision_date = ?, last_reviewed_date = ?,
                mastery_score = ?, status = ?
            WHERE id = ? AND student_id = ?;
        """, (new_interval, next_date, today_str, score, new_status, item_id, student_id))
        conn.commit()
        cursor.execute("SELECT * FROM revision_schedule WHERE id = ?;", (item_id,))
        return dict(cursor.fetchone())


# Voice Sessions Helpers

def record_voice_session(
    session_id: str,
    language: str,
    topic: Optional[str] = None,
    goal_id: Optional[str] = None,
    duration_seconds: int = 0,
    transcript_summary: Optional[str] = None,
    student_id: int = 1,
) -> Dict[str, Any]:
    """Record metadata for a voice tutoring session."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        created_at = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO voice_sessions (
                id, student_id, language, topic, goal_id, duration_seconds, transcript_summary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (session_id, student_id, language, topic, goal_id, duration_seconds, transcript_summary, created_at))
        conn.commit()
    return {
        "id": session_id,
        "language": language,
        "topic": topic,
        "goal_id": goal_id,
        "duration_seconds": duration_seconds,
        "created_at": created_at,
    }


def list_voice_sessions(student_id: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
    """List recent voice sessions."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM voice_sessions
            WHERE student_id = ?
            ORDER BY created_at DESC
            LIMIT ?;
        """, (student_id, limit))
        return [dict(r) for r in cursor.fetchall()]


# Existing Study Material Helpers

def list_study_materials() -> List[Dict[str, Any]]:
    """List all registered PDF study materials."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_materials ORDER BY upload_date DESC;")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def insert_study_material(
    doc_id: str,
    name: str,
    subject: str,
    size_str: str,
    pages: int,
    chunks: int,
    status: str = "Ready",
    education_level: str = "All",
    curriculum: str = "General",
    goal_id: str = "",
) -> Dict[str, Any]:
    """Save a newly uploaded study material metadata record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        upload_date = date.today().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO study_materials (
                id, name, subject, upload_date, size_str, pages, chunks, status,
                education_level, curriculum, goal_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (doc_id, name, subject, upload_date, size_str, pages, chunks, status, education_level, curriculum, goal_id))
        conn.commit()
    return {
        "id": doc_id,
        "name": name,
        "subject": subject,
        "uploadDate": upload_date,
        "size": size_str,
        "pages": pages,
        "chunks": chunks,
        "status": status,
        "education_level": education_level,
        "curriculum": curriculum,
        "goal_id": goal_id,
    }


def delete_study_material(doc_id: str) -> bool:
    """Delete a study material record by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM study_materials WHERE id = ?;", (doc_id,))
        conn.commit()
        return cursor.rowcount > 0


def reset_db_to_baseline() -> None:
    """Clear dynamic study data without repopulating mock records."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quiz_sessions;")
        cursor.execute("DELETE FROM voice_sessions;")
        cursor.execute("DELETE FROM daily_study_tasks;")
        cursor.execute("DELETE FROM revision_schedule;")
        cursor.execute("DELETE FROM weak_areas;")
        cursor.execute("DELETE FROM strong_areas;")
        cursor.execute("DELETE FROM subject_progress;")
        conn.commit()


# Call init_db on module import
init_db()
