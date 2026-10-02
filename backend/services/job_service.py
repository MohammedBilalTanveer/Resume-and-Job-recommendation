import aiohttp
import asyncio
import re
import time
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timezone
from backend.config import settings
from backend.utils import skills_taxonomy as tax
from backend.utils import text_utils as tu
from backend.utils.semantic import calibrate, similarity_matrix


# Role families used to infer target job titles from a resume's skills when the
# resume has no clear title. Each entry: role query -> {skill: weight}
ROLE_PROFILES: Dict[str, Dict[str, float]] = {
    "machine learning engineer": {"Machine Learning": 3, "Deep Learning": 2, "PyTorch": 2, "TensorFlow": 2,
                                  "scikit-learn": 2, "MLOps": 2, "NLP": 1.5, "Computer Vision": 1.5, "Python": 1},
    "ai engineer": {"LLMs": 3, "Generative AI": 3, "RAG": 3, "LangChain": 2, "Prompt Engineering": 2,
                    "Vector Databases": 2, "Hugging Face": 1.5, "Transformers": 1.5, "Python": 1},
    "data scientist": {"Data Science": 3, "Machine Learning": 2, "Statistics": 2, "Pandas": 1.5, "Python": 1,
                       "Predictive Modeling": 2, "Regression": 1, "A/B Testing": 1.5, "R": 1.5},
    "data analyst": {"Data Analysis": 3, "SQL": 2, "Excel": 2, "Tableau": 2, "Power BI": 2, "Statistics": 1,
                     "Data Visualization": 2, "Google Sheets": 1},
    "data engineer": {"Data Engineering": 3, "Apache Spark": 2, "Airflow": 2, "Kafka": 2, "ETL": 2, "dbt": 2,
                      "Snowflake": 1.5, "Databricks": 1.5, "SQL": 1, "Data Warehousing": 1.5},
    "backend developer": {"Backend Development": 3, "Django": 2, "FastAPI": 2, "Flask": 2, "Node.js": 2,
                          "Spring Boot": 2, "REST APIs": 2, "PostgreSQL": 1, "Microservices": 1.5, "Go": 1.5},
    "frontend developer": {"Frontend Development": 3, "React": 2.5, "Angular": 2, "Vue.js": 2, "TypeScript": 1.5,
                           "JavaScript": 1, "HTML": 1, "CSS": 1, "Next.js": 1.5, "Tailwind CSS": 1},
    "full stack developer": {"Full Stack Development": 3, "React": 1.5, "Node.js": 1.5, "Express.js": 1.5,
                             "MongoDB": 1, "JavaScript": 1, "Django": 1, "REST APIs": 1},
    "devops engineer": {"DevOps": 3, "Kubernetes": 2, "Docker": 2, "Terraform": 2, "CI/CD": 2, "AWS": 1.5,
                        "Jenkins": 1.5, "Ansible": 1.5, "Linux": 1, "SRE": 2},
    "cloud engineer": {"AWS": 2.5, "Azure": 2.5, "GCP": 2.5, "Cloud Architecture": 2, "Terraform": 1.5,
                       "Serverless": 1.5},
    "mobile developer": {"Mobile Development": 3, "Android": 2, "iOS": 2, "Flutter": 2, "React Native": 2,
                         "Kotlin": 1.5, "Swift": 1.5},
    "qa automation engineer": {"Automation Testing": 3, "Selenium": 2, "Cypress": 2, "Playwright": 2,
                               "Manual Testing": 1.5, "Unit Testing": 1},
    "security analyst": {"Security": 3, "Penetration Testing": 2, "SIEM": 2, "Networking": 1, "CISSP": 2},
    "ui ux designer": {"UI/UX": 3, "Figma": 2.5, "Adobe XD": 2, "Sketch": 2, "Photoshop": 1},
    "product manager": {"Product Management": 3, "Agile": 1, "Jira": 1, "Stakeholder Management": 1.5},
    "project manager": {"Project Management": 3, "PMP": 2, "Agile": 1.5, "Scrum": 1.5, "Risk Management": 1},
    "business analyst": {"Business Analysis": 3, "SQL": 1, "Excel": 1.5, "Data Analysis": 1, "Jira": 1},
    "digital marketing specialist": {"Digital Marketing": 3, "SEO": 2, "PPC": 2, "Social Media Marketing": 2,
                                     "Content Marketing": 2, "Google Analytics": 1.5, "Email Marketing": 1.5},
    "sales executive": {"Sales": 3, "CRM": 1.5, "Salesforce": 1.5, "Negotiation": 1.5, "HubSpot": 1},
    "accountant": {"Accounting": 3, "Taxation": 2, "Auditing": 2, "Financial Analysis": 1.5, "Tally": 1.5,
                   "QuickBooks": 1.5, "Excel": 1},
    "financial analyst": {"Financial Analysis": 3, "Budgeting": 2, "Excel": 1.5, "CFA": 2},
    "hr generalist": {"HR Management": 3, "Recruitment": 2.5, "Workday": 1},
    "registered nurse": {"Nursing": 3, "Patient Care": 2.5, "Critical Care": 2, "EMR": 1.5, "BLS": 1, "ACLS": 1},
    "customer support specialist": {"Customer Service": 3, "Zendesk": 2, "CRM": 1, "Communication": 0.5},
}

_LEVEL_WORDS = r"\b(?:senior|sr|junior|jr|lead|principal|staff|intern|internship|trainee|associate|entry[- ]level|ii|iii|iv|i)\b\.?"
_SENIOR_RE = re.compile(r"\b(?:senior|sr\.?|lead|principal|staff|head of|director|architect|manager|vp)\b", re.I)
_JUNIOR_RE = re.compile(r"\b(?:junior|jr\.?|intern|internship|trainee|entry[- ]level|graduate|fresher|associate)\b", re.I)


class _TTLCache:
    def __init__(self, ttl_seconds: int = 1800, max_items: int = 256):
        self.ttl, self.max_items, self._data = ttl_seconds, max_items, {}

    def get(self, key):
        item = self._data.get(key)
        if item and time.time() - item[0] < self.ttl:
            return item[1]
        self._data.pop(key, None)
        return None

    def set(self, key, value):
        if len(self._data) >= self.max_items:
            oldest = min(self._data, key=lambda k: self._data[k][0])
            self._data.pop(oldest, None)
        self._data[key] = (time.time(), value)


class JobService:
    """
    Service to integrate multiple job APIs for job search and recommendations.
    """

    def __init__(self):
        self.remotive_url = "https://remotive.com/api/remote-jobs"
        self.adzuna_app_id = settings.ADZUNA_APP_ID
        self.adzuna_app_key = settings.ADZUNA_APP_KEY
        self.jooble_key = settings.JOOBLE_API_KEY
        self.timeout = aiohttp.ClientTimeout(total=15, connect=6)
        # Job boards rate-limit aggressively (Remotive asks for few requests/day)
        self._cache = _TTLCache(ttl_seconds=1800)

    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate job postings: same URL, or same company + title + description start
        (the same job posted to several locations or returned by several queries/sources).
        """
        if not jobs:
            return jobs

        seen = set()
        unique_jobs = []

        for job in jobs:
            company = (job.get("company") or "").lower().strip()
            title = re.sub(r"\W+", " ", (job.get("title") or "").lower()).strip()
            description = tu.strip_html(job.get("description") or "").lower()[:160].strip()
            url = (job.get("url") or "").split("?")[0].lower()
            keys = {f"{company}|{title}|{description}"}
            if url:
                keys.add(url)
            if keys & seen:
                continue
            seen |= keys
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
        Search for jobs from multiple sources (queried concurrently).
        """
        cache_key = (keyword.lower().strip(), (location or "").lower().strip(), job_type, source)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        tasks = []
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            if source is None or source == "remotive":
                tasks.append(self._search_remotive(session, keyword, location, job_type))
            if source is None or source == "adzuna":
                tasks.append(self._search_adzuna(session, keyword, location))
            if source is None or source == "jooble":
                tasks.append(self._search_jooble(session, keyword, location))
            batches = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for batch in batches:
            if isinstance(batch, Exception):
                print(f"Error searching jobs: {batch}")
                continue
            results.extend(batch)

        results = self._deduplicate_jobs(results)
        if results:
            self._cache.set(cache_key, results)
        return results

    async def _search_remotive(
        self,
        session: aiohttp.ClientSession,
        keyword: str,
        location: str,
        job_type: Optional[str]
    ) -> List[Dict]:
        """
        Search jobs from Remotive API.
        Free API - no authentication needed.
        """
        try:
            params = {"search": keyword, "limit": 50}
            async with session.get(self.remotive_url, params=params) as resp:
                if resp.status != 200:
                    print(f"Remotive API error: {resp.status}")
                    return []
                data = await resp.json(content_type=None)
                jobs = []
                for job in data.get("jobs", []):
                    if job_type and job_type.lower().replace("-", "_") not in (job.get("job_type") or "").lower():
                        continue
                    jobs.append({
                        "id": str(job.get("id")),
                        "title": job.get("title"),
                        "company": job.get("company_name"),
                        "location": job.get("candidate_required_location") or "Remote",
                        "description": job.get("description"),
                        "url": job.get("url"),
                        "type": (job.get("job_type") or "full_time").replace("_", "-").title(),
                        "posted_date": job.get("publication_date"),
                        "source": "remotive",
                        "salary": job.get("salary") or "Not specified",
                        "tags": job.get("tags") or [],
                    })
                return jobs
        except Exception as e:
            print(f"Error searching Remotive: {e}")
            return []

    async def _search_adzuna(self, session: aiohttp.ClientSession, keyword: str, location: str) -> List[Dict]:
        """
        Search jobs from Adzuna API.
        Requires API credentials.
        """
        try:
            if not self.adzuna_app_id or not self.adzuna_app_key:
                return []

            country_code, where = self._adzuna_country(location)
            params = {
                "app_id": self.adzuna_app_id,
                "app_key": self.adzuna_app_key,
                "what": keyword,
                "results_per_page": 50,
                "content-type": "application/json",
            }
            if where:
                params["where"] = where
            url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"

            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    print(f"Adzuna API error: {resp.status}")
                    return []
                data = await resp.json(content_type=None)
                jobs = []
                for job in data.get("results", []):
                    smin, smax = job.get("salary_min"), job.get("salary_max")
                    salary = "Not specified"
                    if smin and smax and smin != smax:
                        salary = f"{int(smin):,} - {int(smax):,}"
                    elif smin:
                        salary = f"{int(smin):,}"
                    jobs.append({
                        "id": str(job.get("id")),
                        "title": job.get("title"),
                        "company": (job.get("company") or {}).get("display_name"),
                        "location": (job.get("location") or {}).get("display_name"),
                        "description": job.get("description"),
                        "url": job.get("redirect_url"),
                        "type": (job.get("contract_time") or "full_time").replace("_", "-").title(),
                        "posted_date": job.get("created"),
                        "source": "adzuna",
                        "salary": salary,
                    })
                return jobs

        except Exception as e:
            print(f"Error searching Adzuna: {e}")
            return []

    @staticmethod
    def _adzuna_country(location: str) -> Tuple[str, str]:
        """Map a free-text location to an Adzuna country code + 'where' filter."""
        loc = (location or "").lower().strip()
        countries = {
            "india": "in", "united kingdom": "gb", "uk": "gb", "england": "gb", "london": "gb",
            "canada": "ca", "australia": "au", "germany": "de", "france": "fr", "netherlands": "nl",
            "singapore": "sg", "new zealand": "nz", "south africa": "za", "brazil": "br", "poland": "pl",
            "italy": "it", "spain": "es", "austria": "at", "belgium": "be", "switzerland": "ch", "mexico": "mx",
            "bangalore": "in", "bengaluru": "in", "mumbai": "in", "delhi": "in", "hyderabad": "in",
            "pune": "in", "chennai": "in", "toronto": "ca", "sydney": "au", "berlin": "de",
        }
        if loc in ("", "remote", "anywhere", "worldwide"):
            return "us", ""
        for name, code in countries.items():
            if name in loc:
                where = "" if loc == name and name in ("india", "uk", "united kingdom", "canada", "australia",
                                                         "germany", "france") else location
                return code, where
        return "us", location

    async def _search_jooble(self, session: aiohttp.ClientSession, keyword: str, location: str) -> List[Dict]:
        """
        Search jobs from Jooble API.
        Requires API key.
        """
        try:
            if not self.jooble_key:
                return []

            url = f"https://jooble.org/api/{self.jooble_key}"
            payload = {
                "keywords": keyword,
                "location": location if location and location.lower() != "remote" else ""
            }
            async with session.post(url, json=payload, headers={"Content-Type": "application/json"}) as resp:
                if resp.status != 200:
                    print(f"Jooble API error: {resp.status}")
                    return []
                data = await resp.json(content_type=None)
                jobs = []
                for job in data.get("jobs", []):
                    jobs.append({
                        "id": str(job.get("id")),
                        "title": job.get("title"),
                        "company": job.get("company"),
                        "location": job.get("location"),
                        "description": job.get("snippet"),
                        "url": job.get("link"),
                        "type": job.get("type") or "Full-time",
                        "posted_date": job.get("updated"),
                        "source": "jooble",
                        "salary": job.get("salary") or "Not specified"
                    })
                return jobs

        except Exception as e:
            print(f"Error searching Jooble: {e}")
            return []

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    @staticmethod
    def infer_target_roles(profile: Dict, ranked_skills: List[str], limit: int = 3) -> List[str]:
        """
        Target job titles for a resume: titles it already uses (latest role, headline),
        then roles inferred from its skills.
        """
        roles: List[str] = []

        def add(role: str):
            role = re.sub(_LEVEL_WORDS, " ", role, flags=re.IGNORECASE)
            role = re.sub(r"[^A-Za-z+#./ ]", " ", role)
            role = re.sub(r"\s+", " ", role).strip(" ./").lower()
            if 2 <= len(role) <= 40 and len(role.split()) <= 4 and role not in roles:
                roles.append(role)

        candidates = []
        if profile.get("title"):
            candidates.append(profile["title"])
        header = profile.get("sections", {}).get("header", "")
        from backend.utils.advanced_ats_scorer import ROLE_RE
        for line in header.split("\n")[:6]:
            for part in re.split(r"\s*[|•,]\s*", line):
                if ROLE_RE.fullmatch(part.strip()):
                    candidates.append(part.strip())
        for c in candidates:
            # "AI / ML Engineer" -> "AI Engineer", "ML Engineer"
            m = re.match(r"^\s*([\w+#.]+)\s*/\s*([\w+#.]+)\s+(.+)$", c)
            if m:
                add(f"{m.group(1)} {m.group(3)}")
                add(f"{m.group(2)} {m.group(3)}")
            else:
                add(c)

        have = set(ranked_skills)
        scored = []
        for role, weights in ROLE_PROFILES.items():
            score = sum(w for s, w in weights.items() if s in have)
            if score >= 3:
                scored.append((score, role))
        for _, role in sorted(scored, reverse=True):
            add(role)
        # Job boards match full titles better than abbreviations
        expanded = []
        for r in roles:
            r = re.sub(r"\bml\b", "machine learning", r)
            r = re.sub(r"\bswe\b", "software engineer", r)
            if r not in expanded:
                expanded.append(r)
        return expanded[:limit]

    @staticmethod
    def _job_level(title: str) -> str:
        if _JUNIOR_RE.search(title or ""):
            return "junior"
        if _SENIOR_RE.search(title or ""):
            return "senior"
        return "mid"

    @staticmethod
    def _days_old(posted: Optional[str]) -> Optional[float]:
        if not posted:
            return None
        try:
            dt = datetime.fromisoformat(str(posted).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        except Exception:
            return None

    def rank_jobs(self, jobs: List[Dict], profile: Dict, ranked_skills: List[str],
                  target_roles: List[str], location: Optional[str] = None,
                  shortlist: int = 40) -> List[Dict]:
        """
        Score each job against the candidate and return them best-first with match details.
        Pass 1 scores every job cheaply (skills + title words); pass 2 adds semantic
        similarity for the shortlist only, which keeps ranking fast on CPU.
        """
        if not jobs:
            return []
        have = set(profile["skills"])
        core = [s for s in ranked_skills if not tax.is_soft_skill(s)][:10]
        years = profile.get("experience_years_exact", 0)
        role_queries = [r for r in (target_roles or [profile.get("title") or ""]) if r]
        role_stems = [set(tu.content_terms(r)) for r in role_queries]

        # ---- pass 1: skills + title word overlap -------------------------
        scored = []
        for job in jobs:
            title = job.get("title") or ""
            desc = tu.strip_html(job.get("description") or "")
            job_skills = tax.find_skills(f"{title}\n{desc}")
            title_skills = tax.find_skills(title)
            for tag in job.get("tags") or []:
                for name in tax.find_skills(str(tag)):
                    job_skills.setdefault(name, {"category": tax.CANONICAL_CATEGORY.get(name, ""), "count": 1})

            # Requirement coverage: how much of what the job asks for the candidate has
            weights = {n: tax.skill_weight(n) * (1.5 if n in title_skills else 1.0) for n in job_skills}
            earned = total = 0.0
            matched, missing = [], []
            for n, w in sorted(weights.items(), key=lambda kv: -kv[1]):
                total += w
                if n in have:
                    earned += w
                    matched.append(n)
                else:
                    rel, _ = tax.related_credit(n, have)
                    earned += w * rel * 0.8
                    if not tax.is_soft_skill(n):
                        missing.append(n)
            coverage = earned / total if total else 0.0
            # Candidate-centric: how many of the candidate's core skills the job uses
            core_hit = min(1.0, sum(1 for s in core if s in job_skills) / max(1, min(len(core), 6)))
            if len(job_skills) < 3:  # short snippets: lean on the candidate's skills
                skill_fit = 0.3 * coverage + 0.7 * core_hit
            else:
                skill_fit = 0.6 * coverage + 0.4 * core_hit

            t_stems = set(tu.content_terms(title))
            word_overlap = max((len(t_stems & rs) / len(rs) for rs in role_stems if rs), default=0.0)
            scored.append({"job": job, "desc": desc, "skill_fit": skill_fit, "word_overlap": word_overlap,
                           "matched": matched, "missing": missing,
                           "cheap": 0.65 * skill_fit + 0.35 * word_overlap})

        scored.sort(key=lambda x: x["cheap"], reverse=True)
        scored = scored[:max(shortlist, 1)]

        # ---- pass 2: semantic similarity on the shortlist ------------------
        job_texts = [f"{x['job'].get('title') or ''}\n{x['desc'][:1200]}" for x in scored]
        job_titles = [x["job"].get("title") or "" for x in scored]
        resume_doc = "\n".join(filter(None, [
            profile.get("title") or "", profile.get("sections", {}).get("summary", "")[:600],
            ", ".join(core), "\n".join(profile.get("bullets", [])[:8])]))[:2000]
        sem = similarity_matrix([resume_doc], job_texts)[0]
        title_sim = similarity_matrix(role_queries or ["professional"], job_titles).max(axis=0)

        loc = (location or "").lower().strip()
        ranked = []
        for i, x in enumerate(scored):
            job = x["job"]
            semantic = calibrate(float(sem[i]))
            title_fit = max(calibrate(float(title_sim[i])), x["word_overlap"])
            score = 0.45 * x["skill_fit"] + 0.30 * semantic + 0.25 * title_fit

            level = self._job_level(job.get("title") or "")
            reasons = []
            if level == "senior" and years < 3:
                score *= 0.7
                reasons.append("Senior role - may need more experience")
            elif level == "junior" and years >= 6:
                score *= 0.8
            elif level == "junior" and years < 2:
                score = min(1.0, score * 1.08)
                reasons.append("Matches your experience level")

            age = self._days_old(job.get("posted_date"))
            if age is not None:
                if age <= 14:
                    score = min(1.0, score * 1.04)
                    reasons.append("Posted recently")
                elif age > 60:
                    score *= 0.9

            job_loc = (job.get("location") or "").lower()
            if loc and loc not in ("remote", "anywhere"):
                if loc in job_loc or any(w in job_loc for w in ("worldwide", "anywhere")):
                    score = min(1.0, score * 1.05)
                elif job.get("source") == "remotive" and job_loc:
                    score *= 0.85

            if x["matched"]:
                reasons.insert(0, f"Matches your skills: {', '.join(x['matched'][:5])}")
            if title_fit >= 0.6:
                reasons.insert(0, "Title fits your background")

            out = dict(job)
            out.update({
                "match_score": round(score * 100, 1),
                "matched_skills": x["matched"][:10],
                "missing_skills": x["missing"][:6],
                "match_reasons": reasons[:4],
            })
            ranked.append(out)

        ranked.sort(key=lambda j: j["match_score"], reverse=True)
        return ranked

    async def get_recommendations(
        self,
        skills: List[str],
        top_k: int = 5,
        location: Optional[str] = None,
        profile: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Get job recommendations for a candidate.
        Searches several queries (target roles + core skills) across all sources
        concurrently, then ranks every result by actual fit.
        """
        try:
            if not skills and not profile:
                return []
            if profile is None:
                profile = {"skills": {s: {} for s in skills}, "title": None, "sections": {},
                           "bullets": [], "experience_years_exact": 0}

            roles = self.infer_target_roles(profile, skills)
            core = [s for s in skills if not tax.is_soft_skill(s)
                    and tax.CANONICAL_CATEGORY.get(s) not in ("concepts_practices", "certifications")]
            queries = list(dict.fromkeys(roles[:3] + core[:2])) or skills[:2]
            loc = location or "remote"

            results = await asyncio.gather(*(self.search_jobs(q, loc) for q in queries),
                                           return_exceptions=True)
            jobs = []
            for r in results:
                if not isinstance(r, Exception):
                    jobs.extend(r)
            jobs = self._deduplicate_jobs(jobs)

            # Embedding similarity is CPU-bound: keep it off the event loop
            ranked = await asyncio.to_thread(self.rank_jobs, jobs, profile, skills, roles, location,
                                             max(30, top_k * 4))
            return ranked[:max(1, top_k)]

        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []

    async def get_job_description(self, job_id: str) -> str:
        """
        Get full job description by job ID (searches the cached results).
        """
        for _, (_, jobs) in list(self._cache._data.items()):
            for job in jobs:
                if str(job.get("id")) == str(job_id):
                    return tu.strip_html(f"{job.get('title') or ''}\n{job.get('description') or ''}")
        return ""

    async def get_trending_jobs(self, limit: int = 10, location: str = "remote") -> List[Dict]:
        """
        Get trending jobs.
        """
        try:
            trending_keywords = [
                "Python", "React", "Machine Learning",
                "AWS", "DevOps", "Data Science"
            ]

            batches = await asyncio.gather(*(self.search_jobs(k, location) for k in trending_keywords),
                                           return_exceptions=True)
            all_jobs = []
            for batch in batches:
                if not isinstance(batch, Exception):
                    all_jobs.extend(batch)

            unique_jobs = self._deduplicate_jobs(all_jobs)
            unique_jobs.sort(key=lambda j: self._days_old(j.get("posted_date")) or 9999)

            return unique_jobs[:limit]

        except Exception as e:
            print(f"Error getting trending jobs: {e}")
            return []

    async def analyze_skills_demand(self) -> Dict:
        """
        Analyze most in-demand skills from job postings.
        """
        try:
            trending_jobs = await self.get_trending_jobs(limit=150)

            skills_count: Dict[str, int] = {}
            for job in trending_jobs:
                text = tu.strip_html(f"{job.get('title') or ''}\n{job.get('description') or ''}")
                for skill in tax.find_skills(text):
                    if tax.is_soft_skill(skill):
                        continue
                    skills_count[skill] = skills_count.get(skill, 0) + 1

            sorted_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)

            return {
                "top_skills": sorted_skills[:20],
                "total_jobs_analyzed": len(trending_jobs),
                "analysis_date": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error analyzing skills demand: {e}")
            return {}
