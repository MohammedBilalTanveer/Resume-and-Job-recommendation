from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path
import secrets

# Load backend/.env, then the project-root .env for anything still unset.
# Real environment variables (e.g. set in the Render dashboard) always win, and
# empty values like "GITHUB_CLIENT_ID=" never mask a value from the other file.
from dotenv import dotenv_values
backend_dir = Path(__file__).parent
for _env_file in (backend_dir / ".env", backend_dir.parent / ".env"):
    if _env_file.exists():
        for _key, _value in dotenv_values(_env_file).items():
            if _value and not os.environ.get(_key):
                os.environ[_key] = _value

# Alternative names accepted for some variables -> the name the code reads
_ENV_ALIASES = {
    "GOOGLE_CLIENT_ID": ["GOOGLE_CLIENT_API"],
    "GOOGLE_CLIENT_SECRET": ["GOOGLE_SECRET_API", "GOOGLE_SECRET_KEY"],
    "GITHUB_CLIENT_SECRET": ["GITHUB_SECRET_KEY", "GITHUB_SECRET_API"],
    "ADZUNA_API_KEY": ["ADZUNA_APP_KEY"],
    "MONGODB_URL": ["MONGODB_URI"],
}
for _canonical, _alternatives in _ENV_ALIASES.items():
    if not os.environ.get(_canonical):
        for _alt in _alternatives:
            if os.environ.get(_alt):
                os.environ[_canonical] = os.environ[_alt]
                break

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "Resume ATS Scorer & Job Recommendation"
    API_VERSION: str = "1.0.0"
    
    # CORS: local dev ports + FRONTEND_URL are always allowed. Extra origins go in
    # CORS_ORIGINS as a comma-separated list; CORS_ORIGIN_REGEX can allow e.g. Vercel
    # preview deployments (https://your-app-.*\.vercel\.app).
    CORS_ORIGINS: str = ""
    CORS_ORIGIN_REGEX: str = ""

    @property
    def cors_origin_list(self) -> List[str]:
        origins = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]
        for origin in [self.FRONTEND_URL] + self.CORS_ORIGINS.split(","):
            origin = origin.strip().rstrip("/")
            if origin and origin not in origins:
                origins.append(origin)
        return origins
    
    # File Upload
    UPLOAD_FOLDER: str = os.path.join(os.path.dirname(__file__), "../uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "docx"]
    
    # ML Models
    MODEL_FOLDER: str = os.path.join(os.path.dirname(__file__), "../ml_models")
    
    # MongoDB Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "resume_ats")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    
    # OAuth - Google
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # OAuth - GitHub
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    
    # Frontend URL for OAuth redirects
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # External APIs
    ADZUNA_APP_ID: str = os.getenv("ADZUNA_APP_ID", "")
    ADZUNA_APP_KEY: str = os.getenv("ADZUNA_API_KEY", "")
    
    REMOTIVE_API_URL: str = "https://remotive.com/api/remote-jobs"
    
    JOOBLE_API_KEY: str = os.getenv("JOOBLE_API_KEY", "")

    # Job catalog: jobs are fetched on a daily rotation and served from MongoDB.
    # POST /api/v1/jobs/refresh needs this token (header X-Refresh-Token); empty disables it.
    JOBS_REFRESH_TOKEN: str = ""
    JOB_TTL_DAYS: int = 21                      # stored jobs expire this long after last seen
    # Markets refreshed on rotation: "country" or "country:city" (Adzuna country codes)
    JOB_MARKETS: str = "in,in:Bangalore,in:Hyderabad,in:Pune,in:Mumbai,in:Delhi,in:Chennai,us,gb"

    # API quotas (free tiers). The daily refresh leaves headroom for live fallback searches.
    ADZUNA_LIMIT_MINUTE: int = 25
    ADZUNA_LIMIT_DAY: int = 250
    ADZUNA_LIMIT_WEEK: int = 1000
    ADZUNA_LIMIT_MONTH: int = 2500
    ADZUNA_REFRESH_PER_DAY: int = 70            # ~2,100/month, leaving ~400 for live fallbacks
    JOOBLE_LIMIT_TOTAL: int = 500               # per-account limit; Jooble is used for live fallbacks only
    JOOBLE_LIMIT_DAY: int = 5
    # Remotive's terms forbid showing its jobs to collect sign-ups (the Jobs page needs login),
    # so it's off unless jobs are shown publicly. Max 4 calls/day per their API notice.
    ENABLE_REMOTIVE: bool = False
    REMOTIVE_LIMIT_DAY: int = 4
    
    class Config:
        # .env files are loaded into os.environ above, so settings don't depend
        # on which directory the server is started from
        extra = "ignore"

settings = Settings()

# Create upload folder if not exists
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.MODEL_FOLDER, exist_ok=True)
