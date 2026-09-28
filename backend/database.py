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
                current_subject TEXT NOT NULL DEFAULT 'Data Structures & Algorithms',
                current_topic TEXT NOT NULL DEFAULT 'Binary Search Trees',
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

        # Initialize default profile if empty with 0.0 initial mastery and 0 streak
        cursor.execute("SELECT COUNT(*) AS cnt FROM student_profile;")
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute("""
                INSERT INTO student_profile (
                    id, name, email, level, language, current_subject, current_topic,
                    mastery_score, study_streak_days, last_active_date
                ) VALUES (
                    1, 'Student', 'student@edumate.ai', 'Beginner', 'English',
                    'Computer Science', '', 0.0, 0, ?
                );
            """, (date.today().isoformat(),))

        conn.commit()


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


def update_student_settings(level: Optional[str] = None, language: Optional[str] = None, current_subject: Optional[str] = None, current_topic: Optional[str] = None) -> Dict[str, Any]:
    """Update student learning settings and return updated profile."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if level:
            cursor.execute("UPDATE student_profile SET level = ? WHERE id = 1;", (level,))
        if language:
            cursor.execute("UPDATE student_profile SET language = ? WHERE id = 1;", (language,))
        if current_subject:
            cursor.execute("UPDATE student_profile SET current_subject = ? WHERE id = 1;", (current_subject,))
        if current_topic:
            cursor.execute("UPDATE student_profile SET current_topic = ? WHERE id = 1;", (current_topic,))
        conn.commit()
    return get_student_profile()


def list_study_materials() -> List[Dict[str, Any]]:
    """List all registered PDF study materials."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_materials ORDER BY upload_date DESC;")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def insert_study_material(doc_id: str, name: str, subject: str, size_str: str, pages: int, chunks: int, status: str = "Ready") -> Dict[str, Any]:
    """Save a newly uploaded study material metadata record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        upload_date = date.today().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO study_materials (id, name, subject, upload_date, size_str, pages, chunks, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (doc_id, name, subject, upload_date, size_str, pages, chunks, status))
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
    }


def delete_study_material(doc_id: str) -> bool:
    """Delete a study material record by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM study_materials WHERE id = ?;", (doc_id,))
        conn.commit()
        return cursor.rowcount > 0


def reset_db_to_baseline() -> None:
    """Clear all dynamic session and study data to clean empty state."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM study_materials;")
        cursor.execute("DELETE FROM weak_areas;")
        cursor.execute("DELETE FROM strong_areas;")
        cursor.execute("DELETE FROM subject_progress;")
        cursor.execute("DELETE FROM quiz_sessions;")
        cursor.execute("""
            UPDATE student_profile
            SET name = 'Student', email = '', level = 'Beginner', language = 'English',
                current_subject = '', current_topic = '', mastery_score = 0.0,
                study_streak_days = 0
            WHERE id = 1;
        """)
        conn.commit()


# Call init_db on module import
init_db()

