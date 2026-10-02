"""
Compatibility wrapper around the advanced ATS engine.

The jobs routes use this simpler interface; delegating keeps resume scoring
and job matching consistent (same skill taxonomy, parsing and scoring).
"""

from typing import Dict

from backend.utils.advanced_ats_scorer import advanced_ats_scorer


class ATSScorer:
    """ATS score calculator - thin facade over AdvancedATSScorer."""

    def __init__(self):
        self.engine = advanced_ats_scorer

    def extract_resume_info(self, resume_text: str) -> Dict:
        """
        Extract structured information from a resume.
        Returns: skills (ranked by evidence), experience, education, certifications, contact info, etc.
        """
        profile = self.engine.parse_resume(resume_text)
        return {
            "skills": self.engine._rank_resume_skills(profile),
            "experience_years": profile["experience_years"],
            "experience_years_exact": profile["experience_years_exact"],
            "education": profile["education"],
            "education_level": profile["education_level"],
            "certifications": profile["certifications"],
            "contact_info": profile["contact"],
            "current_title": profile["title"],
            "profile": profile,
            "raw_text": resume_text,
        }

    def calculate_ats_score(self, resume_text: str, job_description: str) -> Dict:
        """
        Calculate the ATS score of a resume against a job description.

        Returns:
            {"score": 0-1, "score_percentage", "matching_keywords", "missing_keywords",
             "breakdown", "method"}
        """
        analysis = self.engine.comprehensive_analysis(resume_text, job_description)
        breakdown = analysis["score_breakdown"]
        return {
            "score": analysis["overall_score"],
            "score_percentage": analysis["score_percentage"],
            "grade": analysis["grade"],
            "matching_keywords": analysis["skills_analysis"]["matched_skills"],
            "missing_keywords": analysis["skills_analysis"]["missing_skills"],
            "breakdown": {
                "skill_match": breakdown["skill_match"],
                "content_similarity": breakdown["content_similarity"],
                "keyword_score": breakdown["keyword_match"],
                "experience_match": breakdown["experience_match"],
                "ml_model_score": None,
            },
            "method": analysis["method"],
        }
