import os
from pydantic import BaseModel

class AIRAGSettings(BaseModel):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    default_model: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    fast_model: str = os.getenv("GEMINI_FAST_MODEL", "gemini-3.8-flash")
    quiz_fallback_models: str = os.getenv(
        "GEMINI_QUIZ_FALLBACK_MODELS",
        "gemini-3.1-flash-lite,gemini-3.5-flash,gemini-3.6-flash",
    )
    embedding_model: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    temperature: float = 0.4
    max_output_tokens: int = 2048

settings = AIRAGSettings()
