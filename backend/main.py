from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path

# Add ML models to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.routes import resume, jobs, models as model_routes, auth, history
from backend.config import settings
from backend.database import init_database, close_connections


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup: Initialize MongoDB indexes
    await init_database()
    yield
    # Shutdown: Close connections
    close_connections()


app = FastAPI(
    title="Resume ATS Scorer & Job Recommendation System",
    description="AI-powered resume analysis and job matching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(history.router, prefix="/api/v1/history", tags=["History"])
app.include_router(model_routes.router, prefix="/api/v1/models", tags=["Models"])

@app.get("/")
def read_root():
    return {
        "message": "Resume ATS Scorer & Job Recommendation System",
        "version": "1.0.0",
        "endpoints": {
            "resume": "/api/v1/resume",
            "jobs": "/api/v1/jobs",
            "models": "/api/v1/models"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
