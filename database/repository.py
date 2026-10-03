"""MongoDB Repository Layer for EduMate.

Implements all CRUD and business query operations for student profiles,
goals, study materials, quizzes, analytics, tasks, and revisions.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from database.connection import get_db
from database.seed_data import seed_database_if_empty, seed_tg_ssc_mongodb


def _clean_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Clean MongoDB document by stripping ObjectId _id to ensure Pydantic JSON serializability."""
    if not doc:
        return None
    d = dict(doc)
    if "_id" in d:
        if "id" not in d:
            d["id"] = str(d["_id"])
        del d["_id"]
    return d


def _clean_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean list of MongoDB documents."""
    return [_clean_doc(d) for d in docs if d is not None]


# ==========================================
# Student Profile Operations
# ==========================================

def get_student_profile(student_id: int = 1) -> Dict[str, Any]:
    """Retrieve current student profile from MongoDB."""
    db = get_db()
    profile = db.student_profile.find_one({"$or": [{"id": student_id}, {"student_id": student_id}, {"_id": student_id}]})
    if not profile:
        seed_database_if_empty()
        profile = db.student_profile.find_one({"$or": [{"id": student_id}, {"student_id": student_id}, {"_id": student_id}]})
    if not profile:
        profile = {"id": student_id, "name": "Druva", "level": "Beginner"}
    
    clean = _clean_doc(profile)
    clean["id"] = clean.get("student_id", student_id)
    return clean


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
    """Update student profile fields in MongoDB."""
    db = get_db()
    updates: Dict[str, Any] = {}
    if level is not None:
        updates["level"] = level
    if language is not None:
        updates["language"] = language
    if current_subject is not None:
        updates["current_subject"] = current_subject
    if current_topic is not None:
        updates["current_topic"] = current_topic
    if name is not None:
        updates["name"] = name
    if education_level is not None:
        updates["education_level"] = education_level
    if institution is not None:
        updates["institution"] = institution
    if stream_branch is not None:
        updates["stream_branch"] = stream_branch
    if academic_year_semester is not None:
        updates["academic_year_semester"] = academic_year_semester
    if daily_study_hours is not None:
        updates["daily_study_hours"] = float(daily_study_hours)
    if onboarding_completed is not None:
        updates["onboarding_completed"] = bool(onboarding_completed)

    if updates:
        db.student_profile.update_one(
            {"$or": [{"id": student_id}, {"student_id": student_id}, {"_id": student_id}]},
            {"$set": updates},
            upsert=True,
        )
    return get_student_profile(student_id)


# ==========================================
# Student Goals Operations
# ==========================================

def list_student_goals(student_id: int = 1) -> List[Dict[str, Any]]:
    """Fetch all goals for a student ordered by active status and priority."""
    db = get_db()
    raw_goals = list(db.student_goals.find({"student_id": student_id}))
    goals = _clean_docs(raw_goals)
    
    # Priority sorting helper
    priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
    goals.sort(
        key=lambda g: (
            0 if g.get("is_active") else 1,
            priority_order.get(g.get("priority", "NORMAL"), 3),
            g.get("created_at", ""),
        )
    )
    for g in goals:
        g["id"] = str(g.get("id", ""))
    return goals


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
    """Insert or update a student goal in MongoDB."""
    db = get_db()
    today_str = date.today().isoformat()
    doc = {
        "id": goal_id,
        "student_id": student_id,
        "name": name,
        "goal_type": goal_type,
        "target_exam": target_exam,
        "target_date": target_date,
        "priority": priority,
        "available_hours_per_day": float(available_hours_per_day),
        "current_level": current_level,
        "target_level": target_level,
        "is_active": bool(is_active),
        "created_at": today_str,
    }
    db.student_goals.update_one({"id": goal_id}, {"$set": doc}, upsert=True)
    return doc


def delete_student_goal(goal_id: str, student_id: int = 1) -> bool:
    """Delete a student goal by ID."""
    db = get_db()
    res = db.student_goals.delete_one({"id": goal_id, "student_id": student_id})
    return res.deleted_count > 0


def toggle_student_goal(goal_id: str, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Toggle a goal active or inactive."""
    db = get_db()
    goal = db.student_goals.find_one({"id": goal_id, "student_id": student_id})
    if not goal:
        return None
    new_active = not goal.get("is_active", True)
    db.student_goals.update_one(
        {"id": goal_id},
        {"$set": {"is_active": new_active}},
    )
    goal["is_active"] = new_active
    return _clean_doc(goal)


def select_active_goal(goal_id: str, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Select the specified goal as active and dynamically reconfigure daily tasks."""
    db = get_db()
    # Deactivate other goals
    db.student_goals.update_many({"student_id": student_id}, {"$set": {"is_active": False}})
    # Activate selected goal
    res = db.student_goals.find_one_and_update(
        {"id": goal_id, "student_id": student_id},
        {"$set": {"is_active": True}},
        return_document=True,
    )
    if not res:
        return None

    today_str = date.today().isoformat()
    db.student_profile.update_one(
        {"$or": [{"id": student_id}, {"student_id": student_id}, {"_id": student_id}]},
        {"$set": {"active_goal_id": goal_id}}
    )

    # Regenerate daily study tasks tailored to the selected goal
    db.daily_study_tasks.delete_many({"student_id": student_id, "date_scheduled": today_str})

    goal_name = res.get("name", "")
    if "POLYCET" in goal_name:
        db.student_profile.update_one(
            {"$or": [{"id": student_id}, {"student_id": student_id}, {"_id": student_id}]},
            {"$set": {"current_subject": "Mathematics", "current_topic": "POLYCET Sets & Quadratic Equations Speed Drill"}},
        )
        tasks = [
            {"id": "task-poly-1", "plan_id": goal_id, "student_id": student_id, "task_type": "PRACTICE", "title": "POLYCET MCQ Speed Drill: Sets & Quadratic Equations", "subject": "Mathematics", "topic": "Sets & Progressions", "estimated_minutes": 40, "is_completed": False, "priority": "HIGH", "reason": "60 marks high-speed section in POLYCET.", "date_scheduled": today_str},
            {"id": "task-poly-2", "plan_id": goal_id, "student_id": student_id, "task_type": "REVISE", "title": "Physics Numerical: Lens Maker Formula & Electric Circuits", "subject": "Physical Sciences", "topic": "Optics & Electricity", "estimated_minutes": 35, "is_completed": False, "priority": "HIGH", "reason": "30 marks physics section in POLYCET.", "date_scheduled": today_str},
            {"id": "task-poly-3", "plan_id": goal_id, "student_id": student_id, "task_type": "QUIZ", "title": "Chemistry MCQ Speed Test: Atomic Structure & Quantum Numbers", "subject": "Physical Sciences", "topic": "Atomic Structure & Bonding", "estimated_minutes": 25, "is_completed": False, "priority": "NORMAL", "reason": "30 marks chemistry section in POLYCET.", "date_scheduled": today_str},
        ]
    elif "TSRJC" in goal_name:
        db.student_profile.update_one(
            {"$or": [{"id": student_id}, {"student_id": student_id}, {"_id": student_id}]},
            {"$set": {"current_subject": "Physical Sciences", "current_topic": "Kirchhoff Laws & Electric Current Circuits"}},
        )
        tasks = [
            {"id": "task-tsrjc-1", "plan_id": goal_id, "student_id": student_id, "task_type": "PRACTICE", "title": "TSRJC Entrance Maths: Similar Triangles & Pythagoras Problems", "subject": "Mathematics", "topic": "Similar Triangles", "estimated_minutes": 40, "is_completed": False, "priority": "HIGH", "reason": "TSRJC MPC merit rank key section.", "date_scheduled": today_str},
            {"id": "task-tsrjc-2", "plan_id": goal_id, "student_id": student_id, "task_type": "REVISE", "title": "Kirchhoff Junction & Loop Laws Application Drill", "subject": "Physical Sciences", "topic": "Electric Current", "estimated_minutes": 35, "is_completed": False, "priority": "HIGH", "reason": "Frequent TSRJC physical science question.", "date_scheduled": today_str},
            {"id": "task-tsrjc-3", "plan_id": goal_id, "student_id": student_id, "task_type": "LEARN", "title": "Biological Science: Nephron Mechanism & Glomerular Filtration", "subject": "Biological Science", "topic": "Excretion", "estimated_minutes": 30, "is_completed": False, "priority": "NORMAL", "reason": "Key chapter for BiPC stream selection.", "date_scheduled": today_str},
        ]
    else:  # TG SSC 10/10 GPA (Default)
        db.student_profile.update_one(
            {"$or": [{"id": student_id}, {"student_id": student_id}, {"_id": student_id}]},
            {"$set": {"current_subject": "Mathematics", "current_topic": "Real Numbers: Logarithms & Euclid Division Lemma"}},
        )
        tasks = [
            {"id": "task-tg-1", "plan_id": goal_id, "student_id": student_id, "task_type": "PRACTICE", "title": "Solve TG SSC Logarithms & Euclid Lemma Exercises (Ex 1.1 & 1.5)", "subject": "Mathematics", "topic": "Real Numbers", "estimated_minutes": 40, "is_completed": False, "priority": "HIGH", "reason": "High-weightage 4-mark question in SSC board exam.", "date_scheduled": today_str},
            {"id": "task-tg-2", "plan_id": goal_id, "student_id": student_id, "task_type": "REVISE", "title": "Revise Lens Maker Formula & Ray Diagrams for Concave Mirror", "subject": "Physical Sciences", "topic": "Optics & Curved Surfaces", "estimated_minutes": 30, "is_completed": False, "priority": "HIGH", "reason": "Core numerical and ray diagram in Physical Sciences.", "date_scheduled": today_str},
            {"id": "task-tg-3", "plan_id": goal_id, "student_id": student_id, "task_type": "LEARN", "title": "Draw & Label Internal Structure of Heart & Blood Clotting Mechanism", "subject": "Biological Science", "topic": "Transportation", "estimated_minutes": 30, "is_completed": False, "priority": "NORMAL", "reason": "Frequent 4-mark diagram question in Paper 2.", "date_scheduled": today_str},
            {"id": "task-tg-4", "plan_id": goal_id, "student_id": student_id, "task_type": "QUIZ", "title": "Telangana Movement 1969 & State Formation Rapid Revision Quiz", "subject": "Social Studies", "topic": "Telangana Movement & State Formation", "estimated_minutes": 20, "is_completed": False, "priority": "NORMAL", "reason": "Essential section in Social Studies Part II.", "date_scheduled": today_str},
        ]

    for t in tasks:
        db.daily_study_tasks.update_one({"id": t["id"]}, {"$set": t}, upsert=True)

    return _clean_doc(res)


# ==========================================
# Daily Tasks & Planner Operations
# ==========================================

def list_daily_tasks(student_id: int = 1, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch daily study tasks for a given date."""
    db = get_db()
    query_date = target_date or date.today().isoformat()
    raw_tasks = list(db.daily_study_tasks.find({"student_id": student_id, "date_scheduled": query_date}))
    tasks = _clean_docs(raw_tasks)
    
    priority_order = {"HIGH": 1, "NORMAL": 2, "LOW": 3}
    tasks.sort(key=lambda t: (1 if t.get("is_completed") else 0, priority_order.get(t.get("priority", "NORMAL"), 2)))
    return tasks


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
    db = get_db()
    sched_date = date_scheduled or date.today().isoformat()
    doc = {
        "id": task_id,
        "plan_id": plan_id,
        "student_id": student_id,
        "task_type": task_type,
        "title": title,
        "subject": subject,
        "topic": topic,
        "estimated_minutes": estimated_minutes,
        "is_completed": False,
        "priority": priority,
        "reason": reason,
        "date_scheduled": sched_date,
    }
    db.daily_study_tasks.update_one({"id": task_id}, {"$set": doc}, upsert=True)
    return doc


def toggle_daily_task(task_id: str, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Toggle completion status of a daily task."""
    db = get_db()
    task = db.daily_study_tasks.find_one({"id": task_id, "student_id": student_id})
    if not task:
        return None
    new_completed = not task.get("is_completed", False)
    db.daily_study_tasks.update_one(
        {"id": task_id},
        {"$set": {"is_completed": new_completed}},
    )
    if new_completed:
        db.student_profile.update_one(
            {"$or": [{"id": student_id}, {"student_id": student_id}, {"_id": student_id}]},
            {"$inc": {"study_streak_days": 1}},
        )
    
    task["is_completed"] = new_completed
    return _clean_doc(task)


# ==========================================
# Study Materials Operations
# ==========================================

def list_study_materials() -> List[Dict[str, Any]]:
    """List all registered PDF study materials."""
    db = get_db()
    raw_materials = list(db.study_materials.find().sort("upload_date", -1))
    materials = _clean_docs(raw_materials)
    for m in materials:
        m["id"] = str(m.get("id", ""))
        m["uploadDate"] = m.get("upload_date", "")
        m["size"] = m.get("size_str", "1.0 MB")
    return materials


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
    db = get_db()
    upload_date = date.today().isoformat()
    doc = {
        "id": doc_id,
        "name": name,
        "subject": subject,
        "upload_date": upload_date,
        "size_str": size_str,
        "pages": pages,
        "chunks": chunks,
        "status": status,
        "education_level": education_level,
        "curriculum": curriculum,
        "goal_id": goal_id,
    }
    db.study_materials.update_one({"id": doc_id}, {"$set": doc}, upsert=True)
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
    """Delete a study material record and its vector chunks."""
    db = get_db()
    res = db.study_materials.delete_one({"id": doc_id})
    db.study_chunks.delete_many({"document_name": doc_id})
    return res.deleted_count > 0


# ==========================================
# Quiz State Machine Operations
# ==========================================

def create_quiz_session(
    session_id: str,
    topic: str,
    difficulty: str,
    total_questions: int,
    questions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Initialize a new quiz session record in MongoDB."""
    db = get_db()
    doc = {
        "id": session_id,
        "topic": topic,
        "difficulty": difficulty,
        "total_questions": total_questions,
        "score": 0,
        "percentage": 0.0,
        "status": "ACTIVE",
        "questions": questions,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    db.quiz_sessions.update_one({"id": session_id}, {"$set": doc}, upsert=True)
    return doc


def get_quiz_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve quiz session by ID."""
    db = get_db()
    session = db.quiz_sessions.find_one({"id": session_id})
    return _clean_doc(session)


def update_quiz_session_evaluation(
    session_id: str,
    score: int,
    percentage: float,
    user_answers: Dict[str, Any],
    mistaken_topics: List[str],
    topic: str,
) -> None:
    """Record evaluation results, update session, weak areas, and mastery."""
    db = get_db()
    completed_at = datetime.now(timezone.utc).isoformat()
    db.quiz_sessions.update_one(
        {"id": session_id},
        {"$set": {
            "score": score,
            "percentage": percentage,
            "status": "EVALUATED",
            "user_answers": user_answers,
            "completed_at": completed_at,
        }},
    )

    # Update Weak Areas
    for m_topic in set(mistaken_topics):
        db.weak_areas.update_one(
            {"topic": m_topic},
            {
                "$set": {"topic": m_topic, "subject": "Computer Science", "last_mistake_date": completed_at, "is_mastered": False},
                "$inc": {"mistake_count": 1},
            },
            upsert=True,
        )

    # Update Strong Areas
    if percentage >= 70:
        db.strong_areas.update_one(
            {"topic": topic},
            {
                "$set": {"topic": topic, "subject": "Computer Science"},
                "$inc": {"success_count": 1},
            },
            upsert=True,
        )

    # Dynamic student mastery update
    delta = 2.5 if percentage >= 70 else -1.5
    profile = get_student_profile(1)
    new_mastery = max(10.0, min(100.0, float(profile.get("mastery_score", 70.0)) + delta))
    db.student_profile.update_one(
        {"$or": [{"id": 1}, {"student_id": 1}, {"_id": 1}]},
        {"$set": {"mastery_score": new_mastery}},
    )


# ==========================================
# Weak Areas & Analytics Operations
# ==========================================

def list_weak_areas(is_mastered: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
    """List weak areas sorted by mistake count."""
    db = get_db()
    cursor = db.weak_areas.find({"is_mastered": is_mastered}).sort("mistake_count", -1).limit(limit)
    return _clean_docs(list(cursor))


def list_strong_areas(limit: int = 50) -> List[Dict[str, Any]]:
    """List strong areas sorted by success count."""
    db = get_db()
    cursor = db.strong_areas.find().sort("success_count", -1).limit(limit)
    return _clean_docs(list(cursor))


def list_subject_progress() -> List[Dict[str, Any]]:
    """List subject progress entries."""
    db = get_db()
    return _clean_docs(list(db.subject_progress.find().sort("progress", -1)))


def record_weak_area(topic: str, subject: str = "Computer Science") -> Dict[str, Any]:
    """Record a mistaken topic into weak areas."""
    db = get_db()
    completed_at = datetime.now(timezone.utc).isoformat()
    db.weak_areas.update_one(
        {"topic": topic},
        {
            "$set": {"topic": topic, "subject": subject, "last_mistake_date": completed_at, "is_mastered": False},
            "$inc": {"mistake_count": 1},
        },
        upsert=True,
    )
    return {"topic": topic, "subject": subject, "status": "recorded"}


def record_strong_area(topic: str, subject: str = "Computer Science") -> Dict[str, Any]:
    """Record a mastered topic into strong areas."""
    db = get_db()
    db.strong_areas.update_one(
        {"topic": topic},
        {
            "$set": {"topic": topic, "subject": subject},
            "$inc": {"success_count": 1},
        },
        upsert=True,
    )
    return {"topic": topic, "subject": subject, "status": "recorded"}


# ==========================================
# Spaced Revision Schedule Operations
# ==========================================

def list_revision_items(student_id: int = 1, due_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieve spaced repetition revision items."""
    db = get_db()
    today_str = date.today().isoformat()
    if due_only:
        query = {
            "student_id": student_id,
            "$or": [{"next_revision_date": {"$lte": today_str}}, {"status": "DUE"}],
        }
        items = list(db.revision_schedule.find(query).sort([("mistake_count", -1), ("next_revision_date", 1)]))
    else:
        items = list(db.revision_schedule.find({"student_id": student_id}).sort("next_revision_date", 1))

    return _clean_docs(items)


def record_revision_completion(item_id: Any, score: float, student_id: int = 1) -> Optional[Dict[str, Any]]:
    """Update spaced revision item after completion using Leitner spacing."""
    db = get_db()
    item = db.revision_schedule.find_one({"$or": [{"id": str(item_id)}, {"id": item_id}]})
    if not item:
        return None

    curr_interval = item.get("interval_days", 1)
    today = date.today()
    today_str = today.isoformat()

    if score >= 75.0:
        new_interval = max(3, curr_interval * 2)
        new_status = "COMPLETED"
    else:
        new_interval = 1
        new_status = "DUE"

    next_date = (today + timedelta(days=new_interval)).isoformat()
    db.revision_schedule.update_one(
        {"id": item.get("id")},
        {"$set": {
            "interval_days": new_interval,
            "next_revision_date": next_date,
            "last_reviewed_date": today_str,
            "mastery_score": score,
            "status": new_status,
        }},
    )
    item.update({
        "interval_days": new_interval,
        "next_revision_date": next_date,
        "last_reviewed_date": today_str,
        "mastery_score": score,
        "status": new_status,
    })
    return _clean_doc(item)


# ==========================================
# Study Plans & Voice Sessions Operations
# ==========================================

def insert_study_plan(
    plan_id: str,
    goal_id: Optional[str],
    title: str,
    target_date: Optional[str],
    total_hours_planned: float,
    student_id: int = 1,
) -> Dict[str, Any]:
    """Store an adaptive study plan in MongoDB."""
    db = get_db()
    doc = {
        "id": plan_id,
        "student_id": student_id,
        "goal_id": goal_id,
        "title": title,
        "target_date": target_date,
        "total_hours_planned": total_hours_planned,
        "status": "ACTIVE",
        "created_at": date.today().isoformat(),
    }
    db.study_plans.update_one({"id": plan_id}, {"$set": doc}, upsert=True)
    return doc


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
    db = get_db()
    created_at = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": session_id,
        "student_id": student_id,
        "language": language,
        "topic": topic,
        "goal_id": goal_id,
        "duration_seconds": duration_seconds,
        "transcript_summary": transcript_summary,
        "created_at": created_at,
    }
    db.voice_sessions.update_one({"id": session_id}, {"$set": doc}, upsert=True)
    return doc


def list_voice_sessions(student_id: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
    """List recent voice sessions."""
    db = get_db()
    sessions = list(db.voice_sessions.find({"student_id": student_id}).sort("created_at", -1).limit(limit))
    return _clean_docs(sessions)
