import os
from pydantic import BaseModel

class AIRAGSettings(BaseModel):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "demo_gemini_key")
    default_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    fast_model: str = os.getenv("GEMINI_FAST_MODEL", "gemini-1.5-flash")
    embedding_model: str = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    temperature: float = 0.4
    max_output_tokens: int = 2048

settings = AIRAGSettings()
