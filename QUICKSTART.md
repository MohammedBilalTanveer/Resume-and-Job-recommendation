# 🎯 QUICK REFERENCE GUIDE

## Start the Application

### Windows (Quick Start)
```powershell
# Terminal 1 - Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cd ..
uvicorn backend.main:app --reload

# Terminal 2 - Frontend (new terminal)
cd frontend
npm install
npm start
```

### Linux/Mac (Quick Start)
```bash
# Terminal 1 - Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cd ..
uvicorn backend.main:app --reload

# Terminal 2 - Frontend (new terminal)
cd frontend
npm install
npm start
```

### Docker (Easiest)
```bash
docker-compose up --build
```

---

## Access the Application

| Component | URL |
|-----------|-----|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

---

## Core Features

### 1. Upload Resume & Get ATS Score
1. Go to http://localhost:3000
2. Click "Resume Analyzer"
3. Upload a PDF resume
4. (Optional) Paste job description
5. View ATS score and analysis

### 2. Search Jobs
1. Click "Job Search" in navigation
2. Enter job title/keyword
3. Select location
4. View recommendations from multiple APIs

### 3. Train Your Own Models
```bash
python scripts/train_model.py
```
This downloads Kaggle datasets and trains ML models.

---

## API Usage Examples

### Example 1: Score a Resume
```bash
curl -X POST "http://localhost:8000/api/v1/resume/score" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python Developer with 5 years experience",
    "job_description": "Python Developer position requiring 5+ years"
  }'
```

### Example 2: Extract Skills
```bash
curl -X POST "http://localhost:8000/api/v1/resume/extract-skills" \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Python, React, AWS, Docker, PostgreSQL"}'
```

### Example 3: Search Jobs
```bash
curl "http://localhost:8000/api/v1/jobs/search?keyword=Python&location=remote"
```

### Example 4: Get Recommendations
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python Developer",
    "top_k": 5
  }'
```

---

## Environment Setup

### Set API Keys (Optional)
Create `.env` file in root directory:
```env
ADZUNA_APP_ID=your_id
ADZUNA_APP_KEY=your_key
JOOBLE_API_KEY=your_key
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Frontend Configuration
Frontend `.env` already set in `frontend/.env`

---

## Project File Locations

| What | Where |
|------|-------|
| Backend code | `backend/` |
| Frontend code | `frontend/src/` |
| ML models | `ml_models/` |
| Training scripts | `scripts/` |
| API documentation | `backend/routes/` |
| Components | `frontend/src/components/` |
| Pages | `frontend/src/pages/` |
| Configuration | `backend/config.py` |
| Dependencies | `backend/requirements.txt`, `frontend/package.json` |

---

## Common Commands

### Backend
```bash
# Run with auto-reload
uvicorn backend.main:app --reload

# Run on specific port
uvicorn backend.main:app --port 8001

# Production run (no reload)
uvicorn backend.main:app --workers 4
```

### Frontend
```bash
# Development
npm start

# Build for production
npm run build

# Test
npm test
```

### Models
```bash
# Download spaCy model
python -m spacy download en_core_web_sm

# Train models
python scripts/train_model.py

# Download Kaggle datasets
python scripts/kaggle_manager.py
```

---

## ATS Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 80-100% | Excellent Match | Apply immediately |
| 60-79% | Good Match | Tailor resume slightly |
| 40-59% | Partial Match | Update skills/experience |
| 0-39% | Poor Match | Not recommended |

---

## Features by Score Component

1. **Skill Match (40%)**
   - Exact keyword matching from 500+ skills
   - Case-insensitive matching
   - Supports skills like "Python", "React", "AWS", etc.

2. **Content Similarity (30%)**
   - TF-IDF vectorization
   - Cosine similarity calculation
   - Captures overall relevance

3. **Keyword Score (30%)**
   - Important term overlap
   - High-value keyword weighting
   - Context-based matching

---

## Job APIs Available

### Remotive (✅ Free, No Auth)
- Remote jobs
- Auto-updated daily
- ~50+ new jobs daily
- No API key needed

### Adzuna (API Key Required)
- 1M+ listings worldwide
- Multiple job types
- Salary information
- Sign up: https://developer.adzuna.com/

### Jooble (API Key Required)
- Global coverage
- Real-time updates
- Advanced filtering
- Sign up: https://jooble.org/api/about

---

## Troubleshooting

### Backend Issues
```bash
# Port 8000 in use
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Spacy model missing
python -m spacy download en_core_web_sm

# Virtual environment not activating
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
```

### Frontend Issues
```bash
# npm not found - Install Node.js 16+
# Node modules issues
rm -rf node_modules
npm install

# Port 3000 in use - check Process or change port
```

### API Connection Issues
```bash
# Test backend
curl http://localhost:8000/health

# Test API
curl http://localhost:8000/docs

# Check CORS settings
# Edit: backend/config.py
# Check: CORS_ORIGINS
```

---

## File Structure Quick Reference

```
intellidiots/
├── backend/routes/resume.py          👈 Resume upload API
├── backend/routes/jobs.py             👈 Job search API
├── backend/utils/ats_scorer.py        👈 ATS scoring logic
├── backend/services/job_service.py    👈 Job API integration
├── backend/utils/pdf_parser.py        👈 PDF parsing
├── frontend/src/pages/Analyzer.jsx    👈 Resume analyzer page
├── frontend/src/pages/Jobs.jsx        👈 Job search page
├── frontend/src/components/           👈 React components
├── ml_models/trainer.py               👈 Model training
├── scripts/train_model.py             👈 Training pipeline
├── scripts/kaggle_manager.py          👈 Dataset download
└── examples.py                         👈 API examples
```

---

## Next Steps

1. ✅ Run the application (`npm start` + backend)
2. ✅ Upload a test resume
3. ✅ Try ATS scoring with job descriptions
4. ✅ Search for jobs
5. ✅ Train models with your data
6. ✅ Deploy to production

---

## Performance Tips

### Optimize Resume Analysis
- Use clear, structured resume format
- Include relevant keywords
- Avoid overly complex formatting

### Improve ATS Score
- Match keywords from job description
- Quantify achievements
- Use industry standard terms
- Include relevant technologies

### Job Search Optimization
- Be specific with keywords
- Include location preferences
- Filter by job type
- Use industry-relevant terms

---

## Contact & Support

- **Issues?** Check README.md
- **Setup Help?** See SETUP.md
- **API Questions?** Visit http://localhost:8000/docs
- **Code Examples?** Run `python examples.py`

---

**Happy Resume Optimization! 🎉**

*Last Updated: February 2024*
*Version: 1.0.0*
