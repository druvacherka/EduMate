"""MongoDB Document Models and Schemas for EduMate.

Defines Pydantic v2 document schemas for MongoDB collections.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date


class StudentProfileDoc(BaseModel):
    student_id: int = Field(default=1, alias="_id")
    name: str = "Druva"
    email: str = "druva@edumate.ai"
    level: str = "Beginner"
    language: str = "English"
    current_subject: str = "Mathematics"
    current_topic: str = "Real Numbers: Logarithms & Euclid Division Lemma"
    mastery_score: float = 72.0
    study_streak_days: int = 3
    last_active_date: str = Field(default_factory=lambda: date.today().isoformat())
    education_level: str = "Telangana State Board SSC (Class 10)"
    institution: str = "Telangana State Model School"
    stream_branch: str = "TG SSC (English & Telugu Medium)"
    academic_year_semester: str = "Class 10th SSC (2026-2027)"
    daily_study_hours: float = 3.0
    onboarding_completed: bool = True
    active_goal_id: str = "tg-goal-ssc-gpa"

    class Config:
        populate_by_name = True


class StudentGoalDoc(BaseModel):
    id: str = Field(alias="_id")
    student_id: int = 1
    name: str
    goal_type: str = "academic"
    target_exam: Optional[str] = None
    target_date: Optional[str] = None
    priority: str = "HIGH"
    available_hours_per_day: float = 2.0
    current_level: str = "Beginner"
    target_level: str = "Advanced"
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: date.today().isoformat())

    class Config:
        populate_by_name = True


class DailyStudyTaskDoc(BaseModel):
    id: str = Field(alias="_id")
    plan_id: Optional[str] = None
    student_id: int = 1
    task_type: str = "LEARN"
    title: str
    subject: str
    topic: str
    estimated_minutes: int = 30
    is_completed: bool = False
    priority: str = "NORMAL"
    reason: Optional[str] = None
    date_scheduled: str = Field(default_factory=lambda: date.today().isoformat())

    class Config:
        populate_by_name = True


class StudyMaterialDoc(BaseModel):
    id: str = Field(alias="_id")
    name: str
    subject: str
    upload_date: str = Field(default_factory=lambda: date.today().isoformat())
    size_str: str = "1.0 MB"
    pages: int = 1
    chunks: int = 1
    status: str = "Ready"
    education_level: str = "All"
    curriculum: str = "General"
    goal_id: str = ""

    class Config:
        populate_by_name = True


class QuizSessionDoc(BaseModel):
    id: str = Field(alias="_id")
    topic: str
    difficulty: str
    total_questions: int
    score: int = 0
    percentage: float = 0.0
    status: str = "CREATED"
    questions: List[Dict[str, Any]] = []
    user_answers: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None

    class Config:
        populate_by_name = True


class WeakAreaDoc(BaseModel):
    topic: str = Field(alias="_id")
    subject: str = "Computer Science"
    mistake_count: int = 1
    last_mistake_date: str = Field(default_factory=lambda: date.today().isoformat())
    is_mastered: bool = False

    class Config:
        populate_by_name = True


class StrongAreaDoc(BaseModel):
    topic: str = Field(alias="_id")
    subject: str = "Computer Science"
    success_count: int = 1

    class Config:
        populate_by_name = True


class SubjectProgressDoc(BaseModel):
    subject_name: str = Field(alias="_id")
    progress: int = 0
    topics_completed: int = 0
    total_topics: int = 10
    status: str = "In Progress"

    class Config:
        populate_by_name = True


class RevisionScheduleDoc(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    student_id: int = 1
    subject: str
    topic: str
    learned_date: str = Field(default_factory=lambda: date.today().isoformat())
    interval_days: int = 1
    next_revision_date: str = Field(default_factory=lambda: date.today().isoformat())
    last_reviewed_date: Optional[str] = None
    mastery_score: float = 50.0
    mistake_count: int = 0
    status: str = "DUE"

    class Config:
        populate_by_name = True


class StudyPlanDoc(BaseModel):
    id: str = Field(alias="_id")
    student_id: int = 1
    goal_id: Optional[str] = None
    title: str
    target_date: Optional[str] = None
    total_hours_planned: float = 0.0
    status: str = "ACTIVE"
    created_at: str = Field(default_factory=lambda: date.today().isoformat())

    class Config:
        populate_by_name = True


class VoiceSessionDoc(BaseModel):
    id: str = Field(alias="_id")
    student_id: int = 1
    language: str = "English"
    topic: Optional[str] = None
    goal_id: Optional[str] = None
    duration_seconds: int = 0
    transcript_summary: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True


class StudyChunkDoc(BaseModel):
    chunk_id: str = Field(alias="_id")
    document_name: str
    page_number: int
    section_title: str
    text_snippet: str
    embedding: List[float]
    subject: Optional[str] = None
    topic: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        populate_by_name = True
