"""
Advanced ATS Scoring System

Scores a resume against a job description the way modern ATS / recruiters do:

  * Skills (38%)       - JD skills weighted by importance (required > general > preferred),
                         full credit when the skill is demonstrated in experience/projects,
                         reduced credit when only listed, partial credit for related skills.
  * Semantic fit (20%) - how well each JD requirement is covered by some resume bullet
                         (sentence embeddings, TF-IDF fallback).
  * Keywords (12%)     - JD domain terms (boilerplate and filler removed), stemmed.
  * Experience (10%)   - years from merged date ranges vs. the JD's minimum years.
  * Education (5%)     - highest degree vs. the JD's required degree.
  * ATS readiness (15%)- parseable sections, contact info, bullets, metrics, action verbs,
                         length, weak phrasing.

Experience/education weights are redistributed when the JD states no requirement.
Recommendations are derived from the same facts, with estimated score gains computed
by re-scoring the resume with each fix applied.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple

import numpy as np

from backend.utils import skills_taxonomy as tax
from backend.utils import text_utils as tu
from backend.utils.semantic import calibrate, encoder, similarity_matrix

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


BASE_WEIGHTS = {
    "skills": 0.38, "semantic": 0.20, "keywords": 0.12,
    "experience": 0.10, "education": 0.05, "format": 0.15,
}

ACTION_VERBS = [
    "accelerate", "achieve", "administer", "analyze", "architect", "automate", "award", "boost",
    "build", "coach", "collaborate", "conduct", "configure", "consolidate", "coordinate", "create",
    "customize", "cut", "debug", "decrease", "define", "deliver", "deploy", "design", "develop",
    "direct", "document", "drive", "earn", "enhance", "engineer", "establish", "evaluate", "execute",
    "expand", "facilitate", "forecast", "found", "generate", "grow", "guide", "hire", "identify",
    "implement", "improve", "increase", "influence", "initiate", "integrate", "introduce",
    "investigate", "launch", "lead", "maintain", "manage", "mentor", "migrate", "model", "modernize",
    "monitor", "negotiate", "optimize", "orchestrate", "organize", "oversee", "own", "partner",
    "pioneer", "plan", "present", "prioritize", "produce", "program", "propose", "prototype",
    "publish", "recruit", "redesign", "reduce", "refactor", "research", "resolve", "restructure",
    "revamp", "save", "scale", "secure", "ship", "simplify", "solve", "spearhead", "standardize",
    "streamline", "strengthen", "supervise", "test", "train", "transform", "translate",
    "troubleshoot", "upgrade", "validate", "visualize", "win", "write", "analyse", "optimise",
    "organise", "achieved", "established", "authored", "championed", "delivered", "exceeded",
]
_ACTION_STEMS = {tu.stem(v): v for v in ACTION_VERBS}

WEAK_PHRASES = [
    "responsible for", "duties included", "duties include", "worked on", "helped with", "helped to",
    "assisted with", "assisted in", "involved in", "tasked with", "in charge of", "participated in",
    "was part of", "familiar with", "exposure to", "various tasks",
]

_METRIC_RE = re.compile(
    r"\d+(?:\.\d+)?\s?%|[$€£₹]\s?\d|\b\d+(?:\.\d+)?\s?(?:k|m|mm|bn|x)\b|\b\d{1,3}(?:,\d{3})+\b|"
    r"\b\d+\+?\s+(?:users|clients|customers|people|engineers|developers|members|projects|hours|days|"
    r"weeks|months|requests|transactions|stores|teams|countries|cities|employees|students|reports|"
    r"applications|services|servers|records|orders|leads|accounts|products|features|patients|beds)\b|"
    r"\b(?:doubled|tripled|halved)\b",
    re.IGNORECASE,
)
_YEAR_ONLY_RE = re.compile(r"^(?:19|20)\d{2}$")

DEGREE_LEVELS = {1: "High School", 2: "Diploma / Associate", 3: "Bachelor's", 4: "Master's", 5: "PhD"}

# (regex, display name, level)
_DEGREE_PATTERNS: List[Tuple[str, str, int]] = [
    (r"\bph\.?\s?d\b|\bdoctor(?:ate| of philosophy)\b", "PhD", 5),
    (r"\bm\.?\s?tech\b", "M.Tech", 4), (r"\bm\.?\s?e\.(?=\s)|\bm\.e\b", "M.E.", 4),
    (r"\bmca\b", "MCA", 4), (r"\bmba\b|\bpgdm\b", "MBA", 4), (r"\bm\.?\s?sc\b", "M.Sc", 4),
    (r"\bm\.?\s?com\b", "M.Com", 4), (r"\bm\.s\.?(?=\s|,|$)|\bms\s+(?:in|of)\b|\bmsc\b", "M.S.", 4),
    (r"\bm\.a\.?(?=\s|,|$)|\bma\s+in\b", "M.A.", 4), (r"\bmaster'?s?\b(?:\s+(?:of|in|degree))?", "Master's", 4),
    (r"\bb\.?\s?tech\b", "B.Tech", 3), (r"\bb\.\s?e\.?(?=\s|,|$)|\bbe\s+in\b", "B.E.", 3),
    (r"\bbca\b", "BCA", 3), (r"\bbba\b", "BBA", 3), (r"\bb\.?\s?sc\b|\bbsc\b", "B.Sc", 3),
    (r"\bb\.?\s?com\b", "B.Com", 3), (r"\bb\.s\.?(?=\s|,|$)|\bbs\s+(?:in|of)\b", "B.S.", 3),
    (r"\bb\.a\.?(?=\s|,|$)|\bba\s+in\b", "B.A.", 3), (r"\bbsn\b", "BSN", 3), (r"\bllb\b", "LLB", 3),
    (r"\bmbbs\b", "MBBS", 3), (r"\bb\.?\s?pharm\b", "B.Pharm", 3),
    (r"\bbachelor'?s?\b(?:\s+(?:of|in|degree))?", "Bachelor's", 3),
    (r"\bassociate'?s?\s+(?:degree|of)\b", "Associate Degree", 2), (r"\bdiploma\b", "Diploma", 2),
    (r"\bpre[\s-]?university\b|\bpuc\b|\b12th\b|\bhsc\b|\bhigher secondary\b|\bintermediate\b", "Pre-University / 12th", 1),
    (r"\b10th\b|\bssc\b|\bsslc\b|\bhigh school\b|\bsecondary school\b", "High School", 1),
]
_FIELD_RE = re.compile(r"^\s*(?:degree\s+)?(?:of|in)\s+([A-Za-z&/ ]{3,60}?)(?=\s*(?:[,(|\-–:;]|\d|\bfrom\b|\bat\b|\bwith\b|\bcgpa\b|\bgpa\b|\n|$))", re.IGNORECASE)

_PHONE_RE = re.compile(r"(?<![\w])(\+?\d{1,3}[\s.-]?)?(\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{3,5}(?![\w])")
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

_ROLE_NOUNS = (
    r"engineer|developer|programmer|analyst|scientist|manager|designer|consultant|intern|architect|"
    r"administrator|specialist|nurse|accountant|teacher|coordinator|executive|associate|officer|"
    r"technician|lead|director|strategist|writer|marketer|recruiter|tester|researcher|assistant|"
    r"representative|advisor|auditor|editor|pharmacist|therapist|physician|operator"
)
ROLE_RE = re.compile(rf"\b(?:[A-Za-z+#./-]+\s+){{0,4}}(?:{_ROLE_NOUNS})s?\b", re.IGNORECASE)

_JD_REQUIRED_HDR = re.compile(
    r"requirement|qualification|must[\s-]have|what you(?:'ll)? (?:need|bring)|what we(?:'re| are) looking for|"
    r"you have|you bring|you should have|who you are|skills|minimum|basic|essential|about you|ideal candidate|"
    r"key skills|technical skills|experience required|desired profile|candidate profile|eligibility",
    re.IGNORECASE)
_JD_PREFERRED_HDR = re.compile(
    r"nice[\s-]to[\s-]have|preferred|bonus|plus|desired|good[\s-]to[\s-]have|would be great|extra credit|"
    r"ideally|optional|advantage",
    re.IGNORECASE)
_JD_RESP_HDR = re.compile(
    r"responsibilit|what you(?:'ll)? do|duties|the role|about the (?:role|job|position)|your impact|"
    r"day[\s-]to[\s-]day|what you will do|job description|role overview|key result",
    re.IGNORECASE)
_JD_NOISE_HDR = re.compile(
    r"benefit|perks|what we offer|we offer|about us|about the company|who we are|our company|compensation|"
    r"salary|equal opportunity|eeo|how to apply|why join|life at|our values|our culture",
    re.IGNORECASE)
_PREFERRED_CUE = re.compile(
    r"\ba plus\b|\bnice[\s-]to[\s-]have\b|\bpreferred\b|\bbonus\b|\bis an advantage\b|\bgood[\s-]to[\s-]have\b|"
    r"\bideally\b|\bdesirable\b|\bwould be great\b|\bnot required\b|\boptional\b|\bplus\b",
    re.IGNORECASE)
_REQUIRED_CUE = re.compile(r"\bmust\b|\brequired\b|\bminimum\b|\bat least\b|\bstrong\b|\bproficien|\bexpert", re.IGNORECASE)
_NOISE_LINE = re.compile(
    r"equal opportunity|benefits|health insurance|401k|paid time off|\bpto\b|salary|compensation|"
    r"apply now|visa|relocation|diversity|accommodation|background check|\bperks\b",
    re.IGNORECASE)
# Lines already scored by the experience/education components, or pure intro text
_UNIT_SKIP = re.compile(
    r"^\W*\d{1,2}\s*\+?\s*(?:-|to)?\s*\d{0,2}\s*\+?\s*(?:years?|yrs?)[^.;]{0,60}$|"
    r"^\W*(?:a\s+)?(?:bachelor|master|ph\.?d|degree|graduate)[^.;]{0,90}$|"
    r"^\W*(?:we are|we're|we have|our team is|you will join|join (?:our|us)|about (?:us|the role))",
    re.IGNORECASE)
_YEARS_REQ_RE = re.compile(
    r"(?:minimum\s+(?:of\s+)?|at\s+least\s+|over\s+)?(\d{1,2})\s*\+?\s*(?:-|to|–)?\s*(\d{1,2})?\s*\+?\s*(?:years?|yrs?)",
    re.IGNORECASE)
_EXPLICIT_YEARS_RE = re.compile(
    r"(\d{1,2}(?:\.\d)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:\w+\s+){0,3}?(?:experience|exp\b)", re.IGNORECASE)


class AdvancedATSScorer:
    """Resume vs. job description analyzer. Kept as a singleton (`advanced_ats_scorer`)."""

    # Kept for backwards compatibility with code that reads these
    SKILLS_DATABASE = {cat: list(skills.keys()) for cat, skills in tax.SKILLS.items()}
    FORMAT_KEYWORDS = {"sections": list(tu.SECTION_TITLES.keys()), "action_verbs": ACTION_VERBS}

    def __init__(self):
        self.openai_client = None
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._initialize_openai()
        encoder.warmup_async()

    def _initialize_openai(self):
        if not OPENAI_AVAILABLE or os.getenv("ATS_DISABLE_LLM", "").lower() in {"1", "true", "yes"}:
            return
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            try:
                self.openai_client = OpenAI(api_key=api_key, timeout=25.0, max_retries=1)
                print("[OK] OpenAI client initialized")
            except Exception as e:
                print(f"[WARN] Failed to initialize OpenAI: {e}")

    # ======================================================================
    # Public entry points
    # ======================================================================

    def comprehensive_analysis(self, resume_text: str, job_description: str) -> Dict:
        resume = self.parse_resume(resume_text)
        job = self.parse_job(job_description)

        skills = self._score_skills(resume, job)
        keywords = self._score_keywords(resume, job)
        semantic = self._score_semantic(resume, job)
        experience = self._score_experience(resume, job)
        education = self._score_education(resume, job)
        fmt = self._score_format(resume)

        components = {
            "skills": skills["score"], "semantic": semantic["score"], "keywords": keywords["score"],
            "experience": experience["score"], "education": education["score"], "format": fmt["score"],
        }
        weights = self._weights(job, components, len(keywords["matched"]) + len(keywords["missing"]))
        components["experience_ratio"] = experience["ratio"]
        overall = self._combine(components, weights)

        action_items = self._generate_action_items(resume, job, skills, keywords, experience,
                                                   education, fmt, components, weights)
        detailed = self._generate_detailed_analysis(resume, job, skills, keywords, semantic,
                                                    experience, education, fmt, overall)
        recommendations = self._get_ai_recommendations(resume, job, skills, keywords, experience,
                                                       education, fmt, overall, action_items, semantic["score"])

        matched_kw, missing_kw = keywords["matched"], keywords["missing"]
        all_resume_skills = sorted(self._rank_resume_skills(resume), key=str.lower)

        warnings = []
        if len(job["text"].split()) < 40:
            warnings.append("The job description is very short - paste the full posting (requirements and "
                            "responsibilities) for an accurate score.")
        if resume["word_count"] < 60:
            warnings.append("Very little text was extracted from the resume - if it's a scanned/image PDF, "
                            "upload a text-based PDF or DOCX.")
        explanation = self._generate_score_explanation(
            overall, skills, keywords, semantic, experience, education, fmt, job)
        if warnings:
            explanation = "Note: " + " ".join(warnings) + " " + explanation

        return {
            "overall_score": round(overall, 3),
            "score_percentage": round(overall * 100, 1),
            "grade": self._get_grade(overall),
            "method": "semantic_embeddings" if encoder.backend == "embeddings" else "rule_based",

            "score_breakdown": {
                "skill_match": round(skills["score"], 3),
                "keyword_match": round(keywords["score"], 3),
                "format_score": round(fmt["score"], 3),
                "content_similarity": round(semantic["score"], 3),
                "experience_match": None if experience["score"] is None else round(experience["score"], 3),
                "education_match": None if education["score"] is None else round(education["score"], 3),
                "ml_prediction": None,
                "weights": {k: round(v, 3) for k, v in weights.items()},
            },

            "skills_analysis": {
                "matched_skills": skills["matched"],
                "missing_skills": skills["missing"],
                "extra_skills": skills["extra"],
                "partial_matches": skills["partial"],
                "missing_required": skills["missing_required"],
                "missing_preferred": skills["missing_preferred"],
                "listed_not_demonstrated": skills["listed_only"],
                "match_percentage": round(skills["score"] * 100, 1),
                "skills_by_category": skills["by_category"],
            },

            "keyword_analysis": {
                "matched_keywords": matched_kw,
                "missing_keywords": missing_kw,
                "keyword_density": keywords["density"],
            },

            "format_analysis": {
                "sections_found": resume["sections_found"],
                "action_verbs_used": resume["action_verbs"],
                "action_verbs_count": len(resume["action_verbs"]),
                "format_issues": fmt["issues"],
                "format_suggestions": fmt["suggestions"],
                "metrics": fmt["metrics"],
            },

            "extracted_info": {
                "experience_years": resume["experience_years"],
                "experience_years_exact": resume["experience_years_exact"],
                "education": resume["education"],
                "highest_degree": DEGREE_LEVELS.get(resume["education_level"]),
                "contact_info": resume["contact"],
                "total_skills_found": len(self._rank_resume_skills(resume)),
                "current_title": resume["title"],
                "job_requirements": {
                    "title": job["title"],
                    "min_years": job["min_years"],
                    "degree": DEGREE_LEVELS.get(job["degree_level"]),
                    "required_skills": job["required_skills"],
                    "preferred_skills": job["preferred_skills"],
                },
            },

            "detailed_analysis": detailed,
            "ai_recommendations": recommendations,
            "action_items": action_items,
            "score_explanation": explanation,
            "warnings": warnings,

            # Flat fields consumed when saving to history
            "skills": all_resume_skills,
            "experience_years": resume["experience_years"],
            "education": resume["education"],
            "certifications": resume["certifications"],
            "matching_keywords": skills["matched"] + [k for k in matched_kw if k not in skills["matched"]][:15],
            "missing_keywords": skills["missing"] + [k for k in missing_kw if k not in skills["missing"]][:10],
        }

    def resume_insights(self, resume_text: str) -> Dict:
        """Resume-only analysis (no job description)."""
        resume = self.parse_resume(resume_text)
        fmt = self._score_format(resume)
        by_category = {}
        for name, info in resume["skills"].items():
            if not info.get("implied_by"):
                by_category.setdefault(info["category"], []).append(name)
        return {
            "skills": self._rank_resume_skills(resume),
            "skills_by_category": {k: sorted(v, key=str.lower) for k, v in by_category.items()},
            "experience_years": resume["experience_years"],
            "education": resume["education"],
            "certifications": resume["certifications"],
            "contact_info": resume["contact"],
            "sections": resume["sections_found"],
            "action_verbs": resume["action_verbs"],
            "current_title": resume["title"],
            "resume_quality_score": round(fmt["score"], 3),
            "format_issues": fmt["issues"],
            "format_suggestions": fmt["suggestions"],
        }

    # ---- Backwards-compatible helpers (used by routes) --------------------

    def _extract_all_skills(self, text: str) -> Dict:
        found = tax.find_skills(tu.normalize_text(text))
        by_category = {cat: [] for cat in tax.SKILLS}
        for name, info in found.items():
            by_category.setdefault(info["category"], []).append(name)
        return {"all": sorted(found, key=str.lower), "by_category": by_category}

    def _extract_experience_years(self, text: str) -> int:
        return self.parse_resume(text)["experience_years"]

    def _extract_education(self, text: str) -> List[str]:
        degrees, _ = self._extract_degrees(tu.normalize_text(text))
        return degrees

    def _extract_contact_info(self, text: str) -> Dict:
        return self._contact(tu.normalize_text(text))

    def _analyze_resume_structure(self, text: str) -> List[str]:
        return self.parse_resume(text)["sections_found"]

    def _extract_action_verbs(self, text: str) -> List[str]:
        return self.parse_resume(text)["action_verbs"]

    # ======================================================================
    # Parsing
    # ======================================================================

    def parse_resume(self, resume_text: str) -> Dict:
        text = tu.normalize_text(resume_text or "")
        sections = tu.split_sections(text)
        exp_text = "\n".join(sections.get(s, "") for s in ("experience",)).strip()
        context_text = "\n".join(sections.get(s, "") for s in ("experience", "projects", "summary",
                                                              "achievements", "volunteer", "publications"))
        # No experience/projects headers: anything outside the skills/education/contact
        # blocks counts as context (a bare skills list never does)
        non_context = ("skills", "education", "header", "certifications", "languages", "interests",
                       "coursework")
        if not exp_text and not sections.get("projects"):
            context_text = "\n".join(v for k, v in sections.items() if k not in non_context)
            if len(sections) == 1:  # no headers at all: can't tell sections apart
                context_text = text

        skills = tax.find_skills(text)
        in_context = tax.find_skills(context_text)
        for name, info in skills.items():
            info["in_context"] = name in in_context
            info["context_count"] = in_context.get(name, {}).get("count", 0)
        # Implied skills (MySQL => SQL); inherit evidence from the strongest source
        for _ in range(2):  # two passes so Next.js => React => JavaScript resolves
            for name, info in list(skills.items()):
                for implied in tax.IMPLIES.get(name, []):
                    if implied in skills and not skills[implied].get("implied_by"):
                        continue
                    cur = skills.get(implied)
                    if cur is None or (info["in_context"] and not cur["in_context"]):
                        skills[implied] = {
                            "category": tax.CANONICAL_CATEGORY.get(implied, info["category"]),
                            "count": 0, "positions": [], "in_context": info["in_context"],
                            "context_count": 0, "implied_by": name,
                        }

        # Bullets
        bullet_src = "\n".join(sections.get(s, "") for s in ("experience", "projects", "achievements",
                                                            "volunteer")).strip()
        if not bullet_src:
            bullet_src = text if len(sections) == 1 else \
                "\n".join(v for k, v in sections.items() if k not in non_context)
        bullets = [b for b in tu.extract_bullets(bullet_src) if len(b.split()) >= 3]

        # Experience years: merged date ranges in experience section (fallback: all text minus education)
        if exp_text:
            ranges = tu.date_ranges(exp_text)
        else:
            non_edu = "\n".join(v for k, v in sections.items() if k not in ("education", "projects",
                                                                            "certifications"))
            ranges = tu.date_ranges(non_edu)
        months = tu.merged_months(ranges)
        computed_years = months / 12.0
        explicit = [float(m.group(1)) for m in _EXPLICIT_YEARS_RE.finditer(
            sections.get("summary", "") + "\n" + sections.get("header", "") + "\n" + text[:600])]
        explicit_years = max([y for y in explicit if y <= 45], default=0.0)
        years_exact = max(computed_years, explicit_years)

        degrees, edu_level = self._extract_degrees(sections.get("education") or text)
        if not degrees and sections.get("education"):
            degrees, edu_level = self._extract_degrees(text)

        action_verbs, bullets_with_verbs = [], 0
        for b in bullets:
            first = tu.tokenize(b[:40])
            if first:
                st = tu.stem(first[0])
                if st in _ACTION_STEMS:
                    bullets_with_verbs += 1
                    if _ACTION_STEMS[st] not in action_verbs:
                        action_verbs.append(_ACTION_STEMS[st])
        # Also count action verbs used anywhere in bullets (for display)
        for b in bullets:
            for tok in tu.tokenize(b):
                st = tu.stem(tok)
                if st in _ACTION_STEMS and _ACTION_STEMS[st] not in action_verbs and len(tok) > 3:
                    action_verbs.append(_ACTION_STEMS[st])

        quantified = [b for b in bullets if self._has_metric(b)]
        lower = text.lower()
        weak_hits = {p: lower.count(p) for p in WEAK_PHRASES if p in lower}
        pronoun_count = sum(len(re.findall(r"\b(?:I|my|me)\b", b)) for b in bullets)

        certs = [n for n, i in skills.items() if i["category"] == "certifications"]
        cert_section = sections.get("certifications", "")
        if cert_section:
            for line in cert_section.split("\n"):
                line = line.strip(" •-")
                if 3 < len(line) < 90 and line not in certs:
                    certs.append(line)

        return {
            "text": text,
            "sections": sections,
            "sections_found": [tu.SECTION_TITLES[s] for s in tu.SECTION_TITLES if sections.get(s)],
            "skills": skills,
            "bullets": bullets,
            "quantified_bullets": quantified,
            "bullets_with_action_verbs": bullets_with_verbs,
            "action_verbs": action_verbs,
            "weak_phrases": weak_hits,
            "pronoun_count": pronoun_count,
            "experience_years_exact": round(years_exact, 1),
            "experience_years": int(years_exact + 0.25),
            "has_dates": bool(ranges),
            "education": degrees,
            "education_level": edu_level,
            "contact": self._contact(text),
            "certifications": certs[:15],
            "word_count": len(text.split()),
            "title": self._guess_title(sections, text),
        }

    def parse_job(self, job_description: str) -> Dict:
        text = tu.normalize_text(tu.strip_html(job_description or "") if "<" in (job_description or "") else job_description or "")
        lines = [l.strip() for l in text.split("\n")]
        title = self._job_title(lines)

        mode = "general"
        skill_weights: Dict[str, float] = {}
        skill_modes: Dict[str, set] = {}
        requirement_units: List[Tuple[str, float]] = []
        req_lines: List[str] = []

        for line in lines:
            if not line:
                continue
            is_header = len(line) <= 60 and (line.endswith(":") or len(line.split()) <= 6) and not line.startswith("• ")
            head = line.split(":")[0] if ":" in line[:50] else line
            if is_header or ":" in line[:50]:
                if _JD_NOISE_HDR.search(head) and len(head.split()) <= 6:
                    mode = "noise"
                    if is_header:
                        continue
                elif _JD_PREFERRED_HDR.search(head) and len(head.split()) <= 6:
                    mode = "preferred"
                elif _JD_REQUIRED_HDR.search(head) and len(head.split()) <= 6:
                    mode = "required"
                elif _JD_RESP_HDR.search(head) and len(head.split()) <= 6:
                    mode = "responsibility"
            if mode == "noise" or _NOISE_LINE.search(line):
                continue

            line_mode = mode
            if _PREFERRED_CUE.search(line):
                line_mode = "preferred"
            elif mode in ("general", "responsibility") and _REQUIRED_CUE.search(line):
                line_mode = "required"

            # Cues apply per clause: "AWS and Docker; Kubernetes is a plus"
            for clause in re.split(r";|\.\s+|\s-\s|\s–\s", line):
                clause_mode = mode
                if _PREFERRED_CUE.search(clause):
                    clause_mode = "preferred"
                elif mode in ("general", "responsibility") and _REQUIRED_CUE.search(clause):
                    clause_mode = "required"
                base = {"required": 1.0, "responsibility": 0.8, "general": 0.8, "preferred": 0.45}[clause_mode]
                for name in tax.find_skills(clause):
                    skill_weights[name] = max(skill_weights.get(name, 0.0), base)
                    skill_modes.setdefault(name, set()).add(clause_mode)

            if line_mode in ("required", "preferred"):
                req_lines.append(line)
            words = len(line.split())
            if 4 <= words <= 60 and not is_header and not _UNIT_SKIP.search(line):
                unit_w = {"required": 1.0, "responsibility": 0.8, "general": 0.6, "preferred": 0.4}[line_mode]
                requirement_units.append((re.sub(r"^(?:•|[-*])\s*", "", line), unit_w))

        # Skills in the title are core requirements
        for name in tax.find_skills(title or ""):
            skill_weights[name] = max(skill_weights.get(name, 0.0), 1.25)
            skill_modes.setdefault(name, set()).add("required")
        # Frequency boost
        all_found = tax.find_skills(text)
        for name, info in all_found.items():
            if name not in skill_weights:
                skill_weights[name] = 0.8
                skill_modes.setdefault(name, set()).add("general")
            if info["count"] >= 3:
                skill_weights[name] *= 1.15
        for name in skill_weights:
            skill_weights[name] *= tax.skill_weight(name)
            if "required" in skill_modes.get(name, set()) and "preferred" in skill_modes[name]:
                skill_weights[name] = max(skill_weights[name], 0.9 * tax.skill_weight(name))

        required = [n for n in skill_weights if "required" in skill_modes.get(n, ()) or
                    (skill_modes.get(n) and "preferred" not in skill_modes[n] and skill_weights[n] >= 0.8 * tax.skill_weight(n))]
        preferred = [n for n in skill_weights if n not in required]

        min_years = self._required_years(text)
        degree_level, degree_equivalent = self._required_degree(text)

        # Long JD without any bullet structure: split into sentences for semantic units
        if len(requirement_units) < 3:
            sentences = re.split(r"(?<=[.!?;])\s+", text.replace("\n", " "))
            requirement_units = [(s.strip(), 0.8) for s in sentences
                                 if 4 <= len(s.split()) <= 60 and not _NOISE_LINE.search(s)
                                 and not _UNIT_SKIP.search(s)] or [(s.strip(), 0.8) for s in sentences
                                                                   if 4 <= len(s.split()) <= 60]

        return {
            "text": text,
            "title": title,
            "skill_weights": skill_weights,
            "required_skills": sorted(required, key=lambda n: -skill_weights[n]),
            "preferred_skills": sorted(preferred, key=lambda n: -skill_weights[n]),
            "requirement_units": requirement_units[:30],
            "requirement_lines": req_lines,
            "min_years": min_years,
            "degree_level": degree_level,
            "degree_equivalent": degree_equivalent,
        }

    # ---- parsing helpers ---------------------------------------------------

    @staticmethod
    def _has_metric(line: str) -> bool:
        for m in _METRIC_RE.finditer(line):
            if not _YEAR_ONLY_RE.match(m.group(0).strip()):
                return True
        return False

    @staticmethod
    def _contact(text: str) -> Dict:
        contact = {}
        m = _EMAIL_RE.search(text)
        if m:
            contact["email"] = m.group()
        for m in _PHONE_RE.finditer(text):
            candidate = m.group().strip()
            digits = re.sub(r"\D", "", candidate)
            groups = re.findall(r"\d+", candidate)
            looks_like_years = len(groups) >= 2 and sum(
                1 for g in groups if len(g) == 4 and 1950 <= int(g) <= 2039) >= len(groups) - 1
            if 10 <= len(digits) <= 13 and not looks_like_years:
                contact["phone"] = candidate
                break
        m = re.search(r"(?:https?://)?(?:[a-z]{2,3}\.)?linkedin\.com/in/[A-Za-z0-9_\-%/]+", text, re.IGNORECASE)
        if m:
            contact["linkedin"] = m.group().rstrip("/.")
        m = re.search(r"(?:https?://)?github\.com/[A-Za-z0-9_\-]+", text, re.IGNORECASE)
        if m:
            contact["github"] = m.group()
        m = re.search(r"https?://(?!(?:www\.)?(?:linkedin|github)\.com)[^\s,|]+", text, re.IGNORECASE)
        if m:
            contact["portfolio"] = m.group().rstrip(".")
        return contact

    @staticmethod
    def _extract_degrees(text: str) -> Tuple[List[str], int]:
        degrees, best = [], 0
        lower = text.lower()
        seen_spans: List[Tuple[int, int]] = []
        for pattern, name, level in _DEGREE_PATTERNS:
            for m in re.finditer(pattern, lower):
                if any(s <= m.start() < e for s, e in seen_spans):
                    continue
                # Generic "bachelor's"/"master's" only when it looks like a degree
                if name in ("Bachelor's", "Master's") and not re.search(r"(?:of|in|degree)\s*$", m.group()):
                    after = lower[m.end():m.end() + 25]
                    if not re.match(r"\s*(?:of|in|degree|'s degree)", after):
                        continue
                seen_spans.append((m.start(), m.end()))
                tail = text[m.end():m.end() + 80]
                field_m = _FIELD_RE.match(tail) if not m.group().rstrip().endswith(("of", "in")) else \
                    re.match(r"\s*([A-Za-z&/ ]{3,60}?)(?=\s*(?:[,(|\-–:;]|\d|\bfrom\b|\bat\b|\bwith\b|\n|$))", tail)
                display = name
                if field_m:
                    field = re.sub(r"\s+", " ", field_m.group(1)).strip()
                    if 3 < len(field) <= 50 and not re.search(r"\b(?:university|college|institute|school)\b", field, re.I):
                        # Use the resume's own wording: "Bachelor of Science in Nursing", "B.S. in Computer Science"
                        original = re.sub(r"\s+", " ", text[m.start():m.end() + field_m.end()]).strip()
                        display = original if original[:1].isupper() else original.title()
                if display.lower() not in {d.lower() for d in degrees} and not any(
                        d.lower().startswith(name.lower()) for d in degrees):
                    degrees.append(display)
                best = max(best, level)
                break
        return degrees, best

    @staticmethod
    def _guess_title(sections: Dict[str, str], text: str) -> Optional[str]:
        def clean(t: str) -> str:
            t = re.split(r"\s[|@,–-]\s|\s{2,}|\t|\(|\bat\b", t)[0]
            return re.sub(r"\s+", " ", t).strip(" •-:|")

        exp = sections.get("experience", "")
        for line in exp.split("\n")[:12]:
            line = line.strip()
            if not line or line.startswith("• ") or len(line) > 110:
                continue
            m = ROLE_RE.search(line)
            if m:
                title = clean(line[m.start():m.end()])
                if 2 <= len(title) <= 60:
                    return title
        for line in (sections.get("header", "") + "\n" + sections.get("summary", "")).split("\n")[:8]:
            m = ROLE_RE.search(line)
            if m and len(line) < 120:
                title = clean(m.group())
                if 2 <= len(title) <= 60:
                    return title
        return None

    @staticmethod
    def _job_title(lines: List[str]) -> Optional[str]:
        for line in lines[:6]:
            if not line:
                continue
            if len(line.split()) <= 10 and ROLE_RE.search(line) and not _JD_RESP_HDR.search(line):
                return re.split(r"\s[|–-]\s|\(", line)[0].strip(" :")
        m = re.search(rf"(?:hiring|looking for|seeking)\s+(?:an?\s+)?((?:[A-Za-z+#./-]+\s+){{0,4}}(?:{_ROLE_NOUNS}))",
                      " ".join(lines[:15]), re.IGNORECASE)
        return m.group(1).strip() if m else None

    @staticmethod
    def _required_years(text: str) -> Optional[float]:
        mins = []
        for m in _YEARS_REQ_RE.finditer(text):
            context = text[max(0, m.start() - 60): m.end() + 80].lower()
            after = text[m.end(): m.end() + 40].lower()
            # "5+ years of experience", "3+ years building production apps", "5+ years Python"
            if "experience" not in context and not re.match(
                    r"\s*(?:of\s+)?(?:\w+\s+){0,2}?(?:building|working|developing|designing|managing|leading|"
                    r"professional|hands-on|industry|relevant|in\b|with\b|as\b|exp)", after) \
                    and not tax.find_skills(after[:30]):
                continue
            if re.search(r"\b(?:company|founded|in business|history|years old|ago|warranty)\b", context):
                continue
            lo = int(m.group(1))
            if 0 < lo <= 20:
                mins.append(lo)
        return float(max(mins)) if mins else None

    @staticmethod
    def _required_degree(text: str) -> Tuple[Optional[int], bool]:
        lower = text.lower()
        level = None
        if re.search(r"\bph\.?\s?d\b|\bdoctorate\b", lower) and re.search(r"(?:require|must|need)[^.]{0,40}ph\.?\s?d", lower):
            level = 5
        elif re.search(r"\bmaster'?s?\b|\bm\.?s\.?\b in|\bmba\b|\bm\.?\s?tech\b|\bmca\b", lower) and \
                not re.search(r"bachelor", lower):
            level = 4
        elif re.search(r"\bbachelor'?s?\b|\bb\.?s\.?\b in|\bb\.?\s?tech\b|\bb\.?e\.?\b in|\bbca\b|\bundergraduate degree\b|"
                       r"\bdegree in\b|\bgraduate in\b|\bgraduation\b|\bdegree\b", lower):
            level = 3
        elif re.search(r"\bdiploma\b|\bassociate'?s? degree\b", lower):
            level = 2
        elif re.search(r"\bhigh school\b|\b12th\b|\bged\b", lower):
            level = 1
        equivalent = bool(re.search(r"or equivalent|equivalent (?:practical |work )?experience|or related experience", lower))
        return level, equivalent

    # ======================================================================
    # Component scores
    # ======================================================================

    def _score_skills(self, resume: Dict, job: Dict) -> Dict:
        weights = job["skill_weights"]
        have = set(resume["skills"])
        matched, partial, missing, listed_only = [], [], [], []
        earned = total = 0.0
        req_earned = req_total = 0.0
        required = set(job["required_skills"])
        credits = {}

        for name, w in sorted(weights.items(), key=lambda kv: -kv[1]):
            total += w
            if name in have:
                info = resume["skills"][name]
                demo = info.get("in_context", False)
                if info.get("implied_by"):
                    credit = 0.85 if demo else 0.7
                else:
                    credit = 1.0 if demo else 0.8
                    if not demo:
                        listed_only.append(name)
                matched.append(name)
            else:
                rel, via = tax.related_credit(name, have)
                credit = rel * 0.85
                if rel > 0:
                    partial.append({"required": name, "have": via, "credit": round(credit, 2)})
                missing.append(name)
            credits[name] = credit
            earned += w * credit
            if name in required:
                req_total += w
                req_earned += w * credit

        score = earned / total if total else 0.0
        required_coverage = req_earned / req_total if req_total else score

        by_category = {}
        for name in weights:
            cat = tax.CANONICAL_CATEGORY.get(name, "other")
            entry = by_category.setdefault(cat, {"matched": [], "missing": [], "score": 0.0, "_w": 0.0, "_e": 0.0})
            (entry["matched"] if name in have else entry["missing"]).append(name)
            entry["_w"] += weights[name]
            entry["_e"] += weights[name] * credits[name]
        for cat, entry in by_category.items():
            entry["score"] = round(entry["_e"] / entry["_w"], 3) if entry["_w"] else 0.0
            del entry["_w"], entry["_e"]

        jd_skill_set = set(weights)
        extra = [n for n in self._rank_resume_skills(resume) if n not in jd_skill_set]
        return {
            "score": score,
            "required_coverage": required_coverage,
            "matched": matched,
            "missing": missing,
            "missing_required": [n for n in missing if n in required],
            "missing_preferred": [n for n in missing if n not in required],
            "partial": partial,
            "listed_only": listed_only,
            "extra": extra,
            "by_category": by_category,
            "credits": credits,
            "jd_skill_count": len(weights),
        }

    def _score_keywords(self, resume: Dict, job: Dict) -> Dict:
        skill_tokens = set()
        for name in list(job["skill_weights"]) + list(resume["skills"]):
            for tok in tu.tokenize(name):
                skill_tokens.add(tu.stem(tok))

        surface: Dict[str, Dict[str, int]] = {}
        weights: Dict[str, float] = {}
        req_text = " ".join(job["requirement_lines"]).lower()
        req_stems = set(tu.content_terms(req_text, tu.JD_BOILERPLATE))
        # Keywords come from requirement/responsibility lines and the title, not intros or perks
        source = "\n".join([job["title"] or ""] + [u for u, w in job["requirement_units"] if w >= 0.6])
        for tok in tu.tokenize(source or job["text"]):
            if len(tok) < 4 or tok in tu.STOPWORDS or tok in tu.JD_BOILERPLATE or tok.isdigit():
                continue
            st = tu.stem(tok)
            if st in skill_tokens or st in {tu.stem(w) for w in ("experience", "year", "skill", "team")}:
                continue
            surface.setdefault(st, {})
            surface[st][tok] = surface[st].get(tok, 0) + 1
            weights[st] = weights.get(st, 0.0) + 1.0
        for st in weights:
            weights[st] = min(weights[st], 3.0) * (1.4 if st in req_stems else 1.0)

        top = sorted(weights.items(), key=lambda kv: -kv[1])[:25]
        resume_stems = set(tu.content_terms(resume["text"]))
        matched, missing = [], []
        earned = total = 0.0
        for st, w in top:
            display = max(surface[st].items(), key=lambda kv: kv[1])[0]
            total += w
            if st in resume_stems:
                earned += w
                matched.append(display)
            else:
                missing.append(display)

        resume_tokens = [tu.stem(t) for t in tu.tokenize(resume["text"])]
        top_set = {st for st, _ in top}
        density = (sum(1 for t in resume_tokens if t in top_set) / len(resume_tokens) * 100) if resume_tokens else 0.0
        return {
            "score": earned / total if total else 0.0,
            "matched": matched,
            "missing": missing,
            "density": round(density, 2),
        }

    def _score_semantic(self, resume: Dict, job: Dict) -> Dict:
        units = job["requirement_units"]
        resume_units = list(dict.fromkeys(
            resume["bullets"]
            + [s for s in re.split(r"(?<=[.!?])\s+|\n", resume["sections"].get("summary", "")) if len(s.split()) >= 4]
            + [l for l in resume["sections"].get("skills", "").split("\n") if len(l.split()) >= 2]
        ))
        if len(resume_units) < 3:
            resume_units += [s for s in re.split(r"(?<=[.!?])\s+|\n", resume["text"]) if len(s.split()) >= 4]
        resume_units = [u[:400] for u in resume_units[:80]]

        if not units or not resume_units:
            return {"score": 0.0, "coverage": [], "doc_similarity": 0.0}

        sims = similarity_matrix([u for u, _ in units], resume_units)
        best = sims.max(axis=1)
        best_idx = sims.argmax(axis=1)
        covered = np.array([calibrate(float(s)) for s in best])
        w = np.array([uw for _, uw in units])
        coverage_score = float((covered * w).sum() / w.sum())

        doc = similarity_matrix([job["text"][:2000]], [resume["text"][:2000]])[0][0]
        doc_score = calibrate(float(doc))
        score = 0.6 * coverage_score + 0.4 * doc_score

        coverage = [{"requirement": units[i][0][:160], "best_match": resume_units[best_idx[i]][:160],
                     "coverage": round(float(covered[i]), 2)} for i in range(len(units))]
        return {"score": score, "coverage": coverage, "doc_similarity": round(float(doc), 3)}

    @staticmethod
    def _score_experience(resume: Dict, job: Dict) -> Dict:
        req = job["min_years"]
        have = resume["experience_years_exact"]
        if req is None:
            return {"score": None, "required": None, "have": have, "gap": 0, "ratio": None}
        if have >= req:
            score = 1.0
        else:
            score = max(0.1, (have + 0.5) / (req + 0.5)) ** 1.3
        return {"score": min(score, 1.0), "required": req, "have": have, "gap": max(0.0, req - have),
                "ratio": min(1.0, have / req) if req else None}

    @staticmethod
    def _score_education(resume: Dict, job: Dict) -> Dict:
        req = job["degree_level"]
        have = resume["education_level"]
        if req is None:
            return {"score": None, "required": None, "have": have}
        if have >= req:
            score = 1.0
        elif have == req - 1:
            score = 0.85 if job["degree_equivalent"] else 0.6
        elif have == 0:
            # Degree not detected - may be a parsing gap, don't zero it
            score = 0.6 if job["degree_equivalent"] else 0.35
        else:
            score = 0.5 if job["degree_equivalent"] else 0.3
        return {"score": score, "required": req, "have": have}

    def _score_format(self, resume: Dict) -> Dict:
        issues, suggestions = [], []
        sections = resume["sections"]
        contact = resume["contact"]
        bullets = resume["bullets"]
        n_bullets = len(bullets)
        score = 0.0

        # Contact (0.12)
        if contact.get("email"):
            score += 0.06
        else:
            issues.append("No email address found")
            suggestions.append("Add a professional email address at the top of your resume")
        if contact.get("phone"):
            score += 0.04
        else:
            issues.append("No phone number found")
            suggestions.append("Add a phone number with country code")
        if contact.get("linkedin"):
            score += 0.02
        else:
            suggestions.append("Add your LinkedIn profile URL")

        # Sections (0.27)
        if sections.get("experience"):
            score += 0.10
        elif sections.get("projects"):
            score += 0.07
            suggestions.append("Add an 'Experience' section (internships, freelance or volunteer work count)")
        else:
            issues.append("Missing 'Experience' section heading")
            suggestions.append("Use a standard 'Experience' or 'Work Experience' heading so ATS can parse your roles")
        if sections.get("education"):
            score += 0.06
        else:
            issues.append("Missing 'Education' section heading")
            suggestions.append("Add an 'Education' section with degree, institution and year")
        if sections.get("skills"):
            score += 0.08
        else:
            issues.append("Missing 'Skills' section heading")
            suggestions.append("Add a dedicated 'Skills' section - ATS keyword matching relies on it")
        if sections.get("summary"):
            score += 0.03
        else:
            suggestions.append("Add a 2-3 line professional summary tailored to the target role")

        # Bullets (0.08)
        if n_bullets >= 3:
            score += 0.08
        else:
            issues.append("Few bullet points describing your work")
            suggestions.append("Describe each role with 3-6 bullet points of achievements")

        # Quantified achievements (0.15)
        q = len(resume["quantified_bullets"])
        q_ratio = q / n_bullets if n_bullets else 0.0
        score += 0.15 * min(1.0, q_ratio / 0.4)
        if n_bullets and q_ratio < 0.25:
            issues.append(f"Only {q} of {n_bullets} bullet points include measurable results")
            suggestions.append("Add numbers to your bullets: %, $, time saved, users, team size")
        elif not n_bullets:
            issues.append("No quantifiable achievements found")

        # Action verbs at bullet start (0.12)
        v_ratio = resume["bullets_with_action_verbs"] / n_bullets if n_bullets else 0.0
        score += 0.12 * min(1.0, v_ratio / 0.6)
        if n_bullets and v_ratio < 0.4:
            issues.append("Most bullets don't start with a strong action verb")
            suggestions.append("Start bullets with verbs like Built, Led, Reduced, Automated, Launched")

        # Length (0.10)
        wc = resume["word_count"]
        if wc < 60:
            pass  # reported below as a parsing problem
        elif 350 <= wc <= 950:
            score += 0.10
        elif 200 <= wc < 350 or 950 < wc <= 1400:
            score += 0.05
            if wc < 350:
                issues.append(f"Resume is short ({wc} words)")
                suggestions.append("Expand on your experience and projects - aim for 400-900 words")
            else:
                suggestions.append(f"Resume is long ({wc} words) - trim older or less relevant content")
        else:
            issues.append(f"Resume is {'too short' if wc < 200 else 'too long'} ({wc} words)")
            suggestions.append("Aim for 400-900 words (1-2 pages)")

        # Weak phrasing (0.06)
        weak_total = sum(resume["weak_phrases"].values())
        score += 0.06 * max(0.0, 1 - weak_total / 4)
        if weak_total:
            top = sorted(resume["weak_phrases"].items(), key=lambda kv: -kv[1])[:3]
            issues.append("Passive phrasing: " + ", ".join(f"'{p}'" for p, _ in top))
            suggestions.append("Replace 'responsible for / worked on' with what you achieved")

        # First-person pronouns (0.04)
        if resume["pronoun_count"] == 0:
            score += 0.04
        else:
            issues.append("First-person pronouns (I, my) used in bullet points")
            suggestions.append("Remove 'I'/'my' from bullets - write 'Built X' instead of 'I built X'")

        # Dates (0.04)
        if resume["has_dates"]:
            score += 0.04
        elif sections.get("experience"):
            issues.append("No employment dates detected")
            suggestions.append("Add start and end dates (e.g. 'Jan 2022 - Present') to each role")

        # Parse quality (0.02)
        text = resume["text"]
        odd = len(re.findall(r"[^\x00-\x7F•₹€£]", text)) / max(1, len(text))
        if odd < 0.02 and wc >= 60:
            score += 0.02
        elif wc < 60:
            issues.append("Very little text could be extracted - the file may be image-based or use complex layouts")
            suggestions.append("Export your resume as a text-based PDF (not a scanned image) using a single-column layout")

        metrics = {
            "word_count": wc, "bullet_count": n_bullets, "quantified_bullets": q,
            "bullets_starting_with_action_verb": resume["bullets_with_action_verbs"],
            "weak_phrases": resume["weak_phrases"],
        }
        return {"score": min(1.0, score), "issues": issues, "suggestions": suggestions, "metrics": metrics}

    # ======================================================================
    # Combining
    # ======================================================================

    @staticmethod
    def _weights(job: Dict, components: Dict, n_keywords: int = 25) -> Dict:
        w = dict(BASE_WEIGHTS)
        n = len(job["skill_weights"])
        if n < 4:
            # Few recognizable skills in the JD -> skill match is a weak signal
            shift = w["skills"] * (1 - n / 4) * 0.7
            w["skills"] -= shift
            w["semantic"] += shift * 0.6
            w["keywords"] += shift * 0.4
        if n_keywords < 10:
            # Short JD -> only a handful of keywords, too noisy to weigh fully
            shift = w["keywords"] * (1 - n_keywords / 10)
            w["keywords"] -= shift
            w["skills"] += shift * 0.5
            w["semantic"] += shift * 0.5
        for k in ("experience", "education"):
            if components[k] is None:
                w.pop(k)
        total = sum(w.values())
        return {k: v / total for k, v in w.items()}

    @staticmethod
    def _combine(components: Dict, weights: Dict) -> float:
        score = sum(components[k] * w for k, w in weights.items() if components.get(k) is not None)
        # A resume that matches almost none of the core requirements shouldn't
        # be rescued by formatting alone.
        relevance = max(components["skills"], components["semantic"])
        score = min(score, 0.02 + 1.5 * relevance)
        # Far below the required years is a common hard filter in real ATS
        ratio = components.get("experience_ratio")
        if ratio is not None and ratio < 0.5:
            score *= 0.8 + 0.4 * ratio
        return float(min(max(score, 0.0), 1.0))

    @staticmethod
    def _get_grade(score: float) -> str:
        for threshold, grade in ((0.90, "A+"), (0.85, "A"), (0.80, "A-"), (0.75, "B+"), (0.70, "B"),
                                 (0.65, "B-"), (0.60, "C+"), (0.55, "C"), (0.50, "C-"), (0.40, "D")):
            if score >= threshold:
                return grade
        return "F"

    def _rank_resume_skills(self, resume: Dict, include_implied: bool = False) -> List[str]:
        def key(item):
            name, info = item
            return (-(info.get("context_count", 0) * 2 + info["count"]) * tax.skill_weight(name), name.lower())
        return [n for n, i in sorted(resume["skills"].items(), key=key)
                if include_implied or not i.get("implied_by")]

    # ======================================================================
    # Narrative: strengths, weaknesses, explanation, recommendations
    # ======================================================================

    @staticmethod
    def _fmt_list(items: List[str], n: int = 5) -> str:
        items = list(items)
        if len(items) <= n:
            return ", ".join(items)
        return ", ".join(items[:n]) + f" (+{len(items) - n} more)"

    def _generate_detailed_analysis(self, resume, job, skills, keywords, semantic, experience,
                                    education, fmt, overall) -> Dict:
        strengths, weaknesses = [], []
        req = job["required_skills"]
        req_have = [s for s in req if s in resume["skills"]]

        if req:
            if len(req_have) / len(req) >= 0.7:
                strengths.append(f"Covers {len(req_have)} of {len(req)} core skills: {self._fmt_list(req_have, 6)}")
            if skills["missing_required"]:
                weaknesses.append(f"Missing core skills from the job description: {self._fmt_list(skills['missing_required'])}")
        elif skills["matched"]:
            strengths.append(f"Matches skills mentioned in the job: {self._fmt_list(skills['matched'], 6)}")

        demonstrated = [s for s in skills["matched"] if s not in skills["listed_only"]]
        if len(demonstrated) >= 3:
            strengths.append(f"Skills backed by real experience/projects: {self._fmt_list(demonstrated, 5)}")
        if len(skills["listed_only"]) >= 2:
            weaknesses.append(f"Listed but not shown in any role or project: {self._fmt_list(skills['listed_only'])}")
        if skills["partial"]:
            p = skills["partial"][0]
            strengths.append(f"Transferable experience: {p['have']} is closely related to the required {p['required']}")

        if experience["score"] is not None:
            if experience["score"] >= 1.0:
                strengths.append(f"{resume['experience_years_exact']:g} years of experience meets the "
                                 f"{experience['required']:g}+ years requirement")
            else:
                weaknesses.append(f"Experience shown: ~{resume['experience_years_exact']:g} years vs. "
                                  f"{experience['required']:g}+ years required")
        elif resume["experience_years"] >= 2:
            strengths.append(f"{resume['experience_years_exact']:g} years of professional experience")

        if education["score"] is not None:
            if education["score"] >= 1.0:
                strengths.append(f"Education meets the requirement ({DEGREE_LEVELS[education['required']]})")
            elif resume["education_level"] == 0:
                weaknesses.append(f"No degree detected - the job asks for a {DEGREE_LEVELS[education['required']]} degree")
            else:
                weaknesses.append(f"Job asks for a {DEGREE_LEVELS[education['required']]} degree; "
                                  f"highest detected is {DEGREE_LEVELS[resume['education_level']]}")

        if semantic["score"] >= 0.65:
            strengths.append("Your experience closely mirrors the job's responsibilities")
        elif semantic["score"] < 0.35:
            weaknesses.append("Your bullet points don't describe work similar to this job's responsibilities")

        n_b, q = fmt["metrics"]["bullet_count"], fmt["metrics"]["quantified_bullets"]
        if n_b and q / n_b >= 0.4:
            strengths.append(f"{q} of {n_b} bullet points include measurable results")
        if fmt["score"] >= 0.8:
            strengths.append("ATS-friendly structure with clear, standard sections")
        elif fmt["score"] < 0.6:
            weaknesses.append("Resume structure/format will hurt ATS parsing (see Format section)")
        if keywords["score"] < 0.4 and keywords["missing"]:
            weaknesses.append(f"Low overlap with the job's terminology (e.g. {self._fmt_list(keywords['missing'], 4)})")

        return {
            "strengths": strengths[:6],
            "weaknesses": weaknesses[:6],
            "summary": self._generate_summary(overall, skills, experience, job),
            "requirement_coverage": semantic.get("coverage", [])[:12],
        }

    def _generate_summary(self, overall, skills, experience, job) -> str:
        role = f" for the {job['title']} role" if job["title"] else ""
        if overall >= 0.8:
            return (f"Excellent match{role}. Your resume covers the core requirements - fine-tune wording "
                    f"to mirror the job description and keep metrics prominent.")
        if overall >= 0.65:
            gap = skills["missing_required"][:3]
            return (f"Good match{role}. " + (f"Closing the gap on {', '.join(gap)} would make you a strong candidate."
                                            if gap else "Strengthen bullets with metrics and job-specific terms."))
        if overall >= 0.45:
            return (f"Partial match{role}. You have relevant foundations, but key requirements are missing or "
                    f"not clearly demonstrated. Tailor your resume to this job before applying.")
        return (f"Low match{role}. Your resume doesn't yet reflect most of this job's core requirements. "
                f"Consider roles closer to your current skills, or build experience in the missing areas.")

    def _generate_score_explanation(self, overall, skills, keywords, semantic, experience, education,
                                    fmt, job) -> str:
        parts = []
        if overall >= 0.8:
            parts.append("Your resume is highly optimized for this position.")
        elif overall >= 0.65:
            parts.append("Your resume is a good fit with room to improve.")
        elif overall >= 0.45:
            parts.append("Your resume partially matches this role.")
        else:
            parts.append("Your resume needs significant changes to match this role.")

        n_jd = skills["jd_skill_count"]
        parts.append(f"Skills ({skills['score'] * 100:.0f}%): {len(skills['matched'])} of {n_jd} job skills found"
                     + (f", missing core: {self._fmt_list(skills['missing_required'], 3)}." if skills["missing_required"] else "."))
        parts.append(f"Relevance ({semantic['score'] * 100:.0f}%): how well your bullets cover the job's requirements.")
        parts.append(f"Keywords ({keywords['score'] * 100:.0f}%): overlap with the job's domain terms.")
        if experience["score"] is not None:
            parts.append(f"Experience ({experience['score'] * 100:.0f}%): ~{experience['have']:g} yrs vs "
                         f"{experience['required']:g}+ required.")
        if education["score"] is not None:
            parts.append(f"Education ({education['score'] * 100:.0f}%).")
        parts.append(f"Format ({fmt['score'] * 100:.0f}%): " +
                     (fmt["issues"][0] + "." if fmt["issues"] else "clean, ATS-friendly structure."))
        return " ".join(parts)

    # ---- action items with simulated impact -------------------------------

    def _simulate(self, components: Dict, weights: Dict, **changes) -> float:
        new = dict(components)
        new.update(changes)
        return self._combine(new, weights)

    def _skills_score_if(self, skills: Dict, job: Dict, add: List[str] = (), demonstrate: List[str] = ()) -> float:
        credits = dict(skills["credits"])
        for n in add:
            credits[n] = max(credits.get(n, 0), 0.8)
        for n in demonstrate:
            credits[n] = 1.0
        w = job["skill_weights"]
        total = sum(w.values())
        return sum(w[n] * credits.get(n, 0) for n in w) / total if total else 0.0

    def _generate_action_items(self, resume, job, skills, keywords, experience, education, fmt,
                               components, weights) -> List[Dict]:
        base = self._combine(components, weights)
        items = []

        def impact(new_score: float, fallback: str) -> str:
            gain = round((new_score - base) * 100)
            return f"Estimated +{gain} points to your ATS score" if gain >= 1 else fallback

        if skills["missing_required"]:
            add = skills["missing_required"][:6]
            new_skill = self._skills_score_if(skills, job, add=add)
            items.append({
                "priority": "high", "category": "Skills Gap",
                "action": f"Add the required skills you have experience with: {', '.join(add)} - "
                          f"list them under Skills and mention them in a relevant bullet",
                "impact": impact(self._simulate(components, weights, skills=new_skill), "Required for this role"),
            })
        if skills["listed_only"]:
            demo = skills["listed_only"][:5]
            new_skill = self._skills_score_if(skills, job, demonstrate=demo)
            items.append({
                "priority": "high" if len(demo) >= 3 else "medium", "category": "Skill Evidence",
                "action": f"Show how you used {', '.join(demo)} in your experience or projects - "
                          f"right now they only appear in your skills list",
                "impact": impact(self._simulate(components, weights, skills=new_skill),
                                 "Recruiters trust skills shown in context"),
            })
        if skills["missing_preferred"] and base >= 0.35:
            add = skills["missing_preferred"][:5]
            new_skill = self._skills_score_if(skills, job, add=add)
            items.append({
                "priority": "medium", "category": "Nice-to-have Skills",
                "action": f"If applicable, add these preferred skills: {', '.join(add)}",
                "impact": impact(self._simulate(components, weights, skills=new_skill), "Helps you stand out"),
            })
        if keywords["missing"] and keywords["score"] < 0.75:
            kw = keywords["missing"][:6]
            new_kw = min(1.0, keywords["score"] + (1 - keywords["score"]) * 0.5)
            items.append({
                "priority": "medium", "category": "Keywords",
                "action": f"Mirror the job's wording where it's truthful: {', '.join(kw)}",
                "impact": impact(self._simulate(components, weights, keywords=new_kw), "Improves keyword matching"),
            })
        n_b, q = fmt["metrics"]["bullet_count"], fmt["metrics"]["quantified_bullets"]
        if n_b and q / n_b < 0.4:
            target_q = max(q + 1, round(n_b * 0.5))
            gain_fmt = 0.15 * (min(1.0, (target_q / n_b) / 0.4) - min(1.0, (q / n_b) / 0.4))
            items.append({
                "priority": "high" if q / n_b < 0.2 else "medium", "category": "Impact & Metrics",
                "action": f"Quantify more achievements - only {q} of {n_b} bullets have numbers "
                          f"(aim for at least {target_q})",
                "impact": impact(self._simulate(components, weights, format=min(1.0, components["format"] + gain_fmt)),
                                 "Makes achievements credible"),
            })
        if experience["score"] is not None and experience["score"] < 1.0:
            items.append({
                "priority": "medium", "category": "Experience",
                "action": f"The role asks for {experience['required']:g}+ years; ~{experience['have']:g} detected. "
                          f"Include all relevant roles (internships, freelance, contract) with clear start/end dates",
                "impact": "Ensures your full experience is counted",
            })
        for issue in fmt["issues"][:4]:
            if issue.startswith("Only ") and "measurable" in issue:
                continue
            items.append({"priority": "medium" if "Missing" in issue or "No " in issue else "low",
                          "category": "Format", "action": issue,
                          "impact": "Improves ATS parsing and readability"})
        if base >= 0.45 and job["title"] and resume["sections"].get("summary") and                 job["title"].lower() not in resume["text"].lower():
            items.append({"priority": "low", "category": "Targeting",
                          "action": f"Mention the target title '{job['title']}' in your summary",
                          "impact": "Recruiters often search by job title"})

        order = {"high": 0, "medium": 1, "low": 2}
        items.sort(key=lambda i: order[i["priority"]])
        return items[:10]

    # ---- recommendations ----------------------------------------------------

    def _get_ai_recommendations(self, resume, job, skills, keywords, experience, education, fmt,
                                overall, action_items, semantic_score: float = 0.0) -> List[str]:
        rule_based = self._get_fallback_recommendations(resume, job, dict(skills, semantic=semantic_score),
                                                        keywords, experience, education, fmt, overall)
        if not self.openai_client:
            return rule_based
        try:
            weak_bullets = [b for b in resume["bullets"] if not self._has_metric(b)][:4]
            facts = {
                "target_role": job["title"],
                "ats_score": round(overall * 100),
                "required_skills_missing": skills["missing_required"][:8],
                "preferred_skills_missing": skills["missing_preferred"][:6],
                "skills_listed_but_not_demonstrated": skills["listed_only"][:6],
                "transferable_skills": [f"{p['have']} -> {p['required']}" for p in skills["partial"][:4]],
                "years_required": experience["required"], "years_detected": experience["have"],
                "format_issues": fmt["issues"][:5],
                "missing_job_terms": keywords["missing"][:8],
                "bullets_without_metrics": weak_bullets,
            }
            prompt = (
                "You are an expert resume coach and ATS specialist. Using the analysis facts, the job description "
                "and the resume, write exactly 5 recommendations that would most improve this candidate's chances "
                "for THIS job. Each must be specific to this resume (name the skill, section or bullet), actionable, "
                "and honest - never suggest claiming skills the candidate doesn't have; say 'if you have it'. "
                "Include one rewrite of a weak bullet from the resume as 'Rewrite: \"...\" -> \"...\"' using a "
                "placeholder like [X%] where a metric is unknown. Each recommendation is 1-2 sentences.\n\n"
                f"ANALYSIS FACTS:\n{json.dumps(facts, ensure_ascii=False)}\n\n"
                f"JOB DESCRIPTION:\n{job['text'][:3500]}\n\nRESUME:\n{resume['text'][:5000]}\n\n"
                'Respond as JSON: {"recommendations": ["...", "...", "...", "...", "..."]}'
            )
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "system", "content": "You give precise, truthful, resume-specific career advice."},
                          {"role": "user", "content": prompt}],
                max_tokens=700,
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            recs = [str(r).strip() for r in data.get("recommendations", []) if str(r).strip()]
            if len(recs) >= 3:
                return recs[:5]
        except Exception as e:
            print(f"[WARN] OpenAI recommendations failed, using rule-based: {e.__class__.__name__}: {e}")
        return rule_based

    def _get_fallback_recommendations(self, resume, job, skills, keywords, experience, education, fmt,
                                      overall: float = 1.0) -> List[str]:
        recs: List[Tuple[int, str]] = []  # (priority, text) lower = more important
        role = job["title"] or "this role"
        tool_cats = {"programming_languages", "frameworks_libraries", "cloud_devops", "databases", "tools_platforms"}

        def them(items):
            return "them" if len(items) > 1 else "it"

        relevance = max(skills["score"], skills.get("semantic", 0.0))
        if overall < 0.35 and relevance < 0.3:
            background = resume["title"] or ", ".join(self._rank_resume_skills(resume)[:3]) or "your current field"
            core = ", ".join(job["required_skills"][:4]) or "the job's core requirements"
            recs.append((0, f"This role is a significant pivot from your background ({background}). It centers on "
                            f"{core}. Build and showcase projects or certifications in these areas first, or target "
                            f"roles closer to your current experience."))

        if skills["missing_required"]:
            miss = skills["missing_required"][:4]
            example_skill = next((m for m in miss if tax.CANONICAL_CATEGORY.get(m) in tool_cats), None)
            example = f" (e.g. 'Built ... using {example_skill}')" if example_skill else ""
            recs.append((0, f"The job requires {', '.join(miss)}, which your resume doesn't mention. If you have "
                            f"experience with {them(miss)}, add {them(miss)} to your Skills section and to a bullet "
                            f"that shows the result{example}."))
        for p in skills["partial"][:2]:
            recs.append((1, f"You list {p['have']} but the job asks for {p['required']}. Highlight the transferable "
                            f"experience and mention any {p['required']} exposure (courses, side projects) explicitly."))
        if skills["listed_only"]:
            lo = skills["listed_only"][:4]
            recs.append((1, f"{', '.join(lo)} appear{'s' if len(lo) == 1 else ''} only in your skills list. Add a bullet "
                            f"under a role or project showing how you used {them(lo)} - ATS and recruiters weight "
                            f"skills shown in context much higher."))

        weak = [b for b in resume["bullets"] if not self._has_metric(b)]
        n_b, q = len(resume["bullets"]), len(resume["quantified_bullets"])
        if n_b and q / n_b < 0.4:
            example = max(weak, key=lambda b: len(b) if len(b) < 140 else 0) if weak else ""
            ex = (f" For example, add the scale or result to \"{example[:100]}\" (%, users, time or money saved)."
                  if example else "")
            recs.append((1, f"Only {q} of {n_b} bullet points contain measurable results.{ex}"))

        weak_phr = resume["weak_phrases"]
        if weak_phr:
            phrase = max(weak_phr, key=weak_phr.get)
            line = next((b for b in resume["bullets"] if phrase in b.lower()), "")
            ex = f" (e.g. \"{line[:80]}\")" if line else ""
            recs.append((2, f"Replace passive phrases like '{phrase}'{ex} with an action verb and an outcome: "
                            f"'Led...', 'Reduced...', 'Delivered...'."))

        if experience["score"] is not None and experience["score"] < 1.0:
            recs.append((1, f"{role} asks for {experience['required']:g}+ years of experience and ~{experience['have']:g} "
                            f"were detected. Make sure every relevant role, internship and freelance project has clear "
                            f"dates, and emphasize scope and ownership to offset the gap."))
        if education["score"] is not None and education["score"] < 1.0:
            recs.append((2, f"The job asks for a {DEGREE_LEVELS[education['required']]} degree. "
                            + ("List your degree with its full name (e.g. 'Bachelor of Science in ...') so ATS detects it."
                               if resume["education_level"] == 0 else
                               "Highlight certifications and practical experience that demonstrate equivalent knowledge.")))

        if skills["missing_preferred"] and overall >= 0.45:
            pref = skills["missing_preferred"][:4]
            recs.append((2, f"Nice-to-have skills you could add if you have them: {', '.join(pref)}. "
                            f"Even brief project or course experience counts."))

        if keywords["missing"] and keywords["score"] < 0.6 and overall >= 0.35:
            recs.append((2, f"Use the job's own terminology where it's accurate for you: "
                            f"{', '.join(keywords['missing'][:6])}."))

        if overall >= 0.45:
            if not resume["sections"].get("summary"):
                top = (job["required_skills"] or skills["matched"])[:3]
                recs.append((2, f"Add a 2-3 line summary aimed at {role}" +
                                (f" that leads with {', '.join(top)}." if top else ".")))
            elif job["title"] and job["title"].lower() not in resume["text"].lower():
                recs.append((3, f"Mention the target title '{job['title']}' in your summary - recruiters search by title."))

        for issue, suggestion in zip(fmt["issues"], fmt["suggestions"]):
            if "measurable" in issue or "Passive" in issue:
                continue
            recs.append((3, suggestion))

        if not recs:
            recs.append((3, "Your resume is well aligned. Tailor the top third (summary + most recent role) to the "
                            "job's top 3 requirements and keep every bullet outcome-focused."))
        recs.sort(key=lambda r: r[0])
        out, seen = [], set()
        for _, text in recs:
            if text not in seen:
                seen.add(text)
                out.append(text)
        return out[:5]


# Create singleton instance
advanced_ats_scorer = AdvancedATSScorer()
