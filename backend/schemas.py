from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SocraticChatRequest(BaseModel):
    query: str
    level: str = "Beginner"  # 'Beginner' | 'Intermediate' | 'Advanced'
    language: str = "English"  # 'English' | 'Hindi' | 'Telugu'
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    document_id: Optional[str] = None

class SocraticChatResponse(BaseModel):
    response: str
    level: str
    language: str
    quick_actions: List[str] = Field(default_factory=list)
    citations: Optional[List[Dict[str, Any]]] = None

class QuizGenerationRequest(BaseModel):
    topic: str
    num_questions: int = 3
    difficulty: str = "Medium"

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
    name: str = "B.Tech Student"
    email: str = "student@edumate.ai"
    level: str = "Beginner"
    language: str = "English"
    currentSubject: str = "Data Structures & Algorithms"
    currentTopic: str = "Binary Search Trees"
    masteryScore: float = 78.5
    weakAreas: List[str] = Field(default_factory=lambda: ["Tree Balancing", "Graph Traversals", "Recurrence Relations"])
    strongAreas: List[str] = Field(default_factory=lambda: ["Arrays & HashMaps", "Sorting Algorithms", "Stack Operations"])
    studyStreakDays: int = 5
    subjectProgress: Optional[List[Dict[str, Any]]] = None


class RagSearchRequest(BaseModel):
    query_text: str = Field(..., description="Natural language search query")
    top_k: int = Field(5, ge=1, le=20, description="Max matching results")
    subject: Optional[str] = Field(None, description="Subject filter")
    topic: Optional[str] = Field(None, description="Topic filter")


class RagSearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[Dict[str, Any]] = Field(default_factory=list)


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


class UpdateProfileRequest(BaseModel):
    level: Optional[str] = None
    language: Optional[str] = None
    current_subject: Optional[str] = None
    current_topic: Optional[str] = None


