from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.job_service import JobService
from backend.utils.ats_scorer import ATSScorer

router = APIRouter()
job_service = JobService()
ats_scorer = ATSScorer()

# Pydantic models for request bodies
class RecommendJobsRequest(BaseModel):
    resume_text: str
    top_k: int = 5
    location: Optional[str] = None

class MatchResumeRequest(BaseModel):
    resume_text: str
    job_id: Optional[str] = None
    job_description: Optional[str] = None

@router.get("/search")
async def search_jobs(
    keyword: str,
    location: Optional[str] = "remote",
    job_type: Optional[str] = None,
    source: Optional[str] = None
):
    """
    Search for jobs using multiple job APIs.
    Sources: remotive, adzuna, jooble
    """
    try:
        results = await job_service.search_jobs(
            keyword=keyword,
            location=location,
            job_type=job_type,
            source=source
        )
        return {
            "keyword": keyword,
            "location": location,
            "total_jobs": len(results),
            "jobs": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommend")
async def recommend_jobs(request: RecommendJobsRequest):
    """
    Get job recommendations based on resume content.
    Uses extracted skills to find matching jobs.
    """
    try:
        if not request.resume_text:
            raise HTTPException(status_code=400, detail="resume_text is required")
        
        # Extract skills from resume
        resume_data = ats_scorer.extract_resume_info(request.resume_text)
        skills = resume_data.get("skills", [])
        
        if not skills:
            raise HTTPException(status_code=400, detail="Could not extract skills from resume")
        
        # Search for jobs based on extracted skills
        recommendations = await job_service.get_recommendations(
            skills=skills,
            top_k=request.top_k,
            location=request.location
        )
        
        return {
            "extracted_skills": skills,
            "total_recommendations": len(recommendations),
            "jobs": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match-resume-to-job")
async def match_resume_to_job(request: MatchResumeRequest):
    """
    Calculate match score between resume and specific job.
    """
    try:
        if request.job_id and request.job_description:
            raise HTTPException(
                status_code=400,
                detail="Provide either job_id or job_description, not both"
            )
        
        if request.job_description:
            target_job_desc = request.job_description
        elif request.job_id:
            # Fetch job description from API
            target_job_desc = await job_service.get_job_description(request.job_id)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either job_id or job_description is required"
            )
        
        # Calculate ATS score
        ats_result = ats_scorer.calculate_ats_score(request.resume_text, target_job_desc)
        
        return {
            "job_id": request.job_id,
            "match_score": ats_result["score"],
            "matching_keywords": ats_result["matching_keywords"],
            "missing_keywords": ats_result["missing_keywords"],
            "match_percentage": round(ats_result["score"] * 100, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending")
async def get_trending_jobs(
    limit: int = Query(10, ge=1, le=50),
    location: Optional[str] = "remote"
):
    """
    Get trending jobs from all sources.
    """
    try:
        trending = await job_service.get_trending_jobs(limit=limit, location=location)
        return {
            "limit": limit,
            "location": location,
            "jobs": trending
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skills-demand")
async def get_skills_demand():
    """
    Get most in-demand skills from job postings.
    """
    try:
        skills_data = await job_service.analyze_skills_demand()
        return skills_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
