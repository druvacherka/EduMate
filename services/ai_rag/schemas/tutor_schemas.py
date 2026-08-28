"""Pydantic v2 validation schemas for AI Tutor & RAG Engine."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

LearningLevel = Literal["Beginner", "Intermediate", "Advanced"]
Language = Literal["English", "Hindi", "Telugu"]

class DocumentCitation(BaseModel):
    document_name: str = Field(..., description="Filename of uploaded PDF")
    page_number: int = Field(..., description="Page number of retrieved chunk")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    snippet: str = Field(..., description="Text snippet retrieved from vector store")

class CodeSnippet(BaseModel):
    language: str = Field(..., example="cpp")
    code: str = Field(..., example="struct Node { int data; Node* left; Node* right; };")

class TutorRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Student question or prompt")
    level: LearningLevel = Field("Beginner", description="Target explanation depth")
    language: Language = Field("English", description="Target response language")
    subject: str = Field("Data Structures", description="Academic subject")
    topic: str = Field("Binary Search Trees", description="Active learning topic")
    weak_areas: Optional[List[str]] = Field(default_factory=list, description="List of identified student weak areas")
    use_rag: bool = Field(True, description="Whether to perform RAG retrieval on uploaded study material")

class TutorResponse(BaseModel):
    response_text: str = Field(..., description="Markdown-formatted Socratic explanation")
    level: LearningLevel
    language: Language
    formula: Optional[str] = Field(None, description="LaTeX display math formula if applicable")
    code_snippet: Optional[CodeSnippet] = None
    citation: Optional[DocumentCitation] = None
    quick_actions: List[str] = Field(default_factory=list, description="Suggested follow-up Socratic chips")
    is_grounded: bool = Field(True, description="False if requested information was missing from study material")
