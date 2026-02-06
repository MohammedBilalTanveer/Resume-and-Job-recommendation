import aiohttp
import asyncio
from typing import List, Optional, Dict
from datetime import datetime
from backend.config import settings

class JobService:
    """
    Service to integrate multiple job APIs for job search and recommendations.
    """
    
    def __init__(self):
        self.remotive_url = "https://remotive.com/api/remote-jobs"
        self.adzuna_app_id = settings.ADZUNA_APP_ID
        self.adzuna_app_key = settings.ADZUNA_APP_KEY
        self.jooble_key = settings.JOOBLE_API_KEY
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate job postings based on company + description similarity.
        Same company posting the same job in multiple locations will be deduplicated.
        """
        if not jobs:
            return jobs
        
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a fingerprint based on company + first 200 chars of description
            company = (job.get("company") or "").lower().strip()
            description = (job.get("description") or "").lower()[:200].strip()
            title = (job.get("title") or "").lower().strip()
            
            # Fingerprint: company + truncated description (ignores location variations)
            fingerprint = f"{company}|{description}"
            
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
        """
        results = []
        
        try:
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
            print(f"Error searching jobs: {e}")
        
        # Deduplicate jobs (same company posting same job to multiple locations)
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
                                "id": str(job.get("id")),
                                "title": job.get("title"),
                                "company": job.get("company_name"),
                                "location": job.get("candidate_required_location", location),
                                "description": job.get("description"),
                                "url": job.get("url"),
                                "type": job.get("job_type", "Full-time"),
                                "posted_date": job.get("publication_date"),
                                "source": "remotive",
                                "salary": job.get("salary", "Not specified")
                            })
                        
                        return jobs
                    else:
                        print(f"Remotive API error: {resp.status}")
                        return []
        
        except Exception as e:
            print(f"Error searching Remotive: {e}")
            return []
    
    async def _search_adzuna(self, keyword: str, location: str) -> List[Dict]:
        """
        Search jobs from Adzuna API.
        Requires API credentials.
        """
        try:
            if not self.adzuna_app_id or not self.adzuna_app_key:
                return []
            
            base_url = "https://api.adzuna.com/v1/api/jobs"
            
            async with aiohttp.ClientSession() as session:
                params = {
                    "app_id": self.adzuna_app_id,
                    "app_key": self.adzuna_app_key,
                    "what": keyword,
                    "where": location if location != "remote" else "",
                    "results_per_page": 50
                }
                
                # Get country code for location (simplified)
                country_code = "us"  # Default to US for better results
                url = f"{base_url}/{country_code}/search/1"
                
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        jobs = []
                        
                        for job in data.get("results", []):
                            jobs.append({
                                "id": job.get("id"),
                                "title": job.get("title"),
                                "company": job.get("company", {}).get("display_name"),
                                "location": job.get("location", {}).get("display_name"),
                                "description": job.get("description"),
                                "url": job.get("redirect_url"),
                                "type": "Full-time",
                                "posted_date": job.get("created"),
                                "source": "adzuna",
                                "salary": job.get("salary_min", "Not specified")
                            })
                        
                        return jobs
                    else:
                        return []
        
        except Exception as e:
            print(f"Error searching Adzuna: {e}")
            return []
    
    async def _search_jooble(self, keyword: str, location: str) -> List[Dict]:
        """
        Search jobs from Jooble API.
        Requires API key.
        """
        try:
            if not self.jooble_key:
                return []
            
            # Jooble API URL with API key in path
            url = f"https://jooble.org/api/{self.jooble_key}"
            
            payload = {
                "keywords": keyword,
                "location": location if location != "remote" else ""
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        jobs = []
                        
                        for job in data.get("jobs", []):
                            jobs.append({
                                "id": str(job.get("id")),
                                "title": job.get("title"),
                                "company": job.get("company"),
                                "location": job.get("location"),
                                "description": job.get("snippet"),
                                "url": job.get("link"),
                                "type": job.get("type", "Full-time"),
                                "posted_date": job.get("updated"),
                                "source": "jooble",
                                "salary": job.get("salary", "Not specified")
                            })
                        
                        return jobs
                    else:
                        print(f"Jooble API error: {resp.status}")
                        return []
        
        except Exception as e:
            print(f"Error searching Jooble: {e}")
            return []
    
    async def get_recommendations(
        self,
        skills: List[str],
        top_k: int = 5,
        location: Optional[str] = None
    ) -> List[Dict]:
        """
        Get job recommendations based on skills.
        """
        try:
            # Search for jobs based on primary skill
            if not skills:
                return []
            
            primary_skill = skills[0]
            jobs = await self.search_jobs(
                keyword=primary_skill,
                location=location or "remote"
            )
            
            # Sort by relevance (jobs matching more skills appear first)
            def skill_match_score(job):
                desc = (job.get("description", "") + job.get("title", "")).lower()
                matches = sum(1 for skill in skills if skill.lower() in desc)
                return matches
            
            jobs.sort(key=skill_match_score, reverse=True)
            
            return jobs[:top_k]
        
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    async def get_job_description(self, job_id: str) -> str:
        """
        Get full job description by job ID.
        """
        # This would fetch the full description from the job
        return "Senior Software Engineer role with focus on backend development."
    
    async def get_trending_jobs(self, limit: int = 10, location: str = "remote") -> List[Dict]:
        """
        Get trending jobs.
        """
        try:
            trending_keywords = [
                "Python", "React", "Machine Learning",
                "AWS", "DevOps", "Data Science"
            ]
            
            all_jobs = []
            for keyword in trending_keywords:
                jobs = await self.search_jobs(keyword, location)
                all_jobs.extend(jobs)
            
            # Use deduplication method (handles same job posted to multiple locations)
            unique_jobs = self._deduplicate_jobs(all_jobs)
            
            return unique_jobs[:limit]
        
        except Exception as e:
            print(f"Error getting trending jobs: {e}")
            return []
    
    async def analyze_skills_demand(self) -> Dict:
        """
        Analyze most in-demand skills from job postings.
        """
        try:
            trending_jobs = await self.get_trending_jobs(limit=100)
            
            skills_count = {}
            for job in trending_jobs:
                description = (job.get("description", "") + job.get("title", "")).lower()
                
                # Count skill occurrences
                common_skills = [
                    "python", "javascript", "java", "react", "aws",
                    "docker", "machine learning", "data science"
                ]
                
                for skill in common_skills:
                    if skill in description:
                        skills_count[skill] = skills_count.get(skill, 0) + 1
            
            # Sort by frequency
            sorted_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "top_skills": sorted_skills[:20],
                "total_jobs_analyzed": len(trending_jobs),
                "analysis_date": datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error analyzing skills demand: {e}")
            return {}
