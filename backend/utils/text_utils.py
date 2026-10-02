"""
Text helpers shared by the resume analyzer and job recommender:
normalization, section splitting, tokenization, light stemming and
date-range parsing.
"""

import html
import re
import unicodedata
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

_BULLET_CHARS = "•●▪■□◦‣∙·➢➤►▶✓✔❖◆○*"
_LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}


def normalize_text(text: str) -> str:
    """Clean text extracted from PDF/DOCX while keeping line structure."""
    if not text:
        return ""
    for lig, rep in _LIGATURES.items():
        text = text.replace(lig, rep)
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    # Unify dashes and quotes
    text = re.sub(r"[‐‑‒–—―−]", "-", text)
    text = re.sub(r"[‘’´`]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    # Normalize bullet glyphs to a single marker at line start
    text = re.sub(rf"^[ \t]*[{re.escape(_BULLET_CHARS)}][ \t]*", "• ", text, flags=re.MULTILINE)
    text = re.sub(rf"[ \t]+[{re.escape(_BULLET_CHARS)}][ \t]+", "\n• ", text)
    # Re-join words hyphenated across line breaks ("develop-\nment")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[  ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<(br|/p|/li|/div|/h\d)[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>", "\n• ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return normalize_text(text)


# ---------------------------------------------------------------------------
# Tokenization / stemming
# ---------------------------------------------------------------------------

# Words that appear in nearly every job posting and say nothing about fit.
JD_BOILERPLATE = {
    "looking", "join", "joining", "team", "teams", "role", "roles", "candidate", "candidates",
    "ideal", "nice", "plus", "bonus", "strong", "experience", "experienced", "ability", "able",
    "work", "working", "years", "year", "including", "etc", "responsibilities", "responsibility",
    "requirements", "requirement", "required", "qualifications", "qualification", "preferred",
    "skills", "skill", "knowledge", "understanding", "familiarity", "familiar", "proficiency",
    "proficient", "excellent", "good", "great", "solid", "proven", "track", "record", "demonstrated",
    "must", "should", "will", "would", "can", "may", "need", "needs", "want", "wants", "help",
    "opportunity", "opportunities", "company", "companies", "position", "job", "apply", "applicant",
    "benefits", "salary", "competitive", "equal", "employer", "inclusive", "diverse", "diversity",
    "environment", "culture", "fast", "paced", "dynamic", "passionate", "passion", "growing",
    "growth", "mission", "world", "class", "best", "new", "using", "use", "used", "related",
    "relevant", "similar", "equivalent", "field", "degree", "level", "minimum", "least", "plus",
    "highly", "desired", "desirable", "hands", "day", "days", "time", "full", "part", "remote",
    "hybrid", "onsite", "office", "location", "based", "per", "within", "across", "well", "make",
    "making", "like", "also", "every", "other", "others", "range", "wide", "variety", "various",
    "including", "include", "includes", "via", "us", "our", "we", "you", "your", "they", "their",
    "about", "who", "what", "why", "how", "senior", "junior", "mid", "lead", "staff", "principal",
    "engineer", "engineers", "developer", "developers", "manager", "specialist", "associate",
    "build", "building", "deliver", "delivering", "ensure", "ensuring", "drive", "driving",
    "support", "supporting", "own", "owning", "contribute", "contributing", "responsible",
    "collaborate", "collaborating", "closely", "partner", "partnering", "excited", "exciting",
    "love", "enjoy", "thrive", "self", "starter", "motivated", "detail", "oriented", "written",
    "verbal", "english", "fluent", "bachelor", "bachelors", "master", "masters", "phd", "bs", "ms",
    "ba", "computer", "science", "engineering", "related", "least", "eg", "ie", "e", "g", "one",
    "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "first", "high",
    "quality", "end", "key", "core", "multiple", "others", "existing", "around", "please", "send",
    "professional", "professionals", "looking", "seeking", "hiring", "join", "growing", "talented",
    "individual", "person", "someone", "member", "members", "opening", "openings", "immediate",
    "immediately", "preferably", "strongly", "proficiency", "hands-on", "real", "things", "thing",
}

# Conversational verbs/adjectives common in postings that carry no domain meaning
JD_BOILERPLATE |= {
    "loves", "loving", "crafting", "craft", "delightful", "delight", "care", "cares", "caring", "deeply",
    "deep", "turn", "turning", "run", "running", "write", "writing", "count", "counts", "expose", "exposing",
    "advanced", "complex", "simple", "awesome", "amazing", "incredible", "impactful", "meaningful", "unique",
    "innovative", "cutting", "edge", "modern", "latest", "state", "art", "leading", "industry", "world",
    "global", "large", "small", "big", "huge", "massive", "millions", "thousands", "billions", "daily",
    "challenging", "challenges", "challenge", "problems", "problem", "solve", "solving", "solutions",
    "solution", "think", "thinking", "learn", "learning", "learner", "curious", "curiosity", "eager",
    "willing", "willingness", "comfortable", "capable", "effectively", "effective", "efficiently",
    "efficient", "successfully", "success", "successful", "independently", "independent", "together",
    "ideas", "idea", "impact", "value", "values", "create", "creating", "grow", "shape", "shaping",
    "help", "helping", "bring", "bringing", "take", "taking", "get", "getting", "keep", "come",
    "go", "going", "see", "look", "find", "know", "show", "start", "starting", "set", "put",
    "give", "lot", "lots", "many", "much", "more", "most", "less", "least", "very", "really",
    "including", "especially", "particularly", "plus", "bonus", "great", "nice", "ideal", "ideally",
    "preferred", "prefer", "proven", "demonstrable", "track", "minimum", "maximum", "years", "year",
    "months", "month", "weeks", "week", "hours", "hour", "today", "tomorrow", "future", "current",
    "currently", "internship", "internships", "intern", "interns", "graduate", "graduates", "fresh",
    "freshers", "entry", "early", "career", "careers", "position", "positions", "openings",
    "products", "product", "users", "customers", "clients", "people", "everyone", "anyone",
}

STOPWORDS = set(ENGLISH_STOP_WORDS) | {"etc", "eg", "ie", "inc", "ltd", "llc", "co"}

_IRREGULAR = {
    "built": "build", "led": "lead", "ran": "run", "wrote": "write", "written": "write",
    "drove": "drive", "driven": "drive", "made": "make", "grew": "grow", "grown": "grow",
    "taught": "teach", "won": "win", "began": "begin", "spoke": "speak", "chose": "choose",
    "analyses": "analysis", "data": "data", "people": "person",
}


def stem(word: str) -> str:
    """Small, predictable suffix stripper (keeps 'mentored'/'mentoring'/'mentor' together)."""
    w = word.lower()
    if w in _IRREGULAR:
        return _IRREGULAR[w]
    if len(w) <= 4:
        return w
    for suf, rep in (("ization", "ize"), ("isation", "ize"), ("ational", "ate"), ("iveness", "ive"),
                     ("fulness", "ful"), ("ousness", "ous"), ("ments", "ment"), ("ities", "ity"),
                     ("ingly", ""), ("ically", "ic"), ("ings", ""), ("ing", ""), ("ies", "y"),
                     ("ied", "y"), ("ed", ""), ("es", ""), ("ers", "er"), ("s", "")):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: len(w) - len(suf)] + rep
            break
    # "managed" -> "manag" ; "manage" -> "manag" ; unify trailing e / doubled consonant
    if w.endswith("e") and len(w) > 4:
        w = w[:-1]
    if len(w) > 4 and w[-1] == w[-2] and w[-1] not in "aeiouls":
        w = w[:-1]
    return w


_WORD_RE = re.compile(r"[a-z][a-z0-9+#]*(?:[.\-/][a-z0-9+#]+)*")


def tokenize(text: str) -> List[str]:
    return _WORD_RE.findall(text.lower())


def content_terms(text: str, extra_stop: Optional[set] = None) -> List[str]:
    """Lowercased, stop-word filtered, stemmed tokens."""
    stop = STOPWORDS | (extra_stop or set())
    out = []
    for tok in tokenize(text):
        if len(tok) < 3 or tok in stop or tok.isdigit():
            continue
        out.append(stem(tok))
    return out


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

SECTION_ALIASES: Dict[str, List[str]] = {
    "summary": ["summary", "professional summary", "career summary", "profile", "professional profile",
                "objective", "career objective", "about me", "about", "overview", "personal statement",
                "career profile", "executive summary"],
    "experience": ["experience", "work experience", "professional experience", "employment",
                   "employment history", "work history", "career history", "relevant experience",
                   "internship", "internships", "internship experience", "professional background",
                   "industry experience", "work"],
    "education": ["education", "academic background", "academics", "academic qualifications",
                  "educational qualifications", "education and training", "qualifications",
                  "academic profile", "educational background"],
    "skills": ["skills", "technical skills", "core skills", "key skills", "skill set", "skillset",
               "competencies", "core competencies", "technologies", "tech stack", "technical expertise",
               "areas of expertise", "expertise", "tools", "tools and technologies", "technical proficiencies",
               "it skills", "computer skills", "soft skills", "skills and abilities", "skills & tools"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "selected projects",
                 "project experience", "notable projects", "side projects"],
    "certifications": ["certifications", "certificates", "licenses", "licenses and certifications",
                       "certifications and licenses", "courses", "training", "professional development",
                       "certifications & courses"],
    "achievements": ["achievements", "accomplishments", "awards", "honors", "honours", "awards and honors",
                     "key achievements", "recognition"],
    "publications": ["publications", "research", "papers", "research experience"],
    "volunteer": ["volunteer", "volunteering", "volunteer experience", "community service",
                  "extracurricular activities", "extracurriculars", "leadership", "activities",
                  "positions of responsibility"],
    "coursework": ["coursework", "relevant coursework", "courses taken", "key courses", "academic coursework"],
    "languages": ["languages", "language proficiency"],
    "interests": ["interests", "hobbies", "hobbies and interests"],
}

SECTION_TITLES = {
    "summary": "Summary", "experience": "Experience", "education": "Education", "skills": "Skills",
    "projects": "Projects", "certifications": "Certifications", "achievements": "Achievements",
    "publications": "Publications", "volunteer": "Activities", "coursework": "Coursework", "languages": "Languages",
    "interests": "Interests",
}

_ALIAS_TO_SECTION = {alias: sec for sec, aliases in SECTION_ALIASES.items() for alias in aliases}


def _header_section(line: str) -> Optional[str]:
    raw = line.strip().strip("•-:|#*_=").strip()
    if not raw or len(raw) > 45:
        return None
    key = re.sub(r"[^a-z& ]", "", raw.lower()).replace("&", "and").strip()
    key = re.sub(r"\s+", " ", key)
    if key in _ALIAS_TO_SECTION:
        return _ALIAS_TO_SECTION[key]
    key2 = key.replace(" and ", " & ")
    return _ALIAS_TO_SECTION.get(key2)


def split_sections(text: str) -> Dict[str, str]:
    """
    Split resume text into canonical sections. Text before the first header
    is stored under "header" (usually name + contact info).
    Headers like "SKILLS: Python, SQL" (header + content on one line) are supported.
    """
    sections: Dict[str, List[str]] = {"header": []}
    current = "header"
    for line in text.split("\n"):
        stripped = line.strip()
        sec = _header_section(stripped)
        inline_content = ""
        if sec is None and ":" in stripped[:40]:
            head, _, rest = stripped.partition(":")
            sec = _header_section(head)
            inline_content = rest.strip() if sec else ""
        if sec is not None:
            current = sec
            sections.setdefault(current, [])
            if inline_content:
                sections[current].append(inline_content)
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip() or k != "header"}


# ---------------------------------------------------------------------------
# Bullets
# ---------------------------------------------------------------------------

_BULLET_START = re.compile(r"^(?:•|[-*>]|\d{1,2}[.)])\s+(?=\S)")
_ROLE_LINE = re.compile(r"\b(?:19|20)\d{2}\b|\bpresent\b|\s\|\s", re.IGNORECASE)


def extract_bullets(text: str) -> List[str]:
    """
    Return achievement bullets. PDF extraction wraps long bullets over several
    lines, so continuation lines are merged back into the bullet they belong to.
    Lines without a bullet marker count when they read like sentences.
    """
    bullets: List[str] = []
    current: Optional[str] = None
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            if current:
                bullets.append(current)
            current = None
            continue
        if _BULLET_START.match(s):
            if current:
                bullets.append(current)
            current = _BULLET_START.sub("", s)
            continue
        is_role_line = bool(_ROLE_LINE.search(s)) and len(s.split()) <= 14
        continues = current is not None and not is_role_line and (
            s[0].islower() or s[0] in "(&,%" or not re.search(r"[.!?:]$", current))
        if continues and len(s.split()) <= 25 and _header_like(s) is False:
            current = f"{current} {s}"
            continue
        if current:
            bullets.append(current)
            current = None
        if len(s.split()) >= 7 and not is_role_line:
            current = s
    if current:
        bullets.append(current)
    return [b.strip() for b in bullets if len(b.split()) >= 3]


def _header_like(line: str) -> bool:
    """Short title-case / ALL CAPS lines are role or company names, not bullet text."""
    words = line.split()
    if len(words) > 6:
        return False
    if line.isupper():
        return True
    caps = sum(1 for w in words if w[:1].isupper())
    return caps == len(words) and len(words) >= 2 and not line.endswith((".", ","))


# ---------------------------------------------------------------------------
# Date ranges -> experience
# ---------------------------------------------------------------------------

_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3, "apr": 4, "april": 4,
    "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7, "aug": 8, "august": 8, "sep": 9, "sept": 9,
    "september": 9, "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
_MONTH_RE = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sept?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?"
_DATE_RE = rf"(?:{_MONTH_RE}\s*,?\s*(?:19|20)\d{{2}}|(?:0?[1-9]|1[0-2])\s*[/.\-]\s*(?:19|20)\d{{2}}|(?:19|20)\d{{2}}\s*[/.\-]\s*(?:0?[1-9]|1[0-2])(?!\d)|(?:19|20)\d{{2}})"
_END_RE = rf"(?:{_DATE_RE}|present|current|currently|now|today|ongoing|till date|to date|date)"
DATE_RANGE_RE = re.compile(rf"({_DATE_RE})\s*(?:-|to|until|till|~|→|->)\s*({_END_RE})", re.IGNORECASE)


def _parse_date(s: str, is_end: bool) -> Optional[Tuple[int, int]]:
    s = s.strip().lower().rstrip(".")
    now = datetime.now()
    if s in {"present", "current", "currently", "now", "today", "ongoing", "till date", "to date", "date"}:
        return now.year, now.month
    m = re.match(rf"({_MONTH_RE})\s*,?\s*((?:19|20)\d{{2}})", s)
    if m:
        key = m.group(1).rstrip(".")
        mon = _MONTHS.get(key) or _MONTHS.get(key[:3])
        return int(m.group(2)), mon or 1
    m = re.match(r"(\d{1,2})\s*[/.\-]\s*((?:19|20)\d{2})", s)
    if m:
        return int(m.group(2)), int(m.group(1))
    m = re.match(r"((?:19|20)\d{2})\s*[/.\-]\s*(\d{1,2})", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"((?:19|20)\d{2})", s)
    if m:
        # Year-only: assume Jan for starts and Dec for ends (capped at today)
        y = int(m.group(1))
        if is_end:
            return (y, 12) if y < now.year else (now.year, now.month)
        return y, 1
    return None


def date_ranges(text: str) -> List[Tuple[int, int]]:
    """Return (start_month_index, end_month_index) intervals found in text."""
    now = datetime.now()
    now_idx = now.year * 12 + now.month
    out = []
    for m in DATE_RANGE_RE.finditer(text):
        a = _parse_date(m.group(1), False)
        b = _parse_date(m.group(2), True)
        if not a or not b:
            continue
        s, e = a[0] * 12 + a[1], b[0] * 12 + b[1]
        e = min(e, now_idx)
        if 1970 * 12 <= s <= e and e - s <= 50 * 12:
            out.append((s, e))
    return out


def merged_months(intervals: List[Tuple[int, int]]) -> int:
    """Total months covered by intervals, counting overlaps once."""
    if not intervals:
        return 0
    intervals = sorted(intervals)
    total = 0
    cs, ce = intervals[0]
    for s, e in intervals[1:]:
        if s <= ce + 1:
            ce = max(ce, e)
        else:
            total += ce - cs + 1
            cs, ce = s, e
    total += ce - cs + 1
    return total
