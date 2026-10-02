from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body
from fastapi.concurrency import run_in_threadpool
from typing import Optional
from pydantic import BaseModel
import os
import sys
import tempfile
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.utils.pdf_parser import parse_resume
from backend.utils.advanced_ats_scorer import advanced_ats_scorer

router = APIRouter()


class ScoreRequest(BaseModel):
    resume_text: str
    job_description: str


class ExtractRequest(BaseModel):
    resume_text: str


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...), 
    job_description: Optional[str] = Form(None)
):
    """
    Upload and analyze a resume with comprehensive ATS scoring.
    Returns: Resume text, extracted data, detailed ATS analysis (if job description provided)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        contents = await file.read()
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # Parse from a uniquely named temp file that is deleted right away:
        # resumes are personal data and shouldn't be kept on the server, and
        # unique names stop concurrent uploads of "resume.pdf" clobbering each other.
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        suffix = Path(file.filename).suffix.lower()
        fd, file_path = tempfile.mkstemp(suffix=suffix, dir=settings.UPLOAD_FOLDER)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(contents)
            resume_text = await run_in_threadpool(parse_resume, file_path)
        finally:
            try:
                os.remove(file_path)
            except OSError:
                pass
        
        if not resume_text or not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not read any text from this file. If it's a scanned/image PDF, "
                       "export it as a text-based PDF or upload a DOCX."
            )
        
        # Basic response structure
        response = {
            "filename": file.filename,
            "resume_text": resume_text,
            "ats_analysis": None
        }
        
        # Perform comprehensive ATS analysis if job description provided
        if job_description and job_description.strip():
            analysis = await run_in_threadpool(
                advanced_ats_scorer.comprehensive_analysis, resume_text, job_description)
            response["ats_analysis"] = analysis
        else:
            # Resume-only analysis without job comparison
            response["extracted_info"] = await run_in_threadpool(advanced_ats_scorer.resume_insights, resume_text)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score")
async def score_resume(request: ScoreRequest):
    """
    Calculate comprehensive ATS score for given resume and job description.
    Returns detailed analysis with recommendations.
    """
    try:
        if not request.resume_text or not request.job_description:
            raise HTTPException(
                status_code=400,
                detail="Both resume_text and job_description are required"
            )
        
        analysis = await run_in_threadpool(
            advanced_ats_scorer.comprehensive_analysis,
            request.resume_text,
            request.job_description
        )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Score calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-skills")
async def extract_skills(request: ExtractRequest):
    """
    Extract skills and information from resume text.
    """
    try:
        return await run_in_threadpool(advanced_ats_scorer.resume_insights, request.resume_text)
    except Exception as e:
        print(f"[ERROR] Skill extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-score")
async def get_sample_score():
    """
    Get a sample ATS score calculation with example data.
    """
    sample_resume = """
    Mohammed Bilal - Senior Software Engineer
    Email: bilal@email.com | Phone: 555-123-4567 | LinkedIn: linkedin.com/in/bilal
    
    SUMMARY
    Senior Software Engineer with 5+ years of experience in Python, JavaScript, and cloud technologies.
    Passionate about building scalable applications and leading engineering teams.
    
    EXPERIENCE
    Senior Software Engineer | Tech Company | 2020-Present
    - Developed microservices architecture using Python and FastAPI, improving system performance by 40%
    - Led team of 5 engineers in delivering cloud-native applications on AWS
    - Implemented CI/CD pipelines using Jenkins and GitHub Actions
    - Reduced deployment time by 60% through automation
    
    Software Engineer | Startup Inc | 2018-2020
    - Built React-based dashboards for data visualization
    - Designed and implemented RESTful APIs serving 100K+ daily requests
    - Optimized database queries resulting in 50% faster response times
    
    SKILLS
    Programming: Python, JavaScript, TypeScript, SQL
    Frameworks: React, FastAPI, Django, Node.js
    Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
    Tools: Git, Jenkins, PostgreSQL, MongoDB, Redis
    
    EDUCATION
    B.Tech in Computer Science | University of Technology | 2018
    
    CERTIFICATIONS
    - AWS Certified Solutions Architect
    - Kubernetes Administrator (CKA)
    """
    
    sample_job = """
    Senior Software Engineer - Full Stack
    
    About the Role:
    We're looking for a Senior Software Engineer to join our growing team.
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in Python and JavaScript
    - Experience with React or similar frontend frameworks
    - Experience with cloud platforms (AWS preferred)
    - Experience with containerization (Docker, Kubernetes)
    - Strong understanding of microservices architecture
    - Experience with CI/CD pipelines
    
    Nice to have:
    - Experience with FastAPI or Django
    - Machine Learning experience
    - Team leadership experience
    """
    
    analysis = await run_in_threadpool(advanced_ats_scorer.comprehensive_analysis, sample_resume, sample_job)
    
    return {
        "sample_resume": sample_resume,
        "sample_job_description": sample_job,
        "ats_analysis": analysis
    }


@router.post("/quick-score")
async def quick_score(
    resume_text: str = Body(...),
    job_description: str = Body(...)
):
    """
    Quick ATS score calculation (simplified response).
    """
    try:
        analysis = await run_in_threadpool(advanced_ats_scorer.comprehensive_analysis, resume_text, job_description)
        
        return {
            "score": analysis["overall_score"],
            "score_percentage": analysis["score_percentage"],
            "grade": analysis["grade"],
            "matched_skills": analysis["skills_analysis"]["matched_skills"][:10],
            "missing_skills": analysis["skills_analysis"]["missing_skills"][:10],
            "top_recommendations": analysis["ai_recommendations"][:3]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
