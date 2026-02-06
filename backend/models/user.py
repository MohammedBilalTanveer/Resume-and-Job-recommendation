from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    oauth_provider: Optional[str] = None  # 'google', 'github', or None for email
    oauth_id: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: Optional[str] = None  # Nullable for OAuth users


class UserInDB(UserBase):
    """User model as stored in database."""
    id: int
    hashed_password: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response model (excludes sensitive data)."""
    id: int
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    oauth_provider: Optional[str] = None
    is_verified: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


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


class ResumeAnalysisCreate(ResumeAnalysisBase):
    """Model for creating a new resume analysis."""
    pass


class ResumeAnalysisInDB(ResumeAnalysisBase):
    """Resume analysis model as stored in database."""
    id: int
    user_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class ResumeAnalysisResponse(ResumeAnalysisBase):
    """Resume analysis response model."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Helper functions to convert between MongoDB documents and Pydantic models
def user_from_doc(doc: dict) -> UserInDB:
    """Convert MongoDB document to UserInDB model."""
    if doc is None:
        return None
    return UserInDB(
        id=doc.get("id"),
        email=doc.get("email"),
        full_name=doc.get("full_name"),
        avatar_url=doc.get("avatar_url"),
        oauth_provider=doc.get("oauth_provider"),
        oauth_id=doc.get("oauth_id"),
        hashed_password=doc.get("hashed_password"),
        is_active=doc.get("is_active", True),
        is_verified=doc.get("is_verified", False),
        created_at=doc.get("created_at", datetime.utcnow()),
        updated_at=doc.get("updated_at", datetime.utcnow()),
        last_login=doc.get("last_login")
    )


def user_to_doc(user: UserInDB) -> dict:
    """Convert UserInDB model to MongoDB document."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "oauth_provider": user.oauth_provider,
        "oauth_id": user.oauth_id,
        "hashed_password": user.hashed_password,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login
    }


def analysis_from_doc(doc: dict) -> ResumeAnalysisInDB:
    """Convert MongoDB document to ResumeAnalysisInDB model."""
    if doc is None:
        return None
    return ResumeAnalysisInDB(
        id=doc.get("id"),
        user_id=doc.get("user_id"),
        filename=doc.get("filename"),
        resume_text=doc.get("resume_text"),
        job_description=doc.get("job_description"),
        ats_score=doc.get("ats_score"),
        skills=doc.get("skills"),
        experience_years=doc.get("experience_years"),
        education=doc.get("education"),
        certifications=doc.get("certifications"),
        matching_keywords=doc.get("matching_keywords"),
        missing_keywords=doc.get("missing_keywords"),
        analysis_result=doc.get("analysis_result"),
        created_at=doc.get("created_at", datetime.utcnow())
    )


def analysis_to_doc(analysis: ResumeAnalysisInDB) -> dict:
    """Convert ResumeAnalysisInDB model to MongoDB document."""
    return {
        "id": analysis.id,
        "user_id": analysis.user_id,
        "filename": analysis.filename,
        "resume_text": analysis.resume_text,
        "job_description": analysis.job_description,
        "ats_score": analysis.ats_score,
        "skills": analysis.skills,
        "experience_years": analysis.experience_years,
        "education": analysis.education,
        "certifications": analysis.certifications,
        "matching_keywords": analysis.matching_keywords,
        "missing_keywords": analysis.missing_keywords,
        "analysis_result": analysis.analysis_result,
        "created_at": analysis.created_at
    }

