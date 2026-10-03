import os
from pydantic import BaseModel

class BackendSettings(BaseModel):
    app_name: str = "EduMate API Gateway"
    version: str = "1.0.0"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "*"]
    mongodb_uri: str = os.getenv("MONGODB_URI", os.getenv("DATABASE_URL", "mongodb://localhost:27017"))
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "edumate")
    database_url: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017/edumate")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

settings = BackendSettings()
