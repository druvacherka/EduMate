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
                mastery_score REAL NOT NULL DEFAULT 78.5,
                study_streak_days INTEGER NOT NULL DEFAULT 5,
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

        # Seed default profile if empty
        cursor.execute("SELECT COUNT(*) AS cnt FROM student_profile;")
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute("""
                INSERT INTO student_profile (
                    id, name, email, level, language, current_subject, current_topic,
                    mastery_score, study_streak_days, last_active_date
                ) VALUES (
                    1, 'B.Tech Student', 'student@edumate.ai', 'Beginner', 'English',
                    'Data Structures & Algorithms', 'Binary Search Trees', 78.5, 5, ?
                );
            """, (date.today().isoformat(),))

        # Seed initial study materials if empty
        cursor.execute("SELECT COUNT(*) AS cnt FROM study_materials;")
        if cursor.fetchone()["cnt"] == 0:
            sample_docs = [
                ("doc-1", "Data_Structures_Unit3_Trees.pdf", "Data Structures", "2026-08-25", "2.4 MB", 28, 84, "Ready"),
                ("doc-2", "DBMS_Unit_2_Normalization.pdf", "Database Management", "2026-08-26", "1.8 MB", 18, 52, "Ready"),
                ("doc-3", "Algorithms_Sorting_Searching_Notes.pdf", "Algorithms", "2026-08-28", "3.1 MB", 35, 110, "Ready"),
            ]
            cursor.executemany("""
                INSERT INTO study_materials (id, name, subject, upload_date, size_str, pages, chunks, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, sample_docs)

        # Seed initial weak & strong areas if empty
        cursor.execute("SELECT COUNT(*) AS cnt FROM weak_areas;")
        if cursor.fetchone()["cnt"] == 0:
            initial_weak = [
                ("Tree Balancing", "Data Structures", 3, date.today().isoformat()),
                ("Graph Traversals", "Algorithms", 2, date.today().isoformat()),
                ("Recurrence Relations", "Algorithms", 4, date.today().isoformat()),
            ]
            cursor.executemany("""
                INSERT INTO weak_areas (topic, subject, mistake_count, last_mistake_date)
                VALUES (?, ?, ?, ?);
            """, initial_weak)

        cursor.execute("SELECT COUNT(*) AS cnt FROM strong_areas;")
        if cursor.fetchone()["cnt"] == 0:
            initial_strong = [
                ("Arrays & HashMaps", "Data Structures", 5),
                ("Sorting Algorithms", "Algorithms", 4),
                ("Stack Operations", "Data Structures", 6),
            ]
            cursor.executemany("""
                INSERT INTO strong_areas (topic, subject, success_count)
                VALUES (?, ?, ?);
            """, initial_strong)

        # Seed initial subject progress if empty
        cursor.execute("SELECT COUNT(*) AS cnt FROM subject_progress;")
        if cursor.fetchone()["cnt"] == 0:
            initial_progress = [
                ("Data Structures", 85, 12, 14, "Strong"),
                ("Database Management", 72, 8, 11, "Moderate"),
                ("Algorithms", 60, 6, 10, "Needs Review"),
                ("Operating Systems", 45, 4, 9, "Needs Review"),
            ]
            cursor.executemany("""
                INSERT INTO subject_progress (subject_name, progress, topics_completed, total_topics, status)
                VALUES (?, ?, ?, ?, ?);
            """, initial_progress)

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


# Call init_db on module import
init_db()
