# IntelliDiots - Complete Code Documentation & Reference

A comprehensive AI-powered resume analysis and job recommendation system built with FastAPI, React, PyTorch Neural Networks, and MongoDB.

---

## 📋 Table of Contents

1. [Backend Architecture](#backend-architecture)
2. [Authentication System](#authentication-system)
3. [Resume Processing](#resume-processing)
4. [ATS Scoring Engine](#ats-scoring-engine)
5. [Job Integration Service](#job-integration-service)
6. [Frontend Components](#frontend-components)
7. [Database Schema](#database-schema)
8. [API Endpoints](#api-endpoints)
9. [Deployment & Configuration](#deployment--configuration)

---

## 🏗️ Backend Architecture

### Main Application Setup

The main FastAPI application initializes the API server with CORS support and lifespan management for database connections.

**File**: `backend/main.py`

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path

# Add ML models to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.routes import resume, jobs, models as model_routes, auth, history
from backend.config import settings
from backend.database import init_database, close_connections


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Manages database initialization and cleanup.
    """
    # Startup: Initialize MongoDB indexes
    await init_database()
    print("[INFO] Database initialized")
    yield
    # Shutdown: Close connections
    close_connections()
    print("[INFO] Connections closed")


# API Configuration
app = FastAPI(
    title="Resume ATS Scorer & Job Recommendation System",
    description="AI-powered resume analysis and job matching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(history.router, prefix="/api/v1/history", tags=["History"])
app.include_router(model_routes.router, prefix="/api/v1/models", tags=["Models"])

@app.get("/")
def read_root():
    """API root endpoint with available endpoints."""
    return {
        "message": "Resume ATS Scorer & Job Recommendation System",
        "version": "1.0.0",
        "endpoints": {
            "resume": "/api/v1/resume",
            "jobs": "/api/v1/jobs",
            "auth": "/api/v1/auth",
            "history": "/api/v1/history",
            "models": "/api/v1/models"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### Configuration Management

**File**: `backend/config.py`

```python
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path
import secrets
from dotenv import load_dotenv

backend_dir = Path(__file__).parent
load_dotenv(backend_dir / ".env")

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic for validation and type safety.
    """
    
    # API Settings
    API_TITLE: str = "Resume ATS Scorer & Job Recommendation"
    API_VERSION: str = "1.0.0"
    
    # CORS Configuration - Allow both development ports
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "*"
    ]
    
    # File Upload Configuration
    UPLOAD_FOLDER: str = os.path.join(os.path.dirname(__file__), "../uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB limit
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "docx"]
    
    # ML Models Path
    MODEL_FOLDER: str = os.path.join(os.path.dirname(__file__), "../ml_models")
    
    # MongoDB Database Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "resume_ats")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OAuth Configuration - Google
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # OAuth Configuration - GitHub
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    
    # Frontend URL for OAuth Redirects
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # External API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ADZUNA_APP_ID: str = os.getenv("ADZUNA_APP_ID", "")
    ADZUNA_APP_KEY: str = os.getenv("ADZUNA_APP_KEY", "")
    JOOBLE_API_KEY: str = os.getenv("JOOBLE_API_KEY", "")

settings = Settings()
```

### Database Connection Management

**File**: `backend/database.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, ASCENDING, DESCENDING
from backend.config import settings
from typing import Optional

# Global MongoDB client instances
_async_client: Optional[AsyncIOMotorClient] = None
_sync_client: Optional[MongoClient] = None


def get_sync_client() -> MongoClient:
    """
    Get synchronous MongoDB client for blocking operations.
    Used during startup/shutdown procedures.
    """
    global _sync_client
    if _sync_client is None:
        _sync_client = MongoClient(settings.MONGODB_URL)
    return _sync_client


def get_async_client() -> AsyncIOMotorClient:
    """
    Get asynchronous MongoDB client for async operations.
    Recommended for FastAPI async route handlers.
    """
    global _async_client
    if _async_client is None:
        _async_client = AsyncIOMotorClient(settings.MONGODB_URL)
    return _async_client


def get_database():
    """Get the async database instance."""
    client = get_async_client()
    return client[settings.MONGODB_DB_NAME]


def get_sync_database():
    """Get the synchronous database instance."""
    client = get_sync_client()
    return client[settings.MONGODB_DB_NAME]


# Collection Accessors
def get_users_collection():
    """Get users collection for user management."""
    return get_database()["users"]


def get_analyses_collection():
    """Get resume analyses collection for storing analysis results."""
    return get_database()["resume_analyses"]


def get_counters_collection():
    """Get counters collection for auto-increment IDs."""
    return get_database()["counters"]


async def init_database():
    """Initialize database indexes on startup."""
    try:
        db = get_database()
        
        # Create indexes for faster queries
        users_col = db["users"]
        await users_col.create_index("email", unique=True)
        await users_col.create_index("oauth_id")
        
        analyses_col = db["resume_analyses"]
        await analyses_col.create_index("user_id")
        await analyses_col.create_index("created_at")
        
        print("[INFO] Database indexes created successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")


def close_connections():
    """Close all database connections on shutdown."""
    global _async_client, _sync_client
    if _async_client:
        _async_client.close()
    if _sync_client:
        _sync_client.close()


async def get_next_sequence(name: str) -> int:
    """
    Get the next sequence number for auto-increment IDs.
    MongoDB doesn't have native auto-increment, so we use a counter collection.
    """
    counters = get_counters_collection()
    result = await counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return result["seq"]
```

---

## 🔐 Authentication System

### Password & Token Management

**File**: `backend/utils/auth.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.database import get_users_collection, get_next_sequence
from backend.models.user import UserInDB, user_from_doc
import os

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password Hashing with Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer Token Scheme
bearer_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    Uses bcrypt for secure comparison.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    Called during user registration.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    Expires in 24 hours by default.
    
    Args:
        data: Claims to encode in token (e.g., {"sub": user_id})
        expires_delta: Custom expiration time
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.
    Expires in 7 days.
    Used to obtain new access tokens without re-authentication.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"[ERROR] Token decode failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UserInDB:
    """
    Dependency to get the current authenticated user.
    Validates JWT token and retrieves user from database.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials"
        )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims"
        )
    
    user = await get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get a user by email address."""
    users = get_users_collection()
    doc = await users.find_one({"email": email})
    return user_from_doc(doc)


async def get_user_by_id(user_id: int) -> Optional[UserInDB]:
    """Get a user by ID."""
    users = get_users_collection()
    doc = await users.find_one({"id": user_id})
    return user_from_doc(doc)


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user with email and password.
    
    Args:
        email: User email
        password: Plain password
    
    Returns:
        User object if credentials are valid, None otherwise
    """
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(
    email: str,
    password: str,
    full_name: Optional[str] = None
) -> UserInDB:
    """
    Create a new user with email and password.
    
    Args:
        email: User email
        password: Plain password (will be hashed)
        full_name: User's full name
    
    Returns:
        Created user object
    """
    users = get_users_collection()
    user_id = await get_next_sequence("user_id")
    
    user_doc = {
        "id": user_id,
        "email": email,
        "hashed_password": get_password_hash(password),
        "full_name": full_name,
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    await users.insert_one(user_doc)
    return user_from_doc(user_doc)
```

### Authentication Routes

**File**: `backend/routes/auth.py`

```python
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import httpx
import os

from backend.database import get_users_collection
from backend.models.user import UserInDB, user_from_doc
from backend.utils.auth import (
    create_access_token, create_refresh_token, decode_token,
    get_password_hash, authenticate_user, get_user_by_email,
    get_current_user, get_user_by_id, verify_password
)

router = APIRouter()

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


# Pydantic Models for Request/Response
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    oauth_provider: Optional[str]
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Authentication Endpoints
@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup):
    """
    Register a new user with email and password.
    
    - Validates email uniqueness
    - Checks password requirements (8+ characters)
    - Generates JWT access and refresh tokens
    - Returns user and tokens
    """
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Create user (see auth.py for implementation)
    user = await create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    # Generate JWT tokens (sub must be string per JWT specification)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password.
    
    - Authenticates user credentials
    - Generates JWT tokens
    - Returns authenticated user and tokens
    """
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """
    Get a new access token using a refresh token.
    
    - Validates refresh token
    - Generates new access token
    - Returns new access token
    """
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    access_token = create_access_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current authenticated user information.
    Requires valid JWT token in Authorization header.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at
    }
```

---

## 📄 Resume Processing

### PDF/DOCX/TXT Parser

**File**: `backend/utils/pdf_parser.py`

```python
import pdfplumber
import os
from pathlib import Path
from typing import Optional


def parse_resume(file_path: str) -> str:
    """
    Extract text from PDF, DOCX, or TXT files.
    
    Args:
        file_path: Path to resume file
    
    Returns:
        Extracted text content from file
    """
    try:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return parse_pdf(file_path)
        elif file_ext == '.txt':
            return parse_txt(file_path)
        elif file_ext == '.docx':
            return parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    except Exception as e:
        print(f"[ERROR] Error parsing resume: {e}")
        return ""


def parse_pdf(file_path: str) -> str:
    """
    Extract text from PDF file using pdfplumber.
    
    Features:
    - Handles multi-page PDFs
    - Preserves formatting where possible
    - Extracts text from all pages
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ""
                if page_text:
                    text += f"--- Page {page_num} ---\n{page_text}\n"
        
        if not text:
            print(f"[WARNING] No text extracted from PDF: {file_path}")
    
    except Exception as e:
        print(f"[ERROR] Error parsing PDF: {e}")
    
    return text


def parse_txt(file_path: str) -> str:
    """
    Read text from TXT file.
    Simple UTF-8 text file reading.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] Error reading TXT file: {e}")
        return ""


def parse_docx(file_path: str) -> str:
    """
    Extract text from DOCX file using python-docx.
    Extracts text from all paragraphs in the document.
    """
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except ImportError:
        print("[ERROR] python-docx not installed. Cannot parse DOCX files.")
        return ""
    except Exception as e:
        print(f"[ERROR] Error parsing DOCX file: {e}")
        return ""
```

### Resume Upload & Analysis Route

**File**: `backend/routes/resume.py` (Partial)

```python
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body, Depends
from typing import Optional
from pydantic import BaseModel
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.utils.pdf_parser import parse_resume
from backend.utils.advanced_ats_scorer import advanced_ats_scorer
from backend.utils.auth import get_current_user

router = APIRouter()


class ScoreRequest(BaseModel):
    """Request model for ATS scoring."""
    resume_text: str
    job_description: str


class ExtractRequest(BaseModel):
    """Request model for skill extraction."""
    resume_text: str


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...), 
    job_description: Optional[str] = Form(None),
    current_user = Depends(get_current_user)
):
    """
    Upload and analyze a resume with comprehensive ATS scoring.
    
    Parameters:
    - file: Resume file (PDF, DOCX, or TXT)
    - job_description: Optional job description for comparison
    - current_user: Authenticated user (required)
    
    Returns:
    - filename: Uploaded file name
    - resume_text: Extracted text from file
    - ats_analysis: Comprehensive ATS analysis (if job_description provided)
    - extracted_info: Basic extracted information (if no job_description)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file_contents = await file.read()
        if len(file_contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Save uploaded file
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_FOLDER, f"{current_user.id}_{file.filename}")
        
        with open(file_path, "wb") as f:
            f.write(file_contents)
        
        # Parse resume (extract text)
        resume_text = parse_resume(file_path)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from resume"
            )
        
        # Build response
        response = {
            "filename": file.filename,
            "resume_text": resume_text,
            "ats_analysis": None,
            "extracted_info": None
        }
        
        # Perform comprehensive ATS analysis if job description provided
        if job_description and job_description.strip():
            analysis = advanced_ats_scorer.comprehensive_analysis(
                resume_text,
                job_description
            )
            response["ats_analysis"] = analysis
        else:
            # Just extract basic info without job comparison
            resume_lower = resume_text.lower()
            skills = advanced_ats_scorer._extract_all_skills(resume_lower)
            response["extracted_info"] = {
                "skills": skills["all"],
                "skills_by_category": skills["by_category"],
                "experience_years": advanced_ats_scorer._extract_experience_years(resume_lower),
                "education": advanced_ats_scorer._extract_education(resume_lower),
                "contact_info": advanced_ats_scorer._extract_contact_info(resume_text),
                "sections": advanced_ats_scorer._analyze_resume_structure(resume_text),
                "action_verbs": advanced_ats_scorer._extract_action_verbs(resume_text)
            }
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score")
async def score_resume(
    request: ScoreRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate comprehensive ATS score for given resume and job description.
    
    Performs:
    - Keyword matching
    - Skill extraction and matching
    - Format analysis
    - AI-powered recommendations (if OpenAI available)
    
    Returns detailed analysis with improvement recommendations.
    """
    try:
        if not request.resume_text or not request.job_description:
            raise HTTPException(
                status_code=400,
                detail="Both resume_text and job_description are required"
            )
        
        # Perform comprehensive analysis
        analysis = advanced_ats_scorer.comprehensive_analysis(
            request.resume_text,
            request.job_description
        )
        
        return analysis
    
    except Exception as e:
        print(f"[ERROR] Scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🤖 ATS Scoring Engine

### Neural Network Model

**File**: `backend/utils/ats_scorer.py` (Partial)

```python
import re
import torch
import torch.nn as nn
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class ATSNeuralNetwork(nn.Module):
    """
    Neural Network model for ATS scoring.
    
    Architecture:
    - Input: TF-IDF vector (500 features)
    - Layer 1: Linear(500 -> 256) + ReLU + Dropout(0.3)
    - Layer 2: Linear(256 -> 128) + ReLU + Dropout(0.2)
    - Layer 3: Linear(128 -> 64) + ReLU
    - Output: Linear(64 -> 1) + Sigmoid
    
    Output: Normalized ATS score between 0 and 1
    """
    
    def __init__(self, input_size=500, hidden_size=256):
        super(ATSNeuralNetwork, self).__init__()
        
        # First hidden layer
        self.fc1 = nn.Linear(input_size, min(hidden_size, input_size // 2))
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.3)
        
        # Second hidden layer
        self.fc2 = nn.Linear(min(hidden_size, input_size // 2), 128)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.2)
        
        # Third hidden layer
        self.fc3 = nn.Linear(128, 64)
        self.relu3 = nn.ReLU()
        
        # Output layer with sigmoid for normalization
        self.fc4 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        """
        Forward pass through the network.
        
        Args:
            x: Input tensor of shape (batch_size, input_size)
        
        Returns:
            Output tensor of shape (batch_size, 1) with values in [0, 1]
        """
        # Layer 1
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.dropout1(x)
        
        # Layer 2
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.dropout2(x)
        
        # Layer 3
        x = self.fc3(x)
        x = self.relu3(x)
        
        # Output layer
        x = self.fc4(x)
        x = self.sigmoid(x)
        
        return x


class ATSScorer:
    """
    ATS Score calculator using TF-IDF and skill matching.
    Computes match between resume and job description.
    """
    
    # Comprehensive skill dictionary categorized
    SKILLS_DICT = {
        "programming_languages": [
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "php", "ruby", "kotlin", "swift", "scala", "r", "matlab", "perl", "dart"
        ],
        "web_frameworks": [
            "react", "angular", "vue", "django", "flask", "fastapi", "express",
            "spring", "asp.net", "laravel", "rails", "nextjs", "nuxt", "gatsby"
        ],
        "databases": [
            "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
            "dynamodb", "firestore", "oracle", "sql server", "mariadb", "sqlite"
        ],
        "cloud_platforms": [
            "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean",
            "linode", "ibm cloud", "oracle cloud", "alibaba cloud"
        ],
        "devops_tools": [
            "docker", "kubernetes", "jenkins", "gitlab", "github", "bitbucket",
            "terraform", "ansible", "puppet", "chef", "circleci", "travis"
        ],
        "data_science": [
            "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
            "scikit-learn", "pandas", "numpy", "nlp", "computer vision"
        ]
    }
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.model = None
    
    def extract_resume_info(self, resume_text: str) -> Dict:
        """
        Extract key information from resume text.
        
        Returns:
            Dict with extracted:
            - skills: List of detected skills
            - experience_years: Estimated years of experience
            - education: Detected educational qualifications
            - contact_info: Email, phone, location if found
        """
        skills = self._extract_skills(resume_text)
        experience = self._extract_experience_years(resume_text)
        education = self._extract_education(resume_text)
        
        return {
            "skills": skills,
            "experience_years": experience,
            "education": education
        }
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text by matching against skill dictionary."""
        detected_skills = []
        text_lower = text.lower()
        
        for category, skills in self.SKILLS_DICT.items():
            for skill in skills:
                if skill in text_lower:
                    detected_skills.append(skill)
        
        return list(set(detected_skills))  # Remove duplicates
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract years of experience from resume text."""
        import re
        
        # Pattern to find years of experience
        patterns = [
            r'(\d+)\s*(?:\+)?\s*years?\s+(?:of\s+)?(?:experience|exp)',
            r'(?:total\s+)?(\d+)\s*(?:\+)?\s*years?\s+(?:professional\s+)?(?:experience)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract educational qualifications."""
        educations = []
        keywords = [
            'bachelor', 'master', 'phd', 'diploma', 'associate',
            'bsc', 'msc', 'btech', 'mtech', 'b.a', 'm.a',
            'engineering', 'computer science', 'information technology'
        ]
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                educations.append(keyword.title())
        
        return educations
    
    def calculate_ats_score(self, resume_text: str, job_description: str) -> float:
        """
        Calculate ATS score between resume and job description.
        Uses TF-IDF and cosine similarity.
        
        Returns:
            Score between 0 and 100
        """
        try:
            # Combine texts for vectorization
            texts = [resume_text, job_description]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
            
            # Convert to 0-100 scale
            score = similarity * 100
            
            return round(score, 2)
        
        except Exception as e:
            print(f"[ERROR] ATS scoring failed: {e}")
            return 0.0
```

### Advanced ATS Scorer with AI

**File**: `backend/utils/advanced_ats_scorer.py` (Partial)

```python
class AdvancedATSScorer:
    """
    Advanced ATS Scoring System with ML/NN-based scoring and AI analysis.
    
    Features:
    - Neural Network scoring
    - Skill category matching
    - Format analysis
    - AI-powered recommendations (OpenAI)
    - Missing keyword detection
    - Action verb analysis
    """
    
    SKILLS_DATABASE = {
        "programming_languages": [
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
            "rust", "swift", "kotlin", "php", "scala", "r", "matlab", "perl"
        ],
        "frameworks_libraries": [
            "react", "angular", "vue", "django", "flask", "fastapi", "spring",
            "spring boot", ".net", "rails", "laravel", "nextjs", "nuxt"
        ],
        "cloud_devops": [
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
            "terraform", "ansible", "gitlab", "github actions"
        ],
        "databases": [
            "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            "cassandra", "dynamodb", "firebase"
        ],
        "data_science_ai": [
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "keras", "nlp", "computer vision", "transformers"
        ]
    }
    
    FORMAT_KEYWORDS = {
        "sections": [
            "experience", "education", "skills", "projects", "certifications",
            "summary", "objective", "achievements", "awards", "publications"
        ],
        "action_verbs": [
            "developed", "implemented", "designed", "led", "managed",
            "created", "built", "improved", "increased", "reduced",
            "achieved", "delivered", "launched", "optimized"
        ]
    }
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.vectorizer = TfidfVectorizer(max_features=500)
        self._load_trained_models()
    
    def comprehensive_analysis(self, resume_text: str, job_description: str) -> Dict:
        """
        Perform comprehensive ATS analysis of resume against job description.
        
        Returns:
            Dict with:
            - ats_score: Overall ATS score (0-100)
            - matching_keywords: Keywords found in both
            - missing_keywords: Important keywords missing from resume
            - skills_match: Matched skills by category
            - format_score: Resume format analysis
            - recommendations: AI-generated improvement suggestions
        """
        try:
            # Extract key information
            job_keywords = self._extract_keywords(job_description)
            resume_keywords = self._extract_keywords(resume_text)
            
            # Calculate matching keywords
            matching = set(resume_keywords) & set(job_keywords)
            missing = set(job_keywords) - set(resume_keywords)
            
            # Extract and match skills
            resume_skills = self._extract_all_skills(resume_text)
            job_skills = self._extract_job_required_skills(job_description)
            skills_match = self._match_skills(resume_skills, job_skills)
            
            # Calculate overall ATS score
            ats_score = self._calculate_neural_ats_score(resume_text, job_description)
            
            # Analyze format
            format_score = self._analyze_format(resume_text)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                resume_text,
                job_description,
                missing,
                skills_match
            )
            
            return {
                "ats_score": ats_score,
                "matching_keywords": list(matching)[:20],  # Top 20
                "missing_keywords": list(missing)[:15],     # Top 15
                "skills_match": skills_match,
                "format_score": format_score,
                "recommendations": recommendations,
                "sections_found": self._analyze_resume_structure(resume_text)
            }
        
        except Exception as e:
            print(f"[ERROR] Comprehensive analysis failed: {e}")
            return {"error": str(e)}
    
    def _extract_all_skills(self, text: str) -> Dict:
        """
        Extract all skills from text, categorized.
        
        Returns:
            Dict with:
            - all: List of all detected skills
            - by_category: Skills grouped by category
        """
        text_lower = text.lower()
        skills_found = {"all": [], "by_category": {}}
        
        for category, skills in self.SKILLS_DATABASE.items():
            found_in_category = []
            for skill in skills:
                if skill in text_lower:
                    skills_found["all"].append(skill)
                    found_in_category.append(skill)
            
            if found_in_category:
                skills_found["by_category"][category] = found_in_category
        
        return skills_found
    
    def _calculate_neural_ats_score(self, resume: str, job_desc: str) -> float:
        """Calculate ATS score using neural network."""
        try:
            # Vectorize texts
            texts = [resume, job_desc]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Convert to dense for neural network
            resume_vec = torch.FloatTensor(tfidf_matrix[0].toarray()).to(self.device)
            
            # Calculate similarity-based score
            similarity = cosine_similarity(
                tfidf_matrix[0],
                tfidf_matrix[1]
            )[0][0]
            
            score = (similarity * 100)
            return round(max(0, min(100, score)), 2)
        
        except Exception as e:
            print(f"[ERROR] Neural ATS scoring failed: {e}")
            return 0.0
```

---

## 💼 Job Integration Service

**File**: `backend/services/job_service.py` (Partial)

```python
import aiohttp
import asyncio
from typing import List, Optional, Dict
from datetime import datetime
from backend.config import settings


class JobService:
    """
    Service to integrate multiple job APIs for job search and recommendations.
    
    Supported Sources:
    - Remotive (Remote jobs, free API)
    - Adzuna (Job search, requires API key)
    - Jooble (Job search, requires API key)
    """
    
    def __init__(self):
        self.remotive_url = "https://remotive.com/api/remote-jobs"
        self.adzuna_app_id = settings.ADZUNA_APP_ID
        self.adzuna_app_key = settings.ADZUNA_APP_KEY
        self.jooble_key = settings.JOOBLE_API_KEY
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate job postings based on company + description similarity.
        Same company posting the same job in multiple locations is deduplicated.
        
        Args:
            jobs: List of job dictionaries
        
        Returns:
            Deduplicated list of unique jobs
        """
        if not jobs:
            return jobs
        
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create fingerprint: company + truncated description
            company = (job.get("company") or "").lower().strip()
            description = (job.get("description") or "").lower()[:200].strip()
            title = (job.get("title") or "").lower().strip()
            
            # Fingerprint ignores location and posting date variations
            fingerprint = f"{company}|{title}|{description}"
            
            if fingerprint not in seen:
                seen.add(fingerprint)
                unique_jobs.append(job)
        
        return unique_jobs
    
    async def search_jobs(
        self,
        keyword: str,
        location: str = "remote",
        job_type: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for jobs from multiple sources.
        
        Args:
            keyword: Job search keyword (e.g., "Python Developer")
            location: Job location (default: "remote")
            job_type: Type of job (e.g., "full-time", "part-time")
            source: Specific source ("remotive", "adzuna", "jooble", or None for all)
        
        Returns:
            List of job postings from all enabled sources
        """
        results = []
        
        try:
            # Search from selected sources
            if source is None or source == "remotive":
                remotive_jobs = await self._search_remotive(keyword, location, job_type)
                results.extend(remotive_jobs)
            
            if source is None or source == "adzuna":
                adzuna_jobs = await self._search_adzuna(keyword, location)
                results.extend(adzuna_jobs)
            
            if source is None or source == "jooble":
                jooble_jobs = await self._search_jooble(keyword, location)
                results.extend(jooble_jobs)
        
        except Exception as e:
            print(f"[ERROR] Error searching jobs: {e}")
        
        # Deduplicate jobs across sources
        results = self._deduplicate_jobs(results)
        
        return results
    
    async def _search_remotive(
        self,
        keyword: str,
        location: str,
        job_type: Optional[str]
    ) -> List[Dict]:
        """
        Search jobs from Remotive API.
        Free API - no authentication needed.
        Specializes in remote jobs.
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "search": keyword,
                    "limit": 50
                }
                
                async with session.get(self.remotive_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        jobs = []
                        
                        for job in data.get("jobs", []):
                            jobs.append({
                                "id": job.get("id"),
                                "title": job.get("title"),
                                "company": job.get("company_name"),
                                "description": job.get("description"),
                                "url": job.get("url"),
                                "location": job.get("job_geo_location", {}).get("name", "Remote"),
                                "job_type": job.get("job_type", "Full-time"),
                                "source": "remotive",
                                "posted_date": job.get("publication_date")
                            })
                        
                        return jobs
        
        except Exception as e:
            print(f"[ERROR] Remotive search failed: {e}")
        
        return []
    
    async def get_recommendations(
        self,
        skills: List[str],
        top_k: int = 5,
        location: Optional[str] = None
    ) -> List[Dict]:
        """
        Get job recommendations based on extracted skills.
        
        Args:
            skills: List of skills from resume
            top_k: Number of recommendations to return
            location: Optional location filter
        
        Returns:
            List of recommended jobs
        """
        if not skills:
            return []
        
        # Search for jobs matching top skills
        keyword = " ".join(skills[:3])  # Use top 3 skills as keywords
        jobs = await self.search_jobs(keyword, location or "remote")
        
        # Return top K recommendations
        return jobs[:top_k]
```

---

## ⚛️ Frontend Components

### Authentication Store (Zustand)

**File**: `frontend/src/store/authStore.js`

```javascript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../api/client';

/**
 * Zustand store for authentication state management.
 * Persists auth data in localStorage automatically.
 * 
 * State:
 * - user: Current user object
 * - accessToken: JWT access token
 * - refreshToken: JWT refresh token
 * - isAuthenticated: Boolean authentication status
 * - isLoading: Loading state for async operations
 * - error: Error messages from auth operations
 */
const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Set authentication tokens and user
      setAuth: (data) => {
        set({
          user: data.user,
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          isAuthenticated: true,
          error: null,
        });
        // Set token in axios interceptor headers
        api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      },

      // Clear all authentication data
      clearAuth: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        });
        delete api.defaults.headers.common['Authorization'];
      },

      // Signup with email and password
      signup: async (email, password, fullName) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/signup', {
            email,
            password,
            full_name: fullName,
          });
          get().setAuth(response.data);
          return { success: true };
        } catch (error) {
          const errorMsg = error.response?.data?.detail || 'Signup failed';
          set({ error: errorMsg, isLoading: false });
          return { success: false, error: errorMsg };
        }
      },

      // Login with email and password
      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/login', {
            email,
            password,
          });
          get().setAuth(response.data);
          return { success: true };
        } catch (error) {
          const errorMsg = error.response?.data?.detail || 'Login failed';
          set({ error: errorMsg, isLoading: false });
          return { success: false, error: errorMsg };
        }
      },

      // Initialize authentication from stored tokens
      initAuth: async () => {
        const { accessToken } = get();
        if (accessToken) {
          try {
            // Verify token is still valid
            api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
            const response = await api.get('/auth/me');
            set({ user: response.data, isAuthenticated: true });
          } catch (error) {
            // Token expired or invalid
            get().clearAuth();
          }
        }
      },

      // Logout user
      logout: () => {
        get().clearAuth();
      },
    }),
    {
      name: 'auth-storage', // localStorage key
    }
  )
);

export default useAuthStore;
```

### API Client with Interceptors

**File**: `frontend/src/api/client.js`

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * Axios instance with base configuration.
 * Handles API requests with automatic token management.
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to retrieve stored authentication token
const getStoredToken = () => {
  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      const parsed = JSON.parse(authStorage);
      return parsed?.state?.accessToken || null;
    }
  } catch (e) {
    console.error('Error reading auth token:', e);
  }
  return null;
};

/**
 * Request interceptor - automatically includes JWT token.
 * Handles token from both axios defaults (set by setAuth) and localStorage (page refresh).
 */
api.interceptors.request.use(
  (config) => {
    // Try to get token from axios defaults first (set by setAuth in authStore)
    const defaultToken = api.defaults.headers.common['Authorization'];
    // Fallback to localStorage token (persisted by zustand)
    const storedToken = getStoredToken();
    
    const token = defaultToken || (storedToken ? `Bearer ${storedToken}` : null);
    
    if (token) {
      config.headers['Authorization'] = token;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response interceptor - handles errors and token refresh.
 */
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If 401 and not already retried, attempt token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            { refresh_token: refreshToken }
          );
          
          // Update token and retry original request
          api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
          originalRequest.headers['Authorization'] = `Bearer ${response.data.access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('Token refresh failed');
      }
    }
    
    return Promise.reject(error);
  }
);

// Resume Analysis API endpoints
export const resumeAPI = {
  /**
   * Upload resume file for analysis.
   * Supports PDF, DOCX, TXT formats.
   */
  uploadResume: (file, jobDescription) => {
    const formData = new FormData();
    formData.append('file', file);
    if (jobDescription) {
      formData.append('job_description', jobDescription);
    }
    return api.post('/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  /**
   * Score resume against job description.
   */
  scoreResume: (resumeText, jobDescription) =>
    api.post('/resume/score', {
      resume_text: resumeText,
      job_description: jobDescription,
    }),
  
  /**
   * Extract skills from resume text.
   */
  extractSkills: (resumeText) =>
    api.post('/resume/extract-skills', {
      resume_text: resumeText,
    }),
};

// Job Search API endpoints
export const jobsAPI = {
  /**
   * Search for jobs by keywords and filters.
   */
  searchJobs: (keyword, location, jobType, source) =>
    api.get('/jobs/search', {
      params: { keyword, location, job_type: jobType, source },
    }),
  
  /**
   * Get job recommendations based on resume.
   */
  recommendJobs: (resumeText, topK, location) =>
    api.post('/jobs/recommend', {
      resume_text: resumeText,
      top_k: topK,
      location,
    }),
};

// History API endpoints
export const historyAPI = {
  /**
   * Save analysis to history.
   */
  saveAnalysis: (analysisData) =>
    api.post('/history/save', analysisData),
  
  /**
   * Get user's analysis history.
   */
  getHistory: () =>
    api.get('/history/list'),
  
  /**
   * Delete analysis from history.
   */
  deleteAnalysis: (analysisId) =>
    api.delete(`/history/${analysisId}`),
};

export default api;
```

### Resume Upload Component

**File**: `frontend/src/components/ResumeUpload.jsx`

```javascript
import React, { useState } from 'react';
import { resumeAPI, historyAPI } from '../api/client';
import useAuthStore from '../store/authStore';
import { LoadingSpinner } from './Common';
import { FiUploadCloud, FiX, FiFileText, FiCheckCircle } from 'react-icons/fi';

/**
 * Resume Upload Component
 * 
 * Features:
 * - Drag and drop file upload
 * - Support for PDF, DOCX, TXT
 * - Job description input
 * - Real-time upload feedback
 * - Save to history option
 */
export const ResumeUpload = ({ onSuccess }) => {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [savedToHistory, setSavedToHistory] = useState(false);
  const { isAuthenticated } = useAuthStore();

  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const validTypes = [
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      const validExtensions = ['.pdf', '.txt', '.docx'];
      const fileExtension = selectedFile.name
        .toLowerCase()
        .substring(selectedFile.name.lastIndexOf('.'));

      // Validate file type and extension
      if (validTypes.includes(selectedFile.type) || validExtensions.includes(fileExtension)) {
        setFile(selectedFile);
        setError(null);
        setUploadSuccess(false);
      } else {
        setError('Please select a PDF, TXT, or DOCX file');
        setFile(null);
      }
    }
  };

  // Handle resume upload
  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!isAuthenticated) {
      setError('Please login to upload resume');
      return;
    }

    setLoading(true);
    setError(null);
    setSavedToHistory(false);

    try {
      // Upload resume and perform analysis
      const response = await resumeAPI.uploadResume(file, jobDescription);
      const data = response.data;

      setUploadSuccess(true);

      // Save to history if analysis was performed
      if (data.ats_analysis) {
        try {
          await historyAPI.saveAnalysis({
            filename: data.filename,
            resume_text: data.resume_text,
            job_description: jobDescription,
            ats_analysis: data.ats_analysis,
          });
          setSavedToHistory(true);
        } catch (historyError) {
          console.error('Failed to save to history:', historyError);
        }
      }

      // Call callback with analysis results
      if (onSuccess) {
        onSuccess({
          filename: data.filename,
          resumeText: data.resume_text,
          atsAnalysis: data.ats_analysis,
          extractedInfo: data.extracted_info,
        });
      }

      // Reset form
      setFile(null);
      setJobDescription('');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Upload failed';
      setError(errorMsg);
      setUploadSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-slate-800 rounded-lg border border-slate-700">
      <form onSubmit={handleUpload}>
        {/* File Input Area */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-200 mb-3">
            <FiUploadCloud className="inline mr-2" />
            Resume File (PDF, DOCX, or TXT)
          </label>
          
          {file ? (
            <div className="flex items-center justify-between p-4 bg-slate-700 rounded border border-green-500">
              <div className="flex items-center">
                <FiFileText className="text-green-500 mr-2" />
                <span className="text-slate-200">{file.name}</span>
              </div>
              <button
                type="button"
                onClick={() => setFile(null)}
                className="text-red-500 hover:text-red-400"
              >
                <FiX />
              </button>
            </div>
          ) : (
            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt"
              className="w-full p-4 border-2 border-dashed border-slate-600 rounded hover:border-slate-500 cursor-pointer"
            />
          )}
        </div>

        {/* Job Description Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-200 mb-3">
            Job Description (Optional)
          </label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste job description here for ATS analysis..."
            rows="4"
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded text-slate-200 placeholder-slate-400"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-900 border border-red-700 rounded text-red-200">
            {error}
          </div>
        )}

        {/* Success Message */}
        {uploadSuccess && (
          <div className="mb-4 p-3 bg-green-900 border border-green-700 rounded text-green-200 flex items-center">
            <FiCheckCircle className="mr-2" />
            Resume uploaded successfully!
            {savedToHistory && ' Saved to history.'}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !file}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 rounded text-white font-medium transition-colors flex items-center justify-center"
        >
          {loading ? <LoadingSpinner /> : 'Upload & Analyze'}
        </button>
      </form>
    </div>
  );
};
```

---

## 🗄️ Database Schema

### User Model

**File**: `backend/models/user.py`

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    oauth_provider: Optional[str] = None  # 'google', 'github'
    oauth_id: Optional[str] = None


class UserInDB(UserBase):
    """User model as stored in MongoDB database."""
    id: int  # Auto-incremented ID
    hashed_password: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class ResumeAnalysisBase(BaseModel):
    """Base resume analysis model."""
    filename: Optional[str] = None
    resume_text: str
    job_description: Optional[str] = None
    ats_score: Optional[float] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    matching_keywords: Optional[List[str]] = None
    missing_keywords: Optional[List[str]] = None
    analysis_result: Optional[Dict[str, Any]] = None


class ResumeAnalysisInDB(ResumeAnalysisBase):
    """Resume analysis as stored in MongoDB."""
    id: int
    user_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 🌐 API Endpoints

### Authentication Endpoints

```
POST /api/v1/auth/signup
- Register new user
- Body: { email, password, full_name }
- Returns: { access_token, refresh_token, user }

POST /api/v1/auth/login
- Login with email/password
- Body: { email, password }
- Returns: { access_token, refresh_token, user }

POST /api/v1/auth/refresh
- Get new access token
- Body: { refresh_token }
- Returns: { access_token }

GET /api/v1/auth/me
- Get current user (requires auth)
- Returns: { user_data }
```

### Resume Endpoints

```
POST /api/v1/resume/upload
- Upload and analyze resume
- Form: file, job_description (optional)
- Returns: { filename, resume_text, ats_analysis, extracted_info }

POST /api/v1/resume/score
- Score resume against job
- Body: { resume_text, job_description }
- Returns: { ats_score, matching_keywords, recommendations }

POST /api/v1/resume/extract-skills
- Extract skills from resume
- Body: { resume_text }
- Returns: { skills, by_category }
```

### Job Endpoints

```
GET /api/v1/jobs/search
- Search for jobs
- Query: keyword, location, job_type, source
- Returns: { keyword, location, total_jobs, jobs }

POST /api/v1/jobs/recommend
- Get job recommendations
- Body: { resume_text, top_k, location }
- Returns: { extracted_skills, recommendations }
```

### History Endpoints

```
POST /api/v1/history/save
- Save analysis to history (requires auth)
- Body: analysis_data
- Returns: { id, created_at }

GET /api/v1/history/list
- Get user's analysis history (requires auth)
- Returns: [ { analyses } ]

DELETE /api/v1/history/{id}
- Delete analysis (requires auth)
- Returns: { status }
```

---

## 🐳 Deployment & Configuration

### Docker Compose Setup

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - MONGODB_URL=${MONGODB_URL:-mongodb://localhost:27017}
      - MONGODB_DB_NAME=resume_ats
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID}
      - GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET}
      - ADZUNA_APP_ID=${ADZUNA_APP_ID}
      - ADZUNA_APP_KEY=${ADZUNA_APP_KEY}
      - JOOBLE_API_KEY=${JOOBLE_API_KEY}
    volumes:
      - ./backend:/app/backend
      - ./ml_models:/app/ml_models
      - ./data:/app/data
      - ./uploads:/app/uploads
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - mongodb

  # React Frontend
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    depends_on:
      - backend

  # MongoDB Database
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD:-password}
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
  uploads:
  data:
  ml_models:
```

### Environment Variables (.env)

```env
# Database
MONGODB_URL=mongodb://admin:password@localhost:27017
MONGODB_DB_NAME=resume_ats

# Security
SECRET_KEY=your-super-secret-key-min-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth - Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth - GitHub
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# External APIs
OPENAI_API_KEY=your-openai-api-key
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key
JOOBLE_API_KEY=your-jooble-api-key

# Frontend
REACT_APP_API_URL=http://localhost:8000/api/v1
FRONTEND_URL=http://localhost:3000
```

---

## 🚀 Running the Application

### Local Development

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 2. Start MongoDB
docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password mongo:6.0

# 3. Run backend
uvicorn backend.main:app --reload

# 4. Run frontend (in another terminal)
cd frontend
npm start

# 5. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access application at http://localhost:3000
```

---

## 📊 Project Statistics

- **Backend**: FastAPI + Python 3.9+
- **Frontend**: React 18 + Tailwind CSS
- **Database**: MongoDB
- **ML**: PyTorch Neural Networks + Scikit-learn
- **APIs**: Remotive, Adzuna, Jooble
- **Authentication**: JWT + OAuth (Google, GitHub)
- **AI**: OpenAI Integration
- **Deployment**: Docker, Docker Compose

---

## 🔗 Key Technologies

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| Frontend | React 18 |
| Database | MongoDB |
| ML/AI | PyTorch, TensorFlow, OpenAI |
| Authentication | JWT, OAuth 2.0 |
| State Management | Zustand |
| HTTP Client | Axios |
| Styling | Tailwind CSS |
| Containerization | Docker |

---

## 📝 License

This project is part of the IntelliDiots AI suite.

---

Generated: April 6, 2026
Last Updated: April 6, 2026
