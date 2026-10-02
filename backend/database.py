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
            ("education_level", "TEXT NOT NULL DEFAULT 'Telangana State Board SSC (Class 10)'"),
            ("institution", "TEXT NOT NULL DEFAULT 'Telangana State Model School'"),
            ("stream_branch", "TEXT NOT NULL DEFAULT 'TG SSC (English & Telugu Medium)'"),
            ("academic_year_semester", "TEXT NOT NULL DEFAULT 'Class 10th SSC (2026-2027)'"),
            ("daily_study_hours", "REAL NOT NULL DEFAULT 3.0"),
            ("onboarding_completed", "INTEGER NOT NULL DEFAULT 1"),
            ("active_goal_id", "TEXT NOT NULL DEFAULT 'tg-goal-ssc-gpa'"),
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
                    1, 'Druva', 'druva@edumate.ai', 'Beginner', 'English',
                    'Mathematics', 'Real Numbers: Logarithms & Euclid Division Lemma', 0.0, 0, ?,
                    'Telangana State Board SSC (Class 10)', 'Telangana State Model School', 'TG SSC (English Medium)', 'Class 10th SSC (2026-2027)',
                    3.0, 1, 'tg-goal-ssc-gpa'
                );
            """, (date.today().isoformat(),))

        # Check if TG SSC specific data needs to be populated
        cursor.execute("SELECT COUNT(*) AS cnt FROM student_goals WHERE id = 'tg-goal-ssc-gpa';")
        if cursor.fetchone()["cnt"] == 0:
            seed_tg_ssc_data(conn)

        conn.commit()


def seed_tg_ssc_data(conn) -> None:
    """Seed comprehensive, authentic Telangana State Board SSC (TG SSC) subjects, goals, and resources."""
    cursor = conn.cursor()
    today_str = date.today().isoformat()

    # 1. Update Profile to TG SSC
    cursor.execute("""
        UPDATE student_profile
        SET education_level = 'Telangana State Board SSC (Class 10)',
            institution = 'Telangana State Model School / Zilla Parishad High School',
            stream_branch = 'TG SSC (English Medium)',
            academic_year_semester = 'Class 10th SSC (2026-2027)',
            current_subject = 'Mathematics',
            current_topic = 'Real Numbers: Logarithms & Euclid Division Lemma',
            daily_study_hours = 3.0,
            active_goal_id = 'tg-goal-ssc-gpa'
        WHERE id = 1;
    """)

    # 2. Re-seed Authentic Student Goals for TG SSC
    cursor.execute("DELETE FROM student_goals;")
    tg_goals = [
        ('tg-goal-ssc-gpa', 1, 'TG SSC 10/10 GPA (Board Exam 2027)', 'academic', 'Telangana SSC Public Examinations (March 2027)', '2027-03-15', 'HIGH', 3.0, 'Beginner', 'Advanced', 1, today_str),
        ('tg-goal-polycet', 1, 'TS POLYCET 2027 (State Rank < 1000)', 'exam', 'Telangana Polytechnic Common Entrance Test (May 2027)', '2027-05-18', 'HIGH', 2.5, 'Beginner', 'Advanced', 0, today_str),
        ('tg-goal-tsrjc', 1, 'TSRJC CET 2027 (Residential Junior Colleges)', 'exam', 'Telangana Residential Junior College Common Entrance (April 2027)', '2027-04-22', 'MEDIUM', 2.0, 'Beginner', 'Advanced', 0, today_str),
        ('tg-goal-nmms', 1, 'TG NMMS / Talent Scholarship', 'exam', 'National Means-cum-Merit Scholarship (November 2026)', '2026-11-20', 'MEDIUM', 1.5, 'Beginner', 'Advanced', 0, today_str),
    ]
    cursor.executemany("""
        INSERT INTO student_goals (
            id, student_id, name, goal_type, target_exam, target_date,
            priority, available_hours_per_day, current_level, target_level, is_active, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, tg_goals)

    # 3. Seed Authentic TG SSC Study Materials & Resources
    cursor.execute("DELETE FROM study_materials;")
    tg_materials = [
        ('doc-tg-maths-formulae', 'TG_SSC_Class10_Maths_Formulae_and_Theorems.pdf', 'Mathematics', today_str, '1.6 MB', 16, 36, 'Ready', 'TG SSC', 'Telangana SCERT', 'tg-goal-ssc-gpa'),
        ('doc-tg-physics-notes', 'TG_SSC_Physical_Sciences_Quick_Revision_Notes.pdf', 'Physical Sciences', today_str, '2.2 MB', 22, 50, 'Ready', 'TG SSC', 'Telangana SCERT', 'tg-goal-ssc-gpa'),
        ('doc-tg-bio-concepts', 'TG_SSC_Biological_Science_Key_Diagrams_and_Concepts.pdf', 'Biological Science', today_str, '1.9 MB', 18, 42, 'Ready', 'TG SSC', 'Telangana SCERT', 'tg-goal-ssc-gpa'),
        ('doc-tg-social-movement', 'TG_SSC_Social_Studies_Telangana_Movement_Special_Guide.pdf', 'Social Studies', today_str, '2.5 MB', 24, 55, 'Ready', 'TG SSC', 'Telangana SCERT', 'tg-goal-ssc-gpa'),
        ('doc-tg-polycet-shortcuts', 'TS_POLYCET_Mathematics_and_Physics_Speed_Shortcuts.pdf', 'Mathematics & Physical Sciences', today_str, '2.0 MB', 20, 45, 'Ready', 'TG SSC', 'SBTET Telangana', 'tg-goal-polycet'),
        ('doc-tg-english-discourses', 'TG_SSC_English_Discourses_and_Grammar_Handbook.pdf', 'Third Language: English', today_str, '1.5 MB', 16, 38, 'Ready', 'TG SSC', 'Telangana SCERT', 'tg-goal-ssc-gpa'),
        ('doc-tg-telugu-vyakaranam', 'TG_SSC_Telugu_Vyakaranam_and_Sahityam_Guide.pdf', 'First Language: Telugu', today_str, '2.1 MB', 20, 45, 'Ready', 'TG SSC', 'Telangana SCERT', 'tg-goal-ssc-gpa'),
    ]
    cursor.executemany("""
        INSERT INTO study_materials (
            id, name, subject, upload_date, size_str, pages, chunks, status, education_level, curriculum, goal_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, tg_materials)

    # 4. Seed Live Subject Progress for TG SSC (6 Papers)
    cursor.execute("DELETE FROM subject_progress;")
    subject_progress_data = [
        ('Mathematics', 72, 10, 14, 'In Progress'),
        ('Physical Sciences', 65, 8, 12, 'In Progress'),
        ('Biological Science', 70, 7, 10, 'In Progress'),
        ('Social Studies', 60, 13, 22, 'In Progress'),
        ('Third Language: English', 78, 6, 8, 'In Progress'),
        ('First Language: Telugu', 80, 8, 10, 'In Progress'),
    ]
    cursor.executemany("""
        INSERT INTO subject_progress (subject_name, progress, topics_completed, total_topics, status)
        VALUES (?, ?, ?, ?, ?);
    """, subject_progress_data)

    # 5. Seed Authentic TG SSC Spaced Revision Items
    cursor.execute("DELETE FROM revision_schedule;")
    revision_items = [
        (1, 'Mathematics', 'Real Numbers: Logarithms & Laws of Logarithms (log xy = log x + log y)', today_str, 1, today_str, today_str, 70.0, 1, 'DUE'),
        (1, 'Physical Sciences', 'Structure of Atom: Quantum Numbers (n, l, m_l, m_s) & Aufbau Rule', today_str, 2, today_str, today_str, 62.0, 2, 'DUE'),
        (1, 'Physical Sciences', 'Refraction at Curved Surfaces: Lens Maker Formula 1/f = (n-1)(1/R1 - 1/R2)', today_str, 3, today_str, today_str, 55.0, 2, 'DUE'),
        (1, 'Biological Science', 'Excretion: Structure of Nephron & Mechanism of Urine Formation', today_str, 2, today_str, today_str, 75.0, 1, 'PENDING'),
        (1, 'Social Studies', 'Telangana Movement: 1969 Agitation & Gentlemen Agreement 1956', today_str, 4, today_str, today_str, 85.0, 0, 'PENDING'),
    ]
    cursor.executemany("""
        INSERT INTO revision_schedule (
            student_id, subject, topic, learned_date, interval_days,
            next_revision_date, last_reviewed_date, mastery_score, mistake_count, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, revision_items)

    # 6. Seed Daily Tasks tailored to TG SSC 10/10 GPA
    cursor.execute("DELETE FROM daily_study_tasks WHERE date_scheduled = ?;", (today_str,))
    daily_tasks = [
        ('task-tg-1', 'tg-goal-ssc-gpa', 1, 'PRACTICE', 'Solve TG SSC Logarithms & Euclid Lemma Exercises (Ex 1.1 & 1.5)', 'Mathematics', 'Real Numbers', 40, 0, 'HIGH', 'High-weightage 4-mark question in SSC board exam.', today_str),
        ('task-tg-2', 'tg-goal-ssc-gpa', 1, 'REVISE', 'Revise Lens Maker Formula & Ray Diagrams for Concave Mirror', 'Physical Sciences', 'Optics & Curved Surfaces', 30, 0, 'HIGH', 'Core numerical and ray diagram in Physical Sciences.', today_str),
        ('task-tg-3', 'tg-goal-ssc-gpa', 1, 'LEARN', 'Draw & Label Internal Structure of Heart & Blood Clotting Mechanism', 'Biological Science', 'Transportation', 30, 0, 'NORMAL', 'Frequent 4-mark diagram question in Paper 2.', today_str),
        ('task-tg-4', 'tg-goal-ssc-gpa', 1, 'QUIZ', 'Telangana Movement 1969 & State Formation Rapid Revision Quiz', 'Social Studies', 'Telangana Movement & State Formation', 20, 0, 'NORMAL', 'Essential section in Social Studies Part II.', today_str),
    ]
    cursor.executemany("""
        INSERT INTO daily_study_tasks (
            id, plan_id, student_id, task_type, title, subject, topic,
            estimated_minutes, is_completed, priority, reason, date_scheduled
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, daily_tasks)

    # 7. Seed TG SSC Weak and Strong Areas
    cursor.execute("DELETE FROM weak_areas;")
    cursor.execute("DELETE FROM strong_areas;")
    weak_areas = [
        ('Lens Maker Formula & Sign Conventions', 'Physical Sciences', 3, today_str, 0),
        ('Logarithm Laws Application & Expansions', 'Mathematics', 2, today_str, 0),
        ('Quantum Numbers & Aufbau Configuration', 'Physical Sciences', 2, today_str, 0),
    ]
    cursor.executemany("""
        INSERT INTO weak_areas (topic, subject, mistake_count, last_mistake_date, is_mastered)
        VALUES (?, ?, ?, ?, ?);
    """, weak_areas)

    strong_areas = [
        ('Sets: Venn Diagrams & Set Difference (A-B)', 'Mathematics', 7),
        ('Nutrition: Human Digestive System & Enzymes', 'Biological Science', 6),
        ('Telangana Movement: State Formation June 2, 2014', 'Social Studies', 5),
    ]
    cursor.executemany("""
        INSERT INTO strong_areas (topic, subject, success_count)
        VALUES (?, ?, ?);
    """, strong_areas)

    conn.commit()


def select_active_goal(goal_id: str, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Select the specified goal as active and dynamically reconfigure daily tasks and focus."""
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
        today_str = date.today().isoformat()

        # Regenerate daily study tasks tailored to the selected goal
        cursor.execute("DELETE FROM daily_study_tasks WHERE student_id = ? AND date_scheduled = ?;", (student_id, today_str))

        if "POLYCET" in goal_data["name"]:
            cursor.execute("UPDATE student_profile SET current_subject = 'Mathematics', current_topic = 'POLYCET Sets & Quadratic Equations Speed Drill' WHERE id = ?;", (student_id,))
            tasks = [
                ('task-poly-1', goal_id, student_id, 'PRACTICE', 'POLYCET MCQ Speed Drill: Sets & Quadratic Equations', 'Mathematics', 'Sets & Progressions', 40, 0, 'HIGH', '60 marks high-speed section in POLYCET.', today_str),
                ('task-poly-2', goal_id, student_id, 'REVISE', 'Physics Numerical: Lens Maker Formula & Electric Circuits', 'Physical Sciences', 'Optics & Electricity', 35, 0, 'HIGH', '30 marks physics section in POLYCET.', today_str),
                ('task-poly-3', goal_id, student_id, 'QUIZ', 'Chemistry MCQ Speed Test: Atomic Structure & Quantum Numbers', 'Physical Sciences', 'Atomic Structure & Bonding', 25, 0, 'NORMAL', '30 marks chemistry section in POLYCET.', today_str),
                ('task-poly-4', goal_id, student_id, 'REVIEW_MISTAKES', 'Review POLYCET Shortcut Formulas & Trigonometry Elimination', 'Mathematics', 'Formula Shortcuts', 20, 0, 'NORMAL', 'Target sub-45-second solve time per question.', today_str),
            ]
        elif "TSRJC" in goal_data["name"]:
            cursor.execute("UPDATE student_profile SET current_subject = 'Physical Sciences', current_topic = 'Kirchhoff Laws & Electric Current Circuits' WHERE id = ?;", (student_id,))
            tasks = [
                ('task-tsrjc-1', goal_id, student_id, 'PRACTICE', 'TSRJC Entrance Maths: Similar Triangles & Pythagoras Problems', 'Mathematics', 'Similar Triangles', 40, 0, 'HIGH', 'TSRJC MPC merit rank key section.', today_str),
                ('task-tsrjc-2', goal_id, student_id, 'REVISE', 'Kirchhoff Junction & Loop Laws Application Drill', 'Physical Sciences', 'Electric Current', 35, 0, 'HIGH', 'Frequent TSRJC physical science question.', today_str),
                ('task-tsrjc-3', goal_id, student_id, 'LEARN', 'Biological Science: Nephron Mechanism & Glomerular Filtration', 'Biological Science', 'Excretion', 30, 0, 'NORMAL', 'Key chapter for BiPC stream selection.', today_str),
                ('task-tsrjc-4', goal_id, student_id, 'QUIZ', 'English Grammar & Vocabulary: Attitude is Altitude Reading Comprehension', 'Third Language: English', 'Reading Comprehension', 15, 0, 'NORMAL', 'General English qualifying section.', today_str),
            ]
        elif "NMMS" in goal_data["name"]:
            cursor.execute("UPDATE student_profile SET current_subject = 'Mental Ability (MAT)', current_topic = 'Number Series & Venn Diagrams' WHERE id = ?;", (student_id,))
            tasks = [
                ('task-nmms-1', goal_id, student_id, 'PRACTICE', 'Mental Ability Test (MAT): Number Series & Analogy Puzzles', 'Mental Ability', 'Number Series', 40, 0, 'HIGH', '90 marks MAT high-priority section.', today_str),
                ('task-nmms-2', goal_id, student_id, 'REVISE', 'SAT Science: Basic Motion, Heat & Plant Reproduction Review', 'Physical Sciences', 'SAT Science', 35, 0, 'HIGH', 'Scholastic Aptitude Science section.', today_str),
                ('task-nmms-3', goal_id, student_id, 'QUIZ', 'NMMS Social Studies: Relief Features & Early Civilizations Quiz', 'Social Studies', 'SAT Social', 25, 0, 'NORMAL', 'Scholastic Aptitude Social section.', today_str),
            ]
        else: # TG SSC 10/10 GPA (Default)
            cursor.execute("UPDATE student_profile SET current_subject = 'Mathematics', current_topic = 'Real Numbers: Logarithms & Euclid Division Lemma' WHERE id = ?;", (student_id,))
            tasks = [
                ('task-tg-1', goal_id, student_id, 'PRACTICE', 'Solve TG SSC Logarithms & Euclid Lemma Exercises (Ex 1.1 & 1.5)', 'Mathematics', 'Real Numbers', 40, 0, 'HIGH', 'High-weightage 4-mark question in SSC board exam.', today_str),
                ('task-tg-2', goal_id, student_id, 'REVISE', 'Revise Lens Maker Formula & Ray Diagrams for Concave Mirror', 'Physical Sciences', 'Optics & Curved Surfaces', 30, 0, 'HIGH', 'Core numerical and ray diagram in Physical Sciences.', today_str),
                ('task-tg-3', goal_id, student_id, 'LEARN', 'Draw & Label Internal Structure of Heart & Blood Clotting Mechanism', 'Biological Science', 'Transportation', 30, 0, 'NORMAL', 'Frequent 4-mark diagram question in Paper 2.', today_str),
                ('task-tg-4', goal_id, student_id, 'QUIZ', 'Telangana Movement 1969 & State Formation Rapid Revision Quiz', 'Social Studies', 'Telangana Movement & State Formation', 20, 0, 'NORMAL', 'Essential section in Social Studies Part II.', today_str),
            ]

        cursor.executemany("""
            INSERT INTO daily_study_tasks (
                id, plan_id, student_id, task_type, title, subject, topic,
                estimated_minutes, is_completed, priority, reason, date_scheduled
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, tasks)

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
    """Clear all dynamic session and study data and re-seed clean TG SSC Class 10 baseline."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quiz_sessions;")
        cursor.execute("DELETE FROM voice_sessions;")
        seed_tg_ssc_data(conn)


# Call init_db on module import
init_db()

