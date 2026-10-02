"""
MongoDB-backed job catalog.

Instead of calling the job APIs on every request, jobs are fetched on a daily
rotating schedule (see JobService.run_refresh), stored here with their skills
pre-extracted, and served to users from the database. Collections:

  jobs          - job postings; auto-deleted JOB_TTL_DAYS after they were last seen
  job_queries   - the rotation plan: one row per (source, market, search query)
  api_usage     - calls made per source per day, used to stay within API quotas

If MongoDB is unreachable every method degrades gracefully (empty results /
in-memory counters) so the app keeps working with live searches.
"""

import asyncio
import math
import re
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from pymongo import UpdateOne

from backend.config import settings
from backend.database import get_database


# Search queries refreshed on rotation. Broad on purpose: user-specific searches
# that aren't covered here are added automatically by the live fallback.
ROTATION_ROLES = [
    # Software & data
    "software engineer", "python developer", "java developer", "frontend developer", "react developer",
    "backend developer", "full stack developer", "node js developer", "android developer", "ios developer",
    "flutter developer", "devops engineer", "cloud engineer", "site reliability engineer", "data engineer",
    "data analyst", "data scientist", "machine learning engineer", "ai engineer", "nlp engineer",
    "computer vision engineer", "qa automation engineer", "software tester", "cyber security analyst",
    "network engineer", "system administrator", "database administrator", "ui ux designer",
    "product manager", "project manager", "business analyst", "salesforce developer", "sap consultant",
    "embedded engineer", "game developer", "technical support engineer", "software engineer intern",
    "data science intern", "graduate trainee",
    # Other functions
    "digital marketing", "content writer", "sales executive", "business development executive",
    "accountant", "financial analyst", "hr executive", "recruiter", "customer support",
    "graphic designer", "operations manager", "nurse", "teacher", "mechanical engineer",
    "civil engineer", "electrical engineer",
]

CITY_ALIASES = {
    "bangalore": ["bangalore", "bengaluru"], "bengaluru": ["bangalore", "bengaluru"],
    "mumbai": ["mumbai", "bombay", "navi mumbai", "thane"], "delhi": ["delhi", "new delhi", "noida", "gurgaon", "gurugram", "ncr"],
    "gurgaon": ["gurgaon", "gurugram"], "gurugram": ["gurgaon", "gurugram"], "noida": ["noida"],
    "chennai": ["chennai", "madras"], "hyderabad": ["hyderabad", "secunderabad"], "pune": ["pune"],
    "kolkata": ["kolkata", "calcutta"], "ahmedabad": ["ahmedabad"], "kochi": ["kochi", "cochin"],
}
COUNTRY_NAMES = {
    "in": ["india"], "us": ["united states", "usa", "us"], "gb": ["united kingdom", "uk", "england", "london"],
    "ca": ["canada"], "au": ["australia"], "de": ["germany"], "sg": ["singapore"], "nl": ["netherlands"],
    "fr": ["france"], "ae": ["uae", "dubai"],
}
_REMOTE_RE = re.compile(r"\bremote\b|\banywhere\b|\bwork from home\b|\bwfh\b|\bworldwide\b", re.IGNORECASE)


def parse_markets(spec: str) -> List[Tuple[str, str]]:
    """'in,in:Bangalore,us' -> [('in', ''), ('in', 'Bangalore'), ('us', '')]"""
    markets = []
    for part in (spec or "").split(","):
        part = part.strip()
        if not part:
            continue
        country, _, where = part.partition(":")
        markets.append((country.strip().lower(), where.strip()))
    return markets


class QuotaTracker:
    """
    Counts external API calls per source and enforces the per-minute, per-day,
    per-week, per-month and lifetime limits from settings. Counts persist in
    MongoDB (api_usage); week/month windows take the stricter of the calendar
    and rolling interpretation, since providers don't always say which they use.
    """

    def __init__(self, store: "JobStore"):
        self.store = store
        self._memory: Dict[str, int] = defaultdict(int)  # fallback when MongoDB is down
        self._recent: Dict[str, deque] = defaultdict(deque)

    @staticmethod
    def limits(source: str) -> Dict[str, int]:
        if source == "adzuna":
            return {"minute": settings.ADZUNA_LIMIT_MINUTE, "day": settings.ADZUNA_LIMIT_DAY,
                    "week": settings.ADZUNA_LIMIT_WEEK, "month": settings.ADZUNA_LIMIT_MONTH}
        if source == "jooble":
            return {"day": settings.JOOBLE_LIMIT_DAY, "total": settings.JOOBLE_LIMIT_TOTAL}
        if source == "remotive":
            return {"day": settings.REMOTIVE_LIMIT_DAY}
        return {}

    async def usage(self, source: str) -> Dict[str, int]:
        now = datetime.utcnow()
        today = now.date()
        days: Dict[str, int] = {}
        total = None
        if await self.store.available():
            try:
                coll = self.store.db["api_usage"]
                since = (now - timedelta(days=40)).strftime("%Y-%m-%d")
                async for doc in coll.find({"source": source, "day": {"$gte": since}}):
                    days[doc["day"]] = doc.get("count", 0)
                if "total" in self.limits(source):
                    agg = await coll.aggregate([{"$match": {"source": source}},
                                                {"$group": {"_id": None, "n": {"$sum": "$count"}}}]).to_list(1)
                    total = agg[0]["n"] if agg else 0
            except Exception as e:
                print(f"[WARN] Quota read failed, using in-memory counts: {e}")
                days = {}
        for key, count in self._memory.items():
            src, _, day = key.partition("|")
            if src == source:
                days[day] = max(days.get(day, 0), count)

        def used_since(d):
            return sum(c for day, c in days.items() if day >= d.strftime("%Y-%m-%d"))

        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        return {
            "day": days.get(today.strftime("%Y-%m-%d"), 0),
            "week": max(used_since(week_start), used_since(today - timedelta(days=6))),
            "month": max(used_since(month_start), used_since(today - timedelta(days=29))),
            "total": total if total is not None else sum(days.values()),
        }

    async def remaining(self, source: str, reserves: Optional[Dict[str, int]] = None) -> int:
        # A limit of 0 means "disabled" (blocks every call); negative means "no limit"
        limits = {k: v for k, v in self.limits(source).items() if k != "minute" and v is not None and v >= 0}
        if not limits:
            return 10 ** 6
        used = await self.usage(source)
        reserves = reserves or {}
        return min(limit - used.get(window, 0) - reserves.get(window, 0) for window, limit in limits.items())

    async def acquire(self, source: str, reserves: Optional[Dict[str, int]] = None) -> bool:
        """Reserve one call. Returns False (and makes no call) when a limit would be exceeded."""
        if await self.remaining(source, reserves) <= 0:
            print(f"[INFO] {source} quota reached - skipping call")
            return False
        await self._respect_minute_limit(source)
        await self._record(source)
        return True

    async def _respect_minute_limit(self, source: str):
        per_minute = self.limits(source).get("minute")
        if not per_minute:
            return
        window = self._recent[source]
        while True:
            now = time.monotonic()
            while window and now - window[0] > 60:
                window.popleft()
            if len(window) < max(1, per_minute - 2):  # small safety margin
                window.append(now)
                return
            await asyncio.sleep(60 - (now - window[0]) + 0.5)

    async def _record(self, source: str):
        day = datetime.utcnow().strftime("%Y-%m-%d")
        self._memory[f"{source}|{day}"] += 1
        if await self.store.available():
            try:
                await self.store.db["api_usage"].update_one(
                    {"_id": f"{source}|{day}"},
                    {"$inc": {"count": 1}, "$setOnInsert": {"source": source, "day": day}},
                    upsert=True)
            except Exception as e:
                print(f"[WARN] Quota write failed: {e}")


class JobStore:
    def __init__(self):
        self._available: Optional[bool] = None
        self._checked_at = 0.0
        self._indexes_ready = False

    @property
    def db(self):
        return get_database()

    async def available(self) -> bool:
        """Cached MongoDB reachability check (re-checked every 60s after a failure)."""
        if self._available is True or (self._available is False and time.time() - self._checked_at < 60):
            return self._available
        try:
            await self.db.command("ping")
            self._available = True
            await self.ensure_indexes()
        except Exception as e:
            print(f"[WARN] Job store unavailable (MongoDB): {e.__class__.__name__}")
            self._available = False
        self._checked_at = time.time()
        return self._available

    async def ensure_indexes(self):
        if self._indexes_ready:
            return
        jobs = self.db["jobs"]
        ttl = settings.JOB_TTL_DAYS * 86400
        try:
            await jobs.create_index("fetched_at", expireAfterSeconds=ttl, name="ttl_fetched_at")
        except Exception:
            # TTL changed since the index was created: update it in place
            await self.db.command({"collMod": "jobs", "index": {"name": "ttl_fetched_at", "expireAfterSeconds": ttl}})
        await jobs.create_index("skills")
        await jobs.create_index([("country", 1), ("posted_at", -1)])
        await jobs.create_index("is_remote")
        await jobs.create_index("id")
        await self.db["job_queries"].create_index("last_fetched")
        self._indexes_ready = True

    # ---- jobs ------------------------------------------------------------

    async def upsert_jobs(self, jobs: List[Dict], query_key: Optional[str] = None) -> int:
        """Store/refresh normalized jobs (skills already extracted). Returns number written."""
        if not jobs or not await self.available():
            return 0
        now = datetime.utcnow()
        ops = []
        for job in jobs:
            if not job.get("id") or not job.get("source"):
                continue
            doc = {k: v for k, v in job.items() if not k.startswith("_")}
            doc.update({
                "skills": job.get("_skills", []),
                "text": (job.get("_text") or "")[:2500],
                "country": job.get("_country"),
                "is_remote": bool(job.get("_is_remote")),
                "posted_at": job.get("_posted_at"),
                "fetched_at": now,
            })
            update = {"$set": doc, "$setOnInsert": {"first_seen": now}}
            if query_key:
                update["$addToSet"] = {"queries": query_key}
            ops.append(UpdateOne({"_id": f"{job['source']}:{job['id']}"}, update, upsert=True))
        if not ops:
            return 0
        try:
            result = await self.db["jobs"].bulk_write(ops, ordered=False)
            return result.upserted_count + result.modified_count
        except Exception as e:
            print(f"[WARN] Storing jobs failed: {e}")
            return 0

    def _location_filter(self, location: Optional[str]) -> Dict:
        loc = (location or "").strip().lower()
        if loc in ("", "remote", "anywhere", "worldwide"):
            return {"is_remote": True}
        for code, names in COUNTRY_NAMES.items():
            if loc in names or loc == code:
                return {"country": code}
        for city, aliases in CITY_ALIASES.items():
            if city in loc:
                return {"$or": [{"location": {"$regex": "|".join(map(re.escape, aliases)), "$options": "i"}},
                                {"is_remote": True, "country": "in"}]}
        return {"location": {"$regex": re.escape(loc), "$options": "i"}}

    async def find_candidates(self, skills: List[str], roles: List[str], location: Optional[str],
                              limit: int = 300) -> List[Dict]:
        """
        Jobs sharing skills with the candidate or matching a target role title,
        pre-sorted in MongoDB by overlap so only the best few hundred are ranked in Python.
        """
        if not await self.available():
            return []
        role_words = [w for r in roles for w in re.findall(r"[a-z+#.]{3,}", r.lower())
                      if w not in {"engineer", "developer", "senior", "junior", "lead", "and"}]
        role_regex = "|".join(sorted(set(map(re.escape, role_words)))) or "a^"
        cutoff = datetime.utcnow() - timedelta(days=45)
        pipeline = [
            {"$match": {"$and": [self._location_filter(location),
                                 {"$or": [{"posted_at": {"$gte": cutoff}}, {"posted_at": None}]}]}},
            {"$addFields": {
                "_overlap": {"$size": {"$setIntersection": [{"$ifNull": ["$skills", []]}, skills]}},
                "_title_hit": {"$regexMatch": {"input": {"$ifNull": ["$title", ""]}, "regex": role_regex, "options": "i"}},
            }},
            {"$match": {"$or": [{"_overlap": {"$gte": 1}}, {"_title_hit": True}]}},
            {"$addFields": {"_pre": {"$add": ["$_overlap", {"$cond": ["$_title_hit", 3, 0]}]}}},
            {"$sort": {"_pre": -1, "posted_at": -1}},
            {"$limit": limit},
        ]
        try:
            docs = await self.db["jobs"].aggregate(pipeline).to_list(limit)
        except Exception as e:
            print(f"[WARN] Job query failed: {e}")
            return []
        return [self._to_job(d) for d in docs]

    @staticmethod
    def _to_job(doc: Dict) -> Dict:
        job = {k: v for k, v in doc.items()
               if k not in ("_id", "skills", "text", "country", "is_remote", "posted_at", "fetched_at",
                            "first_seen", "queries") and not k.startswith("_")}
        job["_skills"] = doc.get("skills") or []
        job["_text"] = doc.get("text") or ""
        job["_is_remote"] = doc.get("is_remote", False)
        return job

    async def find_by_id(self, job_id: str) -> Optional[Dict]:
        if not await self.available():
            return None
        doc = await self.db["jobs"].find_one({"id": str(job_id)})
        return self._to_job(doc) if doc else None

    async def recent_jobs(self, limit: int = 10, location: Optional[str] = None) -> List[Dict]:
        if not await self.available():
            return []
        docs = await self.db["jobs"].find(self._location_filter(location) if location else {}) \
            .sort("posted_at", -1).limit(limit).to_list(limit)
        return [{k: v for k, v in self._to_job(d).items() if not k.startswith("_")} for d in docs]

    async def skills_demand(self, top: int = 40) -> Tuple[List[Tuple[str, int]], int]:
        if not await self.available():
            return [], 0
        total = await self.db["jobs"].estimated_document_count()
        rows = await self.db["jobs"].aggregate([
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills", "n": {"$sum": 1}}},
            {"$sort": {"n": -1}},
            {"$limit": top},
        ]).to_list(top)
        return [(r["_id"], r["n"]) for r in rows], total

    async def stats(self) -> Dict:
        if not await self.available():
            return {"available": False}
        jobs = self.db["jobs"]
        by_source = await jobs.aggregate([{"$group": {"_id": "$source", "n": {"$sum": 1}}}]).to_list(20)
        return {
            "available": True,
            "total_jobs": await jobs.estimated_document_count(),
            "by_source": {r["_id"]: r["n"] for r in by_source},
            "queries_in_rotation": await self.db["job_queries"].estimated_document_count(),
        }

    # ---- rotation plan ----------------------------------------------------

    @staticmethod
    def query_key(source: str, country: str, where: str, query: str) -> str:
        return f"{source}|{country}|{where.lower()}|{query.lower()}"

    async def ensure_plan(self, markets: List[Tuple[str, str]]):
        if not await self.available():
            return
        ops = []
        for country, where in markets:
            for role in ROTATION_ROLES:
                key = self.query_key("adzuna", country, where, role)
                ops.append(UpdateOne({"_id": key}, {"$setOnInsert": {
                    "source": "adzuna", "country": country, "where": where, "query": role,
                    "last_fetched": None, "last_count": 0, "demand": 0, "created_at": datetime.utcnow()}},
                    upsert=True))
        if ops:
            await self.db["job_queries"].bulk_write(ops, ordered=False)

    async def add_demand(self, source: str, country: str, where: str, query: str, fetched: bool):
        """Record a user-driven search so future refreshes keep it fresh."""
        if not await self.available():
            return
        update = {"$inc": {"demand": 1}, "$setOnInsert": {
            "source": source, "country": country, "where": where, "query": query.lower(),
            "created_at": datetime.utcnow(), "last_count": 0}}
        if fetched:
            update["$set"] = {"last_fetched": datetime.utcnow()}
        else:
            update["$setOnInsert"]["last_fetched"] = None
        await self.db["job_queries"].update_one(
            {"_id": self.query_key(source, country, where, query)}, update, upsert=True)

    async def recently_fetched(self, source: str, country: str, where: str, query: str,
                               hours: int = 24) -> bool:
        if not await self.available():
            return False
        doc = await self.db["job_queries"].find_one({"_id": self.query_key(source, country, where, query)})
        return bool(doc and doc.get("last_fetched")
                    and datetime.utcnow() - doc["last_fetched"] < timedelta(hours=hours))

    async def pick_queries(self, source: str, budget: int) -> List[Dict]:
        """Oldest (or never) fetched first, boosted by how often users searched for it."""
        if budget <= 0 or not await self.available():
            return []
        now = datetime.utcnow()
        docs = await self.db["job_queries"].find({"source": source}).to_list(5000)

        def priority(d):
            age_h = 1e6 if not d.get("last_fetched") else (now - d["last_fetched"]).total_seconds() / 3600
            return age_h * (1 + 0.5 * math.log1p(d.get("demand", 0)))

        docs = [d for d in docs if not d.get("last_fetched") or (now - d["last_fetched"]) > timedelta(hours=20)]
        return sorted(docs, key=priority, reverse=True)[:budget]

    async def mark_fetched(self, key: str, count: int):
        if await self.available():
            await self.db["job_queries"].update_one(
                {"_id": key}, {"$set": {"last_fetched": datetime.utcnow(), "last_count": count}})

    async def save_run(self, stats: Dict):
        if await self.available():
            await self.db["job_refresh_runs"].insert_one(dict(stats))

    async def last_run(self) -> Optional[Dict]:
        if not await self.available():
            return None
        doc = await self.db["job_refresh_runs"].find_one(sort=[("started_at", -1)])
        if doc:
            doc.pop("_id", None)
        return doc
