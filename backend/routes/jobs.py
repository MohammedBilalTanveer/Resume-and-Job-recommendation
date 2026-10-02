from fastapi import APIRouter, HTTPException, Query, Header
from fastapi.concurrency import run_in_threadpool
from typing import Optional, List
from pydantic import BaseModel
import asyncio
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import settings
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
    Infers target roles and core skills from the resume, searches several
    queries across job sources, and ranks results by actual fit.
    """
    try:
        if not request.resume_text or not request.resume_text.strip():
            raise HTTPException(status_code=400, detail="resume_text is required")

        resume_data = await run_in_threadpool(ats_scorer.extract_resume_info, request.resume_text)
        skills = resume_data.get("skills", [])
        profile = resume_data["profile"]

        if not skills and not profile.get("title"):
            raise HTTPException(
                status_code=400,
                detail="Could not identify skills or a job title in the resume. "
                       "Make sure it has a Skills section and readable (not scanned) text."
            )

        top_k = max(1, min(request.top_k or 5, 50))
        recommendations = await job_service.get_recommendations(
            skills=skills,
            top_k=top_k,
            location=request.location,
            profile=profile,
        )

        return {
            "extracted_skills": skills[:20],
            "target_roles": job_service.infer_target_roles(profile, skills),
            "total_recommendations": len(recommendations),
            "jobs": recommendations
        }

    except HTTPException:
        raise
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
            target_job_desc = await job_service.get_job_description(request.job_id)
            if not target_job_desc:
                raise HTTPException(
                    status_code=404,
                    detail="Job not found - search or get recommendations first, or pass job_description"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either job_id or job_description is required"
            )

        ats_result = await run_in_threadpool(ats_scorer.calculate_ats_score, request.resume_text, target_job_desc)

        return {
            "job_id": request.job_id,
            "match_score": ats_result["score"],
            "matching_keywords": ats_result["matching_keywords"],
            "missing_keywords": ats_result["missing_keywords"],
            "match_percentage": round(ats_result["score"] * 100, 2),
            "grade": ats_result["grade"],
            "breakdown": ats_result["breakdown"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _check_refresh_token(token: Optional[str]):
    expected = settings.JOBS_REFRESH_TOKEN
    if not expected:
        raise HTTPException(status_code=503, detail="Job refresh is disabled (JOBS_REFRESH_TOKEN not set)")
    if not token or not secrets.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Invalid refresh token")


_refresh_tasks = set()


@router.post("/refresh", status_code=202)
async def refresh_job_catalog(
    x_refresh_token: Optional[str] = Header(None),
    max_calls: Optional[int] = Query(None, ge=0, le=250, description="Cap Adzuna calls for this run"),
):
    """
    Start today's rotating fetch of jobs into the catalog (runs in the background).
    Called once a day by the GitHub Actions workflow; needs the X-Refresh-Token header.
    """
    _check_refresh_token(x_refresh_token)
    if job_service.refresh_state.get("running"):
        return {"status": "already_running", "progress": job_service.refresh_state}
    task = asyncio.create_task(job_service.run_refresh(max_adzuna_calls=max_calls))
    _refresh_tasks.add(task)  # keep a reference so the task isn't garbage-collected
    task.add_done_callback(_refresh_tasks.discard)
    return {"status": "started"}


@router.get("/refresh/status")
async def refresh_job_catalog_status(x_refresh_token: Optional[str] = Header(None)):
    """Progress of the current/last refresh, catalog size and API quota usage."""
    _check_refresh_token(x_refresh_token)
    return await job_service.refresh_status()


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
