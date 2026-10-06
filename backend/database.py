"""Database layer for EduMate Backend & Analytics Engine.

Stores student data, study materials, quiz sessions, and learning plans in a
reliable relational database. Defaults to PostgreSQL for multi-user scalability,
while retaining explicitly configured SQLite support for local development and tests.
"""

import os
import sqlite3
import re
import json
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, text

from backend.config import settings

DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "edumate.db")
DATABASE_URL = getattr(settings, "database_url", "") or ""
IS_POSTGRES = DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg://", "postgresql+psycopg2://"))
logger = logging.getLogger(__name__)

if IS_POSTGRES:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=1800,
        connect_args={"connect_timeout": 5},
    )
else:
    engine = None


class PostgresConnection:
    """Compatibility wrapper around a SQLAlchemy connection for SQLite-style code."""

    def __init__(self, connection: Any):
        self._connection = connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.commit()
            else:
                self._connection.rollback()
        finally:
            self.close()

    def cursor(self):
        return PostgresCursor(self._connection)

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()


class PostgresCursor:
    def __init__(self, connection: Any):
        self._connection = connection
        self._result = None

    def execute(self, sql: str, params: tuple = ()) -> "PostgresCursor":
        normalized_sql, bound_params = _normalize_sql_for_postgres(sql, params or ())
        self._result = self._connection.execute(text(normalized_sql), bound_params)
        return self

    def fetchone(self):
        if not self._result:
            return None
        row = self._result.fetchone()
        return dict(row._mapping) if row is not None else None

    def fetchall(self):
        if not self._result:
            return []
        return [dict(row._mapping) for row in self._result.fetchall()]

    @property
    def rowcount(self) -> int:
        if not self._result:
            return 0
        return int(getattr(self._result, "rowcount", 0) or 0)


class SQLiteConnection:
    """Give SQLite the same close-on-exit behavior as pooled PostgreSQL connections."""

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            return self._connection.__exit__(exc_type, exc_val, exc_tb)
        finally:
            self._connection.close()

    def cursor(self):
        return self._connection.cursor()

    def execute(self, *args, **kwargs):
        return self._connection.execute(*args, **kwargs)

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()


def _normalize_sql_for_postgres(sql: str, params: tuple) -> tuple[str, Dict[str, Any]]:
    """Translate SQLite-style positional SQL to SQLAlchemy/PostgreSQL syntax."""
    normalized = sql.strip().rstrip(";")
    parameter_names = [f"p{index}" for index in range(len(params))]
    bound_params = dict(zip(parameter_names, params))
    replace_match = re.search(
        r"(?is)^\s*INSERT\s+OR\s+REPLACE\s+INTO\s+([A-Za-z0-9_]+)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)\s*$",
        normalized,
    )
    if replace_match:
        table_name, columns_sql, values_sql = replace_match.groups()
        column_names = [column.strip().strip('"`') for column in columns_sql.split(",") if column.strip()]
        key_columns = ", ".join(column_names[:1])
        assignments = ", ".join(f"{column} = EXCLUDED.{column}" for column in column_names[1:])
        index = 0

        def replace_insert_parameter(_match):
            nonlocal index
            if index >= len(parameter_names):
                raise ValueError("SQL parameter count does not match supplied values")
            name = parameter_names[index]
            index += 1
            return f":{name}"

        values_sql = re.sub(r"\?", replace_insert_parameter, values_sql)
        if index != len(parameter_names):
            raise ValueError("SQL parameter count does not match supplied values")
        normalized = (
            f"INSERT INTO {table_name} ({columns_sql}) VALUES ({values_sql}) "
            f"ON CONFLICT ({key_columns}) DO UPDATE SET {assignments}"
        )
    else:
        index = 0

        def replace_parameter(_match):
            nonlocal index
            if index >= len(parameter_names):
                raise ValueError("SQL parameter count does not match supplied values")
            name = parameter_names[index]
            index += 1
            return f":{name}"

        normalized = re.sub(r"\?", replace_parameter, normalized)
        if index != len(parameter_names):
            raise ValueError("SQL parameter count does not match supplied values")

    normalized = re.sub(r"\bMAX\(([-\w.]+),\s*([-\w.]+)\)", r"GREATEST(\1, \2)", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bMIN\(([-\w.]+),\s*([-\w.]+)\)", r"LEAST(\1, \2)", normalized, flags=re.IGNORECASE)
    return normalized, bound_params


def get_db_connection():
    """Create a connection to the configured database without splitting data stores."""
    if IS_POSTGRES:
        return PostgresConnection(engine.connect())

    sqlite_path = DATABASE_URL.removeprefix("sqlite:///")
    conn = sqlite3.connect(sqlite_path or DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return SQLiteConnection(conn)


def _migrate_sqlite_scoped_uniques(cursor) -> None:
    """Replace legacy global unique keys with per-student unique keys."""
    definitions = {
        "weak_areas": (
            ("student_id", "topic"),
            """
            CREATE TABLE weak_areas_scoped (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL DEFAULT 1,
                topic TEXT NOT NULL,
                subject TEXT NOT NULL,
                mistake_count INTEGER NOT NULL DEFAULT 1,
                last_mistake_date TEXT NOT NULL,
                is_mastered INTEGER NOT NULL DEFAULT 0,
                CONSTRAINT weak_areas_student_topic_key UNIQUE(student_id, topic)
            )
            """,
            "id, student_id, topic, subject, mistake_count, last_mistake_date, is_mastered",
        ),
        "strong_areas": (
            ("student_id", "topic"),
            """
            CREATE TABLE strong_areas_scoped (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL DEFAULT 1,
                topic TEXT NOT NULL,
                subject TEXT NOT NULL,
                success_count INTEGER NOT NULL DEFAULT 1,
                CONSTRAINT strong_areas_student_topic_key UNIQUE(student_id, topic)
            )
            """,
            "id, student_id, topic, subject, success_count",
        ),
        "subject_progress": (
            ("student_id", "subject_name"),
            """
            CREATE TABLE subject_progress_scoped (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL DEFAULT 1,
                subject_name TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                topics_completed INTEGER NOT NULL DEFAULT 0,
                total_topics INTEGER NOT NULL DEFAULT 10,
                status TEXT NOT NULL DEFAULT 'In Progress',
                CONSTRAINT subject_progress_student_subject_key UNIQUE(student_id, subject_name)
            )
            """,
            "id, student_id, subject_name, progress, topics_completed, total_topics, status",
        ),
    }

    for table_name, (scoped_columns, create_sql, column_list) in definitions.items():
        cursor.execute(f"PRAGMA index_list({table_name});")
        indexes = cursor.fetchall()
        has_global_unique = False
        has_scoped_unique = False
        for index in indexes:
            if index["origin"] == "pk" or not index["unique"]:
                continue
            cursor.execute(f"PRAGMA index_info({index['name']});")
            index_columns = tuple(row["name"] for row in cursor.fetchall())
            if index_columns == scoped_columns:
                has_scoped_unique = True
            else:
                has_global_unique = True
        if has_global_unique and not has_scoped_unique:
            scoped_table = f"{table_name}_scoped"
            cursor.execute(f"DROP TABLE IF EXISTS {scoped_table};")
            cursor.execute(create_sql)
            cursor.execute(f"INSERT INTO {scoped_table} ({column_list}) SELECT {column_list} FROM {table_name};")
            cursor.execute(f"DROP TABLE {table_name};")
            cursor.execute(f"ALTER TABLE {scoped_table} RENAME TO {table_name};")


def init_db() -> None:
    """Initialize the configured relational schema."""
    try:
        if IS_POSTGRES:
            _init_postgres_db()
            return

        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)

            # 1. Student Profile Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student_profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE REFERENCES app_users(id),
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    level TEXT NOT NULL DEFAULT '',
                    language TEXT NOT NULL DEFAULT '',
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
                    student_id INTEGER NOT NULL DEFAULT 1,
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
                    student_id INTEGER NOT NULL DEFAULT 1,
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
                    student_id INTEGER NOT NULL DEFAULT 1,
                    topic TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    mistake_count INTEGER NOT NULL DEFAULT 1,
                    last_mistake_date TEXT NOT NULL,
                    is_mastered INTEGER NOT NULL DEFAULT 0,
                    CONSTRAINT weak_areas_student_topic_key UNIQUE(student_id, topic)
                );
            """)

            # 5. Strong Areas Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strong_areas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL DEFAULT 1,
                    topic TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    success_count INTEGER NOT NULL DEFAULT 1,
                    CONSTRAINT strong_areas_student_topic_key UNIQUE(student_id, topic)
                );
            """)

            # 6. Subject Progress Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subject_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL DEFAULT 1,
                    subject_name TEXT NOT NULL,
                    progress INTEGER NOT NULL DEFAULT 0,
                    topics_completed INTEGER NOT NULL DEFAULT 0,
                    total_topics INTEGER NOT NULL DEFAULT 10,
                    status TEXT NOT NULL DEFAULT 'In Progress',
                    CONSTRAINT subject_progress_student_subject_key UNIQUE(student_id, subject_name)
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
                    current_level TEXT NOT NULL DEFAULT '',
                    target_level TEXT NOT NULL DEFAULT '',
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
                    language TEXT NOT NULL DEFAULT '',
                    topic TEXT,
                    goal_id TEXT,
                    duration_seconds INTEGER NOT NULL DEFAULT 0,
                    transcript_summary TEXT,
                    created_at TEXT NOT NULL
                );
            """)

            cursor.execute("PRAGMA table_info(student_profile);")
            profile_columns = [col["name"] for col in cursor.fetchall()]

            new_columns = [
                ("user_id", "INTEGER REFERENCES app_users(id)"),
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

            scoped_tables = ("study_materials", "quiz_sessions", "weak_areas", "strong_areas", "subject_progress")
            for table_name in scoped_tables:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [col["name"] for col in cursor.fetchall()]
                if "student_id" not in columns:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN student_id INTEGER NOT NULL DEFAULT 1;")

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

            _migrate_sqlite_scoped_uniques(cursor)
            conn.commit()
    except Exception:
        logger.exception("Database initialization failed")
        raise


def _init_postgres_db() -> None:
    """Create PostgreSQL tables used by EduMate."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_users (
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profile (
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                user_id INTEGER UNIQUE REFERENCES app_users(id),
                name TEXT NOT NULL,
                email TEXT NOT NULL DEFAULT '',
                level TEXT NOT NULL DEFAULT '',
                language TEXT NOT NULL DEFAULT '',
                current_subject TEXT NOT NULL DEFAULT '',
                current_topic TEXT NOT NULL DEFAULT '',
                mastery_score REAL NOT NULL DEFAULT 0.0,
                study_streak_days INTEGER NOT NULL DEFAULT 0,
                last_active_date TEXT NOT NULL,
                education_level TEXT NOT NULL DEFAULT '',
                institution TEXT NOT NULL DEFAULT '',
                stream_branch TEXT NOT NULL DEFAULT '',
                academic_year_semester TEXT NOT NULL DEFAULT '',
                daily_study_hours REAL NOT NULL DEFAULT 0.0,
                onboarding_completed INTEGER NOT NULL DEFAULT 0,
                active_goal_id TEXT NOT NULL DEFAULT ''
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_embeddings (
                id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                student_id INTEGER NOT NULL REFERENCES student_profile(id) ON DELETE CASCADE,
                document_id TEXT NOT NULL,
                chunk_id TEXT NOT NULL,
                document_name TEXT NOT NULL,
                page_number INTEGER NOT NULL CHECK (page_number >= 1),
                content TEXT NOT NULL,
                section_title TEXT,
                subject TEXT,
                topic TEXT,
                char_count INTEGER NOT NULL DEFAULT 0,
                embedding vector(768) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT study_embeddings_owner_document_chunk_key
                    UNIQUE (student_id, document_id, chunk_id)
            );
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS study_embeddings_embedding_hnsw_idx
            ON study_embeddings USING hnsw (embedding vector_cosine_ops);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS study_embeddings_student_id_idx
            ON study_embeddings (student_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS study_embeddings_content_fts_idx
            ON study_embeddings USING gin (to_tsvector('simple', content));
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_materials (
                id TEXT PRIMARY KEY,
                student_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                upload_date TEXT NOT NULL,
                size_str TEXT NOT NULL,
                pages INTEGER NOT NULL DEFAULT 1,
                chunks INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'Ready',
                education_level TEXT DEFAULT 'All',
                curriculum TEXT DEFAULT 'General',
                goal_id TEXT DEFAULT ''
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id TEXT PRIMARY KEY,
                student_id INTEGER NOT NULL DEFAULT 1,
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weak_areas (
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                student_id INTEGER NOT NULL DEFAULT 1,
                topic TEXT NOT NULL,
                subject TEXT NOT NULL,
                mistake_count INTEGER NOT NULL DEFAULT 1,
                last_mistake_date TEXT NOT NULL,
                is_mastered INTEGER NOT NULL DEFAULT 0,
                UNIQUE(student_id, topic)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strong_areas (
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                student_id INTEGER NOT NULL DEFAULT 1,
                topic TEXT NOT NULL,
                subject TEXT NOT NULL,
                success_count INTEGER NOT NULL DEFAULT 1,
                UNIQUE(student_id, topic)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subject_progress (
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                student_id INTEGER NOT NULL DEFAULT 1,
                subject_name TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                topics_completed INTEGER NOT NULL DEFAULT 0,
                total_topics INTEGER NOT NULL DEFAULT 10,
                status TEXT NOT NULL DEFAULT 'In Progress',
                UNIQUE(student_id, subject_name)
            );
        """)
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
                current_level TEXT NOT NULL DEFAULT '',
                target_level TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );
        """)
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revision_schedule (
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_sessions (
                id TEXT PRIMARY KEY,
                student_id INTEGER NOT NULL DEFAULT 1,
                language TEXT NOT NULL DEFAULT '',
                topic TEXT,
                goal_id TEXT,
                duration_seconds INTEGER NOT NULL DEFAULT 0,
                transcript_summary TEXT,
                created_at TEXT NOT NULL
        );
        """)

        cursor.execute("ALTER TABLE student_profile ADD COLUMN IF NOT EXISTS user_id INTEGER UNIQUE REFERENCES app_users(id);")
        for table_name in ("study_materials", "quiz_sessions", "weak_areas", "strong_areas", "subject_progress"):
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS student_id INTEGER NOT NULL DEFAULT 1;"
            )
        scoped_keys = (
            ("weak_areas", "weak_areas_topic_key", "weak_areas_student_topic_key", "student_id, topic"),
            ("strong_areas", "strong_areas_topic_key", "strong_areas_student_topic_key", "student_id, topic"),
            (
                "subject_progress",
                "subject_progress_subject_name_key",
                "subject_progress_student_subject_key",
                "student_id, subject_name",
            ),
        )
        for table_name, legacy_key, scoped_key, columns in scoped_keys:
            cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {legacy_key};")
            cursor.execute(
                "SELECT 1 FROM pg_constraint WHERE conrelid = to_regclass(?) AND conname = ?;",
                (table_name, scoped_key),
            )
            if cursor.fetchone() is None:
                cursor.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {scoped_key} UNIQUE ({columns});")

        owned_tables = (
            "study_materials",
            "quiz_sessions",
            "weak_areas",
            "strong_areas",
            "subject_progress",
            "student_goals",
            "study_plans",
            "daily_study_tasks",
            "revision_schedule",
            "voice_sessions",
        )
        for table_name in owned_tables:
            constraint_name = f"{table_name}_student_profile_fk"
            cursor.execute(
                "SELECT 1 FROM pg_constraint WHERE conrelid = to_regclass(?) AND conname = ?;",
                (table_name, constraint_name),
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} "
                    "FOREIGN KEY (student_id) REFERENCES student_profile(id) ON DELETE CASCADE NOT VALID;"
                )

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

def create_user_account(email: str, password_hash: str) -> Dict[str, Any]:
    """Create an account and its private student profile in one transaction."""
    normalized_email = email.strip().lower()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO app_users (email, password_hash, created_at) VALUES (?, ?, ?) RETURNING id;",
            (normalized_email, password_hash, datetime.now().isoformat()),
        )
        user_id = cursor.fetchone()["id"]
        cursor.execute(
            """
            INSERT INTO student_profile (
                user_id, name, email, level, language, current_subject, current_topic,
                mastery_score, study_streak_days, last_active_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id;
            """,
            (
                user_id, "", normalized_email, "", "", "", "",
                0.0, 0, date.today().isoformat(),
            ),
        )
        profile_id = cursor.fetchone()["id"]
        conn.commit()
    return {"id": user_id, "student_id": profile_id, "email": normalized_email}


def get_user_account_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Load a user's authentication record and associated profile identifier."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.email, u.password_hash, p.id AS student_id
            FROM app_users u
            JOIN student_profile p ON p.user_id = u.id
            WHERE u.email = ?;
            """,
            (email.strip().lower(),),
        )
        return cursor.fetchone()


def get_user_account(user_id: int) -> Optional[Dict[str, Any]]:
    """Load an authenticated user's public account and profile identifiers."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.email, p.id AS student_id
            FROM app_users u
            JOIN student_profile p ON p.user_id = u.id
            WHERE u.id = ?;
            """,
            (user_id,),
        )
        return cursor.fetchone()


def get_student_profile(student_id: int) -> Dict[str, Any]:
    """Retrieve current student profile with live mastery and streak."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_profile WHERE id = ?;", (student_id,))
        row = cursor.fetchone()
        if not row:
            raise LookupError("Student profile was not found.")
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
    student_id: int = 1,
) -> Dict[str, Any]:
    """Update student learning settings and return updated profile."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if level is not None:
            cursor.execute("UPDATE student_profile SET level = ? WHERE id = ?;", (level, student_id))
        if language is not None:
            cursor.execute("UPDATE student_profile SET language = ? WHERE id = ?;", (language, student_id))
        if current_subject is not None:
            cursor.execute("UPDATE student_profile SET current_subject = ? WHERE id = ?;", (current_subject, student_id))
        if current_topic is not None:
            cursor.execute("UPDATE student_profile SET current_topic = ? WHERE id = ?;", (current_topic, student_id))
        if name is not None:
            cursor.execute("UPDATE student_profile SET name = ? WHERE id = ?;", (name, student_id))
        if education_level is not None:
            cursor.execute("UPDATE student_profile SET education_level = ? WHERE id = ?;", (education_level, student_id))
        if institution is not None:
            cursor.execute("UPDATE student_profile SET institution = ? WHERE id = ?;", (institution, student_id))
        if stream_branch is not None:
            cursor.execute("UPDATE student_profile SET stream_branch = ? WHERE id = ?;", (stream_branch, student_id))
        if academic_year_semester is not None:
            cursor.execute("UPDATE student_profile SET academic_year_semester = ? WHERE id = ?;", (academic_year_semester, student_id))
        if daily_study_hours is not None:
            cursor.execute("UPDATE student_profile SET daily_study_hours = ? WHERE id = ?;", (daily_study_hours, student_id))
        if onboarding_completed is not None:
            cursor.execute("UPDATE student_profile SET onboarding_completed = ? WHERE id = ?;", (onboarding_completed, student_id))
        conn.commit()
    return get_student_profile(student_id)


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
            cursor.execute(
                "UPDATE student_profile SET study_streak_days = study_streak_days + 1 WHERE id = ?;",
                (student_id,),
            )
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

def list_study_materials(student_id: int) -> List[Dict[str, Any]]:
    """List all registered PDF study materials."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_materials WHERE student_id = ? ORDER BY upload_date DESC;", (student_id,))
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
    student_id: int = 1,
) -> Dict[str, Any]:
    """Save a newly uploaded study material metadata record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        upload_date = date.today().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO study_materials (
                id, student_id, name, subject, upload_date, size_str, pages, chunks, status,
                education_level, curriculum, goal_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (doc_id, student_id, name, subject, upload_date, size_str, pages, chunks, status, education_level, curriculum, goal_id))
        conn.commit()
    return {
        "id": doc_id,
        "student_id": student_id,
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


def delete_study_material(doc_id: str, student_id: int) -> bool:
    """Delete a study material record by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM study_materials WHERE id = ? AND student_id = ?;", (doc_id, student_id))
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
