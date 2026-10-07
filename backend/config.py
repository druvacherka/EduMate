import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class BackendSettings(BaseModel):
    app_name: str = "EduMate API Gateway"
    version: str = "1.0.0"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "*"]
    database_url: str = os.getenv("DATABASE_URL", "")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "edumate-secure-dev-jwt-secret-key-32chars-min")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

settings = BackendSettings()
