from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator

class SocraticChatRequest(BaseModel):
    query: str
    level: str = "Beginner"  # 'Beginner' | 'Intermediate' | 'Advanced'
    language: str = "English"  # 'English' | 'Hindi' | 'Telugu'
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    document_id: Optional[str] = None

    @field_validator("level", mode="before")
    @classmethod
    def normalize_level(cls, value: Any) -> str:
        if not value or not str(value).strip():
            return "Beginner"
        normalized = str(value).strip().capitalize()
        if normalized in ("Beginner", "Intermediate", "Advanced"):
            return normalized
        return "Beginner"

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language(cls, value: Any) -> str:
        if not value or not str(value).strip():
            return "English"
        normalized = str(value).strip().capitalize()
        if normalized in ("English", "Hindi", "Telugu"):
            return normalized
        return "English"


class AccountCredentials(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=12, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class SocraticChatResponse(BaseModel):
    response: str
    level: str
    language: str
    quick_actions: List[str] = Field(default_factory=list)
    citations: Optional[List[Dict[str, Any]]] = None

class QuizGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    num_questions: int = Field(3, ge=1, le=10)
    difficulty: Literal["Easy", "Medium", "Hard"] = "Medium"

    @field_validator("topic")
    @classmethod
    def normalize_topic(cls, value: str) -> str:
        topic = value.strip()
        if not topic:
            raise ValueError("Topic must not be blank.")
        return topic

class QuizQuestionSchema(BaseModel):
    id: str
    type: str  # 'mcq' | 'tf' | 'short'
    question: str
    options: Optional[List[str]] = None
    correctAnswer: Any
    explanation: str
    difficulty: str
    topic: str

class AnalyticsProfileResponse(BaseModel):
    name: str = "Student"
    email: str = ""
    level: str = "Beginner"
    language: str = "English"
    currentSubject: str = ""
    currentTopic: str = ""
    masteryScore: float = 0.0
    weakAreas: List[str] = Field(default_factory=list)
    strongAreas: List[str] = Field(default_factory=list)
    studyStreakDays: int = 0
    subjectProgress: Optional[List[Dict[str, Any]]] = None
    educationLevel: Optional[str] = ""
    institution: Optional[str] = ""
    streamBranch: Optional[str] = ""
    academicYearSemester: Optional[str] = ""
    dailyStudyHours: Optional[float] = 0.0
    onboardingCompleted: Optional[bool] = False
    activeGoalsCount: Optional[int] = 0


class RagSearchRequest(BaseModel):
    query_text: str = Field(..., description="Natural language search query")
    top_k: int = Field(5, ge=1, le=20, description="Max matching results")
    subject: Optional[str] = Field(None, description="Subject filter")
    topic: Optional[str] = Field(None, description="Topic filter")
    document_id: Optional[str] = Field(None, description="Limit search to one uploaded document")
    education_level: Optional[str] = Field(None, description="Education level filter")
    goal_id: Optional[str] = Field(None, description="Goal ID filter")


class RagSearchResponse(BaseModel):
    query: str
    answer: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)


class QuizSubmissionRequest(BaseModel):
    session_id: str
    user_answers: Dict[str, Any] = Field(..., description="Map of question_id to selected answer")


class QuizSubmissionResponse(BaseModel):
    session_id: str
    status: str
    score: int
    total_questions: int
    percentage: float
    mistakes_count: int
    mistaken_topics: List[str] = Field(default_factory=list)
    results: List[Dict[str, Any]] = Field(default_factory=list)


class StudyMaterialItem(BaseModel):
    id: str
    name: str
    subject: str
    uploadDate: str
    size: str
    pages: int
    chunks: int
    status: str
    education_level: Optional[str] = "All"
    curriculum: Optional[str] = "General"
    goal_id: Optional[str] = ""


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None
    language: Optional[str] = None
    current_subject: Optional[str] = None
    current_topic: Optional[str] = None
    education_level: Optional[str] = None
    institution: Optional[str] = None
    stream_branch: Optional[str] = None
    academic_year_semester: Optional[str] = None
    daily_study_hours: Optional[float] = None
    onboarding_completed: Optional[int] = None


# ==============================================================================
# Universal Adaptive Learning & Career Expansion Schemas
# ==============================================================================

class StudentGoalSchema(BaseModel):
    id: str
    name: str
    goal_type: str = "academic"  # 'academic' | 'exam' | 'career' | 'skill'
    target_exam: Optional[str] = None
    target_date: Optional[str] = None
    priority: str = "HIGH"  # 'HIGH' | 'MEDIUM' | 'LOW'
    available_hours_per_day: float = 2.0
    current_level: str = "Beginner"
    target_level: str = "Advanced"
    is_active: bool = True
    created_at: Optional[str] = None


class CreateGoalRequest(BaseModel):
    name: str
    goal_type: str = "academic"
    target_exam: Optional[str] = None
    target_date: Optional[str] = None
    priority: str = "HIGH"
    available_hours_per_day: float = 2.0
    current_level: str = "Beginner"
    target_level: str = "Advanced"


class UpdateGoalRequest(BaseModel):
    name: Optional[str] = None
    goal_type: Optional[str] = None
    target_exam: Optional[str] = None
    target_date: Optional[str] = None
    priority: Optional[str] = None
    available_hours_per_day: Optional[float] = None
    current_level: Optional[str] = None
    target_level: Optional[str] = None
    is_active: Optional[bool] = None


class DailyTaskSchema(BaseModel):
    id: str
    title: str
    subject: str
    topic: str
    task_type: str  # 'LEARN' | 'PRACTICE' | 'QUIZ' | 'REVISE' | 'REVIEW_MISTAKES'
    estimated_minutes: int
    is_completed: bool
    priority: str  # 'HIGH' | 'MEDIUM' | 'NORMAL'
    reason: Optional[str] = None
    date_scheduled: str
    plan_id: Optional[str] = None


class DailyDashboardResponse(BaseModel):
    greeting: str
    student_name: str
    education_level: str
    stream_branch: str
    available_hours_today: float
    study_streak_days: int
    overall_mastery: float
    active_goals: List[StudentGoalSchema]
    today_tasks: List[DailyTaskSchema]
    total_tasks_count: int
    completed_tasks_count: int
    estimated_time_remaining_minutes: int
    priority_weak_areas: List[str]
    recent_recommendation: Optional[Dict[str, Any]] = None


class ToggleTaskRequest(BaseModel):
    task_id: str


class StudyPlanItemSchema(BaseModel):
    week_number: int
    theme: str
    focus_topics: List[str]
    target_milestone: str
    estimated_hours: float


class StudyPlanSchema(BaseModel):
    id: str
    goal_id: Optional[str] = None
    title: str
    target_date: Optional[str] = None
    total_hours_planned: float
    status: str
    weekly_breakdown: List[StudyPlanItemSchema] = Field(default_factory=list)


class GeneratePlanRequest(BaseModel):
    goal_id: Optional[str] = None
    goal_name: str = Field(..., min_length=1, max_length=200)
    target_date: Optional[str] = None
    available_hours_per_day: float = Field(2.0, gt=0, le=24)
    current_level: Optional[str] = None
    target_level: Optional[str] = None


class CurriculumLevelSchema(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    streams: List[str]


class SubjectTopicSchema(BaseModel):
    id: str
    subject: str
    topic: str
    chapter: Optional[str] = None
    key_concepts: List[str] = Field(default_factory=list)
    difficulty: str = "Medium"
    importance_for_exams: Optional[List[str]] = None


class CurriculumHierarchyResponse(BaseModel):
    education_level: str
    stream: str
    subjects: List[Dict[str, Any]]


class RevisionItemSchema(BaseModel):
    id: int
    subject: str
    topic: str
    learned_date: str
    interval_days: int
    next_revision_date: str
    last_reviewed_date: Optional[str] = None
    mastery_score: float
    mistake_count: int
    status: str  # 'DUE' | 'PENDING' | 'COMPLETED'


class CompleteRevisionRequest(BaseModel):
    item_id: int
    score: float = 100.0


class CareerPathSchema(BaseModel):
    id: str
    title: str
    category: str
    description: str
    target_degrees: List[str]
    primary_exams: List[str]
    core_subjects: List[str]
    key_skills: List[str]
    typical_roadmap: List[str]


class VoiceSessionCreateRequest(BaseModel):
    language: str = "English"
    topic: Optional[str] = None
    goal_id: Optional[str] = None
    duration_seconds: int = 0
    transcript_summary: Optional[str] = None


class VoiceSessionResponse(BaseModel):
    id: str
    language: str
    topic: Optional[str] = None
    duration_seconds: int
    created_at: str


class OnboardingRequest(BaseModel):
    name: str
    preferred_language: str = "English"
    education_level: str
    institution: Optional[str] = ""
    stream_branch: str
    academic_year_semester: Optional[str] = ""
    daily_study_hours: float = 2.0
    initial_goals: List[str] = Field(default_factory=list)


class OnboardingResponse(BaseModel):
    status: str
    message: str
    profile: Dict[str, Any]
    active_goals: List[StudentGoalSchema]
