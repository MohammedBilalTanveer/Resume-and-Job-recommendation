from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body
from typing import Optional
from pydantic import BaseModel
import os
import sys
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
        
        # Save uploaded file
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
        
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Parse resume
        resume_text = parse_resume(file_path)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not parse resume")
        
        # Basic response structure
        response = {
            "filename": file.filename,
            "resume_text": resume_text,
            "ats_analysis": None
        }
        
        # Perform comprehensive ATS analysis if job description provided
        if job_description and job_description.strip():
            analysis = advanced_ats_scorer.comprehensive_analysis(resume_text, job_description)
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
        
        analysis = advanced_ats_scorer.comprehensive_analysis(
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
        resume_lower = request.resume_text.lower()
        skills = advanced_ats_scorer._extract_all_skills(resume_lower)
        
        return {
            "skills": skills["all"],
            "skills_by_category": skills["by_category"],
            "experience_years": advanced_ats_scorer._extract_experience_years(resume_lower),
            "education": advanced_ats_scorer._extract_education(resume_lower),
            "contact_info": advanced_ats_scorer._extract_contact_info(request.resume_text),
            "sections": advanced_ats_scorer._analyze_resume_structure(request.resume_text),
            "action_verbs": advanced_ats_scorer._extract_action_verbs(request.resume_text)
        }
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
    
    analysis = advanced_ats_scorer.comprehensive_analysis(sample_resume, sample_job)
    
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
        analysis = advanced_ats_scorer.comprehensive_analysis(resume_text, job_description)
        
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
