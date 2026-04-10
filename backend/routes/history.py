from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from backend.database import get_analyses_collection, get_next_sequence
from backend.models.user import UserInDB, analysis_from_doc
from backend.utils.auth import get_current_user

router = APIRouter()


# India Standard Time timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


# Request/Response Models
class SaveAnalysisRequest(BaseModel):
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
    analysis_result: Optional[dict] = None


class AnalysisResponse(BaseModel):
    id: int
    filename: Optional[str]
    resume_text: str
    job_description: Optional[str]
    ats_score: Optional[float]
    skills: Optional[List[str]]
    experience_years: Optional[int]
    education: Optional[List[str]]
    certifications: Optional[List[str]]
    matching_keywords: Optional[List[str]]
    missing_keywords: Optional[List[str]]
    analysis_result: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/save", response_model=AnalysisResponse)
async def save_analysis(
    data: SaveAnalysisRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Save a resume analysis for the current user."""
    analyses = get_analyses_collection()
    
    # Get next analysis ID
    analysis_id = await get_next_sequence("resume_analyses")
    now = datetime.now(IST)  # Use India Standard Time
    
    analysis_doc = {
        "id": analysis_id,
        "user_id": current_user.id,
        "filename": data.filename,
        "resume_text": data.resume_text,
        "job_description": data.job_description,
        "ats_score": data.ats_score,
        "skills": data.skills,
        "experience_years": data.experience_years,
        "education": data.education,
        "certifications": data.certifications,
        "matching_keywords": data.matching_keywords,
        "missing_keywords": data.missing_keywords,
        "analysis_result": data.analysis_result,
        "created_at": now
    }
    
    await analyses.insert_one(analysis_doc)
    
    return AnalysisResponse(
        id=analysis_id,
        filename=data.filename,
        resume_text=data.resume_text,
        job_description=data.job_description,
        ats_score=data.ats_score,
        skills=data.skills,
        experience_years=data.experience_years,
        education=data.education,
        certifications=data.certifications,
        matching_keywords=data.matching_keywords,
        missing_keywords=data.missing_keywords,
        analysis_result=data.analysis_result,
        created_at=now
    )


@router.get("/list", response_model=List[AnalysisResponse])
async def list_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get list of resume analyses for the current user."""
    analyses = get_analyses_collection()
    
    cursor = analyses.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1).skip(skip).limit(limit)
    
    results = []
    async for doc in cursor:
        analysis = analysis_from_doc(doc)
        results.append(AnalysisResponse(
            id=analysis.id,
            filename=analysis.filename,
            resume_text=analysis.resume_text,
            job_description=analysis.job_description,
            ats_score=analysis.ats_score,
            skills=analysis.skills,
            experience_years=analysis.experience_years,
            education=analysis.education,
            certifications=analysis.certifications,
            matching_keywords=analysis.matching_keywords,
            missing_keywords=analysis.missing_keywords,
            analysis_result=analysis.analysis_result,
            created_at=analysis.created_at
        ))
    
    return results


@router.get("/latest", response_model=Optional[AnalysisResponse])
async def get_latest_analysis(
    current_user: UserInDB = Depends(get_current_user)
):
    """Get the most recent resume analysis for the current user."""
    analyses = get_analyses_collection()
    
    doc = await analyses.find_one(
        {"user_id": current_user.id},
        sort=[("created_at", -1)]
    )
    
    if not doc:
        return None
    
    analysis = analysis_from_doc(doc)
    return AnalysisResponse(
        id=analysis.id,
        filename=analysis.filename,
        resume_text=analysis.resume_text,
        job_description=analysis.job_description,
        ats_score=analysis.ats_score,
        skills=analysis.skills,
        experience_years=analysis.experience_years,
        education=analysis.education,
        certifications=analysis.certifications,
        matching_keywords=analysis.matching_keywords,
        missing_keywords=analysis.missing_keywords,
        analysis_result=analysis.analysis_result,
        created_at=analysis.created_at
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific resume analysis by ID."""
    analyses = get_analyses_collection()
    
    doc = await analyses.find_one({
        "id": analysis_id,
        "user_id": current_user.id
    })
    
    if not doc:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_from_doc(doc)
    return AnalysisResponse(
        id=analysis.id,
        filename=analysis.filename,
        resume_text=analysis.resume_text,
        job_description=analysis.job_description,
        ats_score=analysis.ats_score,
        skills=analysis.skills,
        experience_years=analysis.experience_years,
        education=analysis.education,
        certifications=analysis.certifications,
        matching_keywords=analysis.matching_keywords,
        missing_keywords=analysis.missing_keywords,
        analysis_result=analysis.analysis_result,
        created_at=analysis.created_at
    )


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete a resume analysis."""
    analyses = get_analyses_collection()
    
    result = await analyses.delete_one({
        "id": analysis_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {"message": "Analysis deleted successfully"}


@router.get("/count/total")
async def get_analysis_count(
    current_user: UserInDB = Depends(get_current_user)
):
    """Get total count of resume analyses for the current user."""
    analyses = get_analyses_collection()
    
    count = await analyses.count_documents({"user_id": current_user.id})
    
    return {"count": count}

