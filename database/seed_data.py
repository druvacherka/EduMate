"""MongoDB Seed Data and Initializer for EduMate.

Seeds authentic Telangana State Board SSC (TG SSC Class 10) curriculum,
goals, study materials, tasks, and analytics into MongoDB collections.
"""

from datetime import date
from typing import Any, Dict
from database.connection import get_db


def seed_tg_ssc_mongodb() -> None:
    """Populate MongoDB collections with authentic TG SSC Class 10 baseline data."""
    db = get_db()
    today_str = date.today().isoformat()

    # 1. Student Profile Collection
    profile_data = {
        "id": 1,
        "student_id": 1,
        "name": "Druva",
        "email": "druva@edumate.ai",
        "level": "Beginner",
        "language": "English",
        "current_subject": "Mathematics",
        "current_topic": "Real Numbers: Logarithms & Euclid Division Lemma",
        "mastery_score": 72.0,
        "study_streak_days": 3,
        "last_active_date": today_str,
        "education_level": "Telangana State Board SSC (Class 10)",
        "institution": "Telangana State Model School / Zilla Parishad High School",
        "stream_branch": "TG SSC (English Medium)",
        "academic_year_semester": "Class 10th SSC (2026-2027)",
        "daily_study_hours": 3.0,
        "onboarding_completed": True,
        "active_goal_id": "tg-goal-ssc-gpa",
    }
    db.student_profile.update_one(
        {"$or": [{"id": 1}, {"student_id": 1}, {"_id": 1}]},
        {"$set": profile_data},
        upsert=True,
    )

    # 2. Student Goals Collection
    tg_goals = [
        {
            "id": "tg-goal-ssc-gpa",
            "student_id": 1,
            "name": "TG SSC 10/10 GPA (Board Exam 2027)",
            "goal_type": "academic",
            "target_exam": "Telangana SSC Public Examinations (March 2027)",
            "target_date": "2027-03-15",
            "priority": "HIGH",
            "available_hours_per_day": 3.0,
            "current_level": "Beginner",
            "target_level": "Advanced",
            "is_active": True,
            "created_at": today_str,
        },
        {
            "id": "tg-goal-polycet",
            "student_id": 1,
            "name": "TS POLYCET 2027 (State Rank < 1000)",
            "goal_type": "exam",
            "target_exam": "Telangana Polytechnic Common Entrance Test (May 2027)",
            "target_date": "2027-05-18",
            "priority": "HIGH",
            "available_hours_per_day": 2.5,
            "current_level": "Beginner",
            "target_level": "Advanced",
            "is_active": False,
            "created_at": today_str,
        },
        {
            "id": "tg-goal-tsrjc",
            "student_id": 1,
            "name": "TSRJC CET 2027 (Residential Junior Colleges)",
            "goal_type": "exam",
            "target_exam": "Telangana Residential Junior College Common Entrance (April 2027)",
            "target_date": "2027-04-22",
            "priority": "MEDIUM",
            "available_hours_per_day": 2.0,
            "current_level": "Beginner",
            "target_level": "Advanced",
            "is_active": False,
            "created_at": today_str,
        },
        {
            "id": "tg-goal-nmms",
            "student_id": 1,
            "name": "TG NMMS / Talent Scholarship",
            "goal_type": "exam",
            "target_exam": "National Means-cum-Merit Scholarship (November 2026)",
            "target_date": "2026-11-20",
            "priority": "MEDIUM",
            "available_hours_per_day": 1.5,
            "current_level": "Beginner",
            "target_level": "Advanced",
            "is_active": False,
            "created_at": today_str,
        },
    ]
    for g in tg_goals:
        db.student_goals.update_one({"id": g["id"]}, {"$set": g}, upsert=True)

    # 3. Study Materials Collection
    tg_materials = [
        {
            "id": "doc-tg-maths-formulae",
            "name": "TG_SSC_Class10_Maths_Formulae_and_Theorems.pdf",
            "subject": "Mathematics",
            "upload_date": today_str,
            "size_str": "1.6 MB",
            "pages": 16,
            "chunks": 36,
            "status": "Ready",
            "education_level": "TG SSC",
            "curriculum": "Telangana SCERT",
            "goal_id": "tg-goal-ssc-gpa",
        },
        {
            "id": "doc-tg-physics-notes",
            "name": "TG_SSC_Physical_Sciences_Quick_Revision_Notes.pdf",
            "subject": "Physical Sciences",
            "upload_date": today_str,
            "size_str": "2.2 MB",
            "pages": 22,
            "chunks": 50,
            "status": "Ready",
            "education_level": "TG SSC",
            "curriculum": "Telangana SCERT",
            "goal_id": "tg-goal-ssc-gpa",
        },
        {
            "id": "doc-tg-bio-concepts",
            "name": "TG_SSC_Biological_Science_Key_Diagrams_and_Concepts.pdf",
            "subject": "Biological Science",
            "upload_date": today_str,
            "size_str": "1.9 MB",
            "pages": 18,
            "chunks": 42,
            "status": "Ready",
            "education_level": "TG SSC",
            "curriculum": "Telangana SCERT",
            "goal_id": "tg-goal-ssc-gpa",
        },
        {
            "id": "doc-tg-social-movement",
            "name": "TG_SSC_Social_Studies_Telangana_Movement_Special_Guide.pdf",
            "subject": "Social Studies",
            "upload_date": today_str,
            "size_str": "2.5 MB",
            "pages": 24,
            "chunks": 55,
            "status": "Ready",
            "education_level": "TG SSC",
            "curriculum": "Telangana SCERT",
            "goal_id": "tg-goal-ssc-gpa",
        },
        {
            "id": "doc-tg-polycet-shortcuts",
            "name": "TS_POLYCET_Mathematics_and_Physics_Speed_Shortcuts.pdf",
            "subject": "Mathematics & Physical Sciences",
            "upload_date": today_str,
            "size_str": "2.0 MB",
            "pages": 20,
            "chunks": 45,
            "status": "Ready",
            "education_level": "TG SSC",
            "curriculum": "SBTET Telangana",
            "goal_id": "tg-goal-polycet",
        },
        {
            "id": "doc-tg-english-discourses",
            "name": "TG_SSC_English_Discourses_and_Grammar_Handbook.pdf",
            "subject": "Third Language: English",
            "upload_date": today_str,
            "size_str": "1.5 MB",
            "pages": 16,
            "chunks": 38,
            "status": "Ready",
            "education_level": "TG SSC",
            "curriculum": "Telangana SCERT",
            "goal_id": "tg-goal-ssc-gpa",
        },
        {
            "id": "doc-tg-telugu-vyakaranam",
            "name": "TG_SSC_Telugu_Vyakaranam_and_Sahityam_Guide.pdf",
            "subject": "First Language: Telugu",
            "upload_date": today_str,
            "size_str": "2.1 MB",
            "pages": 20,
            "chunks": 45,
            "status": "Ready",
            "education_level": "TG SSC",
            "curriculum": "Telangana SCERT",
            "goal_id": "tg-goal-ssc-gpa",
        },
    ]
    for m in tg_materials:
        db.study_materials.update_one({"id": m["id"]}, {"$set": m}, upsert=True)

    # 4. Subject Progress Collection
    progress_records = [
        {"subject_name": "Mathematics", "progress": 72, "topics_completed": 10, "total_topics": 14, "status": "In Progress"},
        {"subject_name": "Physical Sciences", "progress": 65, "topics_completed": 8, "total_topics": 12, "status": "In Progress"},
        {"subject_name": "Biological Science", "progress": 70, "topics_completed": 7, "total_topics": 10, "status": "In Progress"},
        {"subject_name": "Social Studies", "progress": 60, "topics_completed": 13, "total_topics": 22, "status": "In Progress"},
        {"subject_name": "Third Language: English", "progress": 78, "topics_completed": 6, "total_topics": 8, "status": "In Progress"},
        {"subject_name": "First Language: Telugu", "progress": 80, "topics_completed": 8, "total_topics": 10, "status": "In Progress"},
    ]
    for p in progress_records:
        db.subject_progress.update_one({"subject_name": p["subject_name"]}, {"$set": p}, upsert=True)

    # 5. Spaced Revision Schedule Collection
    revision_items = [
        {"id": "rev-1", "student_id": 1, "subject": "Mathematics", "topic": "Real Numbers: Logarithms & Laws of Logarithms (log xy = log x + log y)", "learned_date": today_str, "interval_days": 1, "next_revision_date": today_str, "last_reviewed_date": today_str, "mastery_score": 70.0, "mistake_count": 1, "status": "DUE"},
        {"id": "rev-2", "student_id": 1, "subject": "Physical Sciences", "topic": "Structure of Atom: Quantum Numbers (n, l, m_l, m_s) & Aufbau Rule", "learned_date": today_str, "interval_days": 2, "next_revision_date": today_str, "last_reviewed_date": today_str, "mastery_score": 62.0, "mistake_count": 2, "status": "DUE"},
        {"id": "rev-3", "student_id": 1, "subject": "Physical Sciences", "topic": "Refraction at Curved Surfaces: Lens Maker Formula 1/f = (n-1)(1/R1 - 1/R2)", "learned_date": today_str, "interval_days": 3, "next_revision_date": today_str, "last_reviewed_date": today_str, "mastery_score": 55.0, "mistake_count": 2, "status": "DUE"},
        {"id": "rev-4", "student_id": 1, "subject": "Biological Science", "topic": "Excretion: Structure of Nephron & Mechanism of Urine Formation", "learned_date": today_str, "interval_days": 2, "next_revision_date": today_str, "last_reviewed_date": today_str, "mastery_score": 75.0, "mistake_count": 1, "status": "PENDING"},
        {"id": "rev-5", "student_id": 1, "subject": "Social Studies", "topic": "Telangana Movement: 1969 Agitation & Gentlemen Agreement 1956", "learned_date": today_str, "interval_days": 4, "next_revision_date": today_str, "last_reviewed_date": today_str, "mastery_score": 85.0, "mistake_count": 0, "status": "PENDING"},
    ]
    for r in revision_items:
        db.revision_schedule.update_one({"id": r["id"]}, {"$set": r}, upsert=True)

    # 6. Daily Tasks Collection
    daily_tasks = [
        {"id": "task-tg-1", "plan_id": "tg-goal-ssc-gpa", "student_id": 1, "task_type": "PRACTICE", "title": "Solve TG SSC Logarithms & Euclid Lemma Exercises (Ex 1.1 & 1.5)", "subject": "Mathematics", "topic": "Real Numbers", "estimated_minutes": 40, "is_completed": False, "priority": "HIGH", "reason": "High-weightage 4-mark question in SSC board exam.", "date_scheduled": today_str},
        {"id": "task-tg-2", "plan_id": "tg-goal-ssc-gpa", "student_id": 1, "task_type": "REVISE", "title": "Revise Lens Maker Formula & Ray Diagrams for Concave Mirror", "subject": "Physical Sciences", "topic": "Optics & Curved Surfaces", "estimated_minutes": 30, "is_completed": False, "priority": "HIGH", "reason": "Core numerical and ray diagram in Physical Sciences.", "date_scheduled": today_str},
        {"id": "task-tg-3", "plan_id": "tg-goal-ssc-gpa", "student_id": 1, "task_type": "LEARN", "title": "Draw & Label Internal Structure of Heart & Blood Clotting Mechanism", "subject": "Biological Science", "topic": "Transportation", "estimated_minutes": 30, "is_completed": False, "priority": "NORMAL", "reason": "Frequent 4-mark diagram question in Paper 2.", "date_scheduled": today_str},
        {"id": "task-tg-4", "plan_id": "tg-goal-ssc-gpa", "student_id": 1, "task_type": "QUIZ", "title": "Telangana Movement 1969 & State Formation Rapid Revision Quiz", "subject": "Social Studies", "topic": "Telangana Movement & State Formation", "estimated_minutes": 20, "is_completed": False, "priority": "NORMAL", "reason": "Essential section in Social Studies Part II.", "date_scheduled": today_str},
    ]
    for t in daily_tasks:
        db.daily_study_tasks.update_one({"id": t["id"]}, {"$set": t}, upsert=True)

    # 7. Weak Areas Collection
    weak_areas = [
        {"topic": "Lens Maker Formula & Sign Conventions", "subject": "Physical Sciences", "mistake_count": 3, "last_mistake_date": today_str, "is_mastered": False},
        {"topic": "Logarithm Laws Application & Expansions", "subject": "Mathematics", "mistake_count": 2, "last_mistake_date": today_str, "is_mastered": False},
        {"topic": "Quantum Numbers & Aufbau Configuration", "subject": "Physical Sciences", "mistake_count": 2, "last_mistake_date": today_str, "is_mastered": False},
    ]
    for w in weak_areas:
        db.weak_areas.update_one({"topic": w["topic"]}, {"$set": w}, upsert=True)

    # 8. Strong Areas Collection
    strong_areas = [
        {"topic": "Sets: Venn Diagrams & Set Difference (A-B)", "subject": "Mathematics", "success_count": 7},
        {"topic": "Nutrition: Human Digestive System & Enzymes", "subject": "Biological Science", "success_count": 6},
        {"topic": "Telangana Movement: State Formation June 2, 2014", "subject": "Social Studies", "success_count": 5},
    ]
    for s in strong_areas:
        db.strong_areas.update_one({"topic": s["topic"]}, {"$set": s}, upsert=True)


def seed_database_if_empty() -> None:
    """Seed MongoDB only if the student_profile collection is empty."""
    db = get_db()
    try:
        count = db.student_profile.count_documents({})
        if count == 0:
            seed_tg_ssc_mongodb()
    except Exception:
        seed_tg_ssc_mongodb()


def reset_database_to_baseline() -> None:
    """Clear session data and re-seed clean TG SSC baseline in MongoDB."""
    db = get_db()
    db.quiz_sessions.delete_many({})
    db.voice_sessions.delete_many({})
    seed_tg_ssc_mongodb()
