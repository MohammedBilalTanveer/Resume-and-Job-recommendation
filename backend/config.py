from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

# Load .env from backend folder
from dotenv import load_dotenv
backend_dir = Path(__file__).parent
load_dotenv(backend_dir / ".env")

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "Resume ATS Scorer & Job Recommendation"
    API_VERSION: str = "1.0.0"
    
    # CORS - allow both ports
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000", "*"]
    
    # File Upload
    UPLOAD_FOLDER: str = os.path.join(os.path.dirname(__file__), "../uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "docx"]
    
    # ML Models
    MODEL_FOLDER: str = os.path.join(os.path.dirname(__file__), "../ml_models")
    
    # Database
    DATABASE_URL: str = "sqlite:///./resume_ats.db"
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # External APIs
    ADZUNA_APP_ID: str = os.getenv("ADZUNA_APP_ID", "")
    ADZUNA_APP_KEY: str = os.getenv("ADZUNA_API_KEY", "")
    
    REMOTIVE_API_URL: str = "https://remotive.com/api/remote-jobs"
    
    JOOBLE_API_KEY: str = os.getenv("JOOBLE_API_KEY", "")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Create upload folder if not exists
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.MODEL_FOLDER, exist_ok=True)
