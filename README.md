# � Career Pilot - AI-Powered Resume & Job Matching Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

**Career Pilot** is a comprehensive full-stack AI-powered web application that analyzes resumes, provides detailed ATS (Applicant Tracking System) scores, and recommends personalized job opportunities. Built with cutting-edge machine learning and natural language processing technologies.

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-application-architecture)
- [Complete Application Flow](#-complete-application-flow)
- [Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Requirements](#-system-requirements)
- [Installation & Setup](#-installation--setup)
- [API Endpoints](#-api-endpoints-documentation)
- [Frontend Components](#-frontend-structure)
- [ML/AI Pipeline](#-mlai-pipeline)
- [Database Schema](#-database-schema)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🎯 Project Overview

**Career Pilot** (Intellidiots) is an intelligent career companion that bridges the gap between job seekers and employers. It leverages advanced AI algorithms to:

- 📄 **Parse & Analyze Resumes**: Extract structured data from PDF, DOCX, and TXT files
- 🎯 **Calculate ATS Scores**: ML-powered matching between resumes and job descriptions with detailed scoring
- 💼 **Recommend Jobs**: Personalized job suggestions based on extracted skills and experience
- 📊 **Skill Analysis**: Market trends and skill demand insights
- 🔍 **Multi-Source Job Search**: Aggregate jobs from Remotive, Adzuna, and Jooble APIs
- 🔐 **User Authentication**: Secure OAuth integration (Google, GitHub) + JWT tokens

### What Sets Career Pilot Apart:
✅ **Multi-Algorithm ATS Scoring** - Ensemble of Random Forest, Gradient Boosting, and Neural Networks  
✅ **AI-Powered Recommendations** - OpenAI integration for smart improvement suggestions  
✅ **Real-Time Job Integration** - Search 3 major job boards simultaneously  
✅ **Skill Categorization** - Automatic categorization of technical and soft skills  
✅ **Format Analysis** - ATS-friendly document structure validation  
✅ **Historical Tracking** - Save and compare multiple resumes

---

## 🏗️ Application Architecture

### System Overview Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React 18)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Pages: Home, Login, Analyzer, Jobs, History          │  │
│  │ Components: Resume Upload, ATS Analysis, Job Lists   │  │
│  │ State: Zustand (Auth, Resume Data, Job Results)      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬──────────────────────────────────┘
                          │ Axios HTTP Requests
                          │ (CORS: http://localhost:3000)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                 BACKEND (FastAPI + Uvicorn)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Routes Layer:                                        │  │
│  │  • /api/v1/auth      (Authentication & OAuth)       │  │
│  │  • /api/v1/resume    (Upload & ATS Analysis)        │  │
│  │  • /api/v1/jobs      (Job Search & Recommendations) │  │
│  │  • /api/v1/history   (Saved Analyses)               │  │
│  │  • /api/v1/models    (Model Management)             │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Service Layer:                                       │  │
│  │  • JobService (Multi-API Job Aggregation)           │  │
│  │  • AuthService (JWT + OAuth Handling)               │  │
│  │  • ResumeService (File Parsing & Storage)           │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ML/AI Layer:                                         │  │
│  │  • AdvancedATSScorer (Ensemble Models)              │  │
│  │  • pdf_parser (Multi-format Resume Extraction)      │  │
│  │  • model_manager (Model Loading & Inference)        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬──────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌─────────────┐   ┌──────────────┐   ┌──────────────┐
│  MongoDB    │   │  ML Models   │   │ External     │
│  Database   │   │ (PyTorch,    │   │ Job APIs     │
│             │   │  scikit-learn)   │              │
│ Collections:│   │              │   │ • Remotive   │
│ • users     │   │ • RF Model   │   │ • Adzuna     │
│ • resumes   │   │ • GB Model   │   │ • Jooble     │
│ • jobs      │   │ • NN Model   │   │              │
│ • history   │   │ • Vectorizer │   │ OpenAI API   │
└─────────────┘   │ • Scalers    │   │ (GPT Models) │
                  └──────────────┘   └──────────────┘
```

---

## 🔄 Complete Application Flow

### User Journey - From Resume to Job Recommendations

#### **Phase 1: Authentication & Landing**
```
┌─────────────────────────────────────────────────────┐
│ 1. User visits http://localhost:3000                │
│    ↓                                                 │
│ 2. Home Page displayed (Features, How-it-works)     │
│    ↓                                                 │
│ 3. User clicks "Get Started" → Signup/Login page    │
│    ↓                                                 │
│ 4. Authentication Options:                          │
│    • Email/Password Signup (POST /api/v1/auth/signup)│
│    • Google OAuth (GET /api/v1/auth/google/login)   │
│    • GitHub OAuth (GET /api/v1/auth/github/login)   │
│    ↓                                                 │
│ 5. JWT tokens stored in Zustand + localStorage      │
│    Access Token + Refresh Token issued              │
│ └─────────────────────────────────────────────────────┘
```

#### **Phase 2: Resume Upload & Initial Analysis**
```
┌─────────────────────────────────────────────────────┐
│ 1. User navigates to "/analyzer" (ProtectedRoute)   │
│    ↓                                                 │
│ 2. Sees ResumeUpload component with:                │
│    • File drag-drop zone                            │
│    • Supported formats (PDF, DOCX, TXT)             │
│    • Optional job description textarea              │
│    ↓                                                 │
│ 3. User uploads resume file                         │
│    ↓                                                 │
│ 4. Frontend sends: POST /api/v1/resume/upload       │
│    FormData: {                                       │
│      file: File,                                    │
│      job_description?: string                       │
│    }                                                 │
│ └─────────────────────────────────────────────────────┘
```

#### **Phase 3: Backend Resume Processing**
```
┌─────────────────────────────────────────────────────┐
│ Backend: /api/v1/resume/upload                      │
│                                                      │
│ 1. Validate file type (PDF|DOCX|TXT)               │
│    ↓                                                │
│ 2. Save uploaded file to ./uploads/ (MultipartFile) │
│    ↓                                                │
│ 3. Parse resume using pdf_parser:                   │
│    • PDF: pdfplumber → extract all text              │
│    • DOCX: python-docx → extract paragraphs         │
│    • TXT: Plain file read                           │
│    ↓                                                │
│ 4. Extract resume data:                             │
│    • Contact info (email, phone, linkedin)          │
│    • Skills (categorized: lang, frameworks, cloud)  │
│    • Experience years (regex from text)             │
│    • Education (degree extraction)                  │
│    • Resume sections (structure analysis)           │
│    • Action verbs (leadership keywords)             │
│    ↓                                                │
│ 5. IF job_description provided:                     │
│    a. Call advanced_ats_scorer.comprehensive_analysis()
│    b. Run ML ensemble scoring (RF + GB + NN)        │
│    c. Calculate match percentages                   │
│    d. Generate recommendations                      │
│    ↓                                                │
│ 6. Return to frontend: {                            │
│      filename, resume_text,                         │
│      [ats_analysis | extracted_info]                │
│    }                                                │
│ └─────────────────────────────────────────────────────┘
```

#### **Phase 4: ATS Score Calculation (ML Pipeline)**
```
┌─────────────────────────────────────────────────────┐
│ AdvancedATSScorer.comprehensive_analysis()          │
│                                                      │
│ INPUT: resume_text, job_description                 │
│                                                      │
│ STEP 1: Text Preprocessing                          │
│  ├─ Lowercase & normalize both texts                │
│  ├─ Remove special characters                       │
│  └─ Tokenize into sentences                         │
│     ↓                                                │
│ STEP 2: Skill Matching (Manual + ML)               │
│  ├─ Extract skills from resume (against database)   │
│  ├─ Extract skills from job description             │
│  ├─ Calculate skill match percentage                │
│  ├─ Apply skill category weights:                   │
│  │  • data_science: 1.5x                            │
│  │  • web_frameworks: 1.2x                          │
│  │  • other skills: 1.0x                            │
│  └─ Skill score = (matched/required) × weight       │
│     ↓                                                │
│ STEP 3: Semantic Similarity (TF-IDF + Cosine)      │
│  ├─ Vectorize both texts using TF-IDF              │
│  ├─ Calculate cosine_similarity between vectors     │
│  ├─ Normalize to 0-100 scale                        │
│  └─ Semantic score = similarity × 100               │
│     ↓                                                │
│ STEP 4: Format & Structure Analysis                 │
│  ├─ Check for ATS-friendly sections                │
│  ├─ Count action verbs (leadership keywords)        │
│  ├─ Calculate readability score                     │
│  ├─ Check for proper formatting                     │
│  └─ Format compliance score                         │
│     ↓                                                │
│ STEP 5: ML Model Ensemble Scoring                   │
│  ├─ Feature extraction (TF-IDF vectors)             │
│  ├─ Random Forest prediction                        │
│  ├─ Gradient Boosting prediction                    │
│  ├─ Neural Network prediction (if available)        │
│  ├─ Weighted ensemble average (30% RF + 30% GB + 40% NN)  │
│  └─ ML score = ensemble output × 100                │
│     ↓                                                │
│ STEP 6: Final ATS Score Calculation                 │
│  ├─ Apply weights:                                  │
│  │  • Skill matching: 40%                           │
│  │  • Semantic similarity: 30%                       │
│  │  • ML model score: 20%                           │
│  │  • Format compliance: 10%                        │
│  └─ FINAL_SCORE = weighted_sum                      │
│     ↓                                                │
│ STEP 7: Gap Analysis & Recommendations              │
│  ├─ Identify missing required skills                │
│  ├─ Generate improvement suggestions                │
│  ├─ AI-powered advice (OpenAI if available)         │
│  └─ Priority-based recommendations                  │
│     ↓                                                │
│ OUTPUT: {                                            │
│   overall_score: 0-100,                             │
│   skill_score: 0-100,                               │
│   semantic_similarity: 0-100,                       │
│   format_compliance: 0-100,                         │
│   ml_score: 0-100,                                  │
│   matched_skills: [...],                           │
│   missing_skills: [...],                           │
│   recommendations: [...],                          │
│   improvement_tips: [...]                          │
│ }                                                    │
│ └─────────────────────────────────────────────────────┘
```

#### **Phase 5: Frontend Display ATS Results**
```
┌─────────────────────────────────────────────────────┐
│ AdvancedResumeAnalysis Component displays:          │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │ Overall ATS Score: 78/100 [Circular Gauge] │    │
│ │ ✅ Good Match - You're a strong candidate! │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │ Score Breakdown:                            │    │
│ │ • Skill Match: 85/100 [Progress Bar]        │    │
│ │ • Semantic Match: 72/100                    │    │
│ │ • ML Model Score: 75/100                    │    │
│ │ • Format Compliance: 90/100                 │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │ Matched Skills (28 found):                  │    │
│ │ [Python badge] [React badge] [AWS badge]   │    │
│ │ [Docker badge] [PostgreSQL badge] ...       │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │ Missing Skills (12 required):               │    │
│ │ ⚠️ Kubernetes, Azure, Go, GraphQL           │    │
│ └─────────────────────────────────────────────┘    │
│                                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │ Top Recommendations:                        │    │
│ │ 1. Add Azure knowledge to your resume       │    │
│ │ 2. Highlight your ML/AI experience more     │    │
│ │ 3. Include specific project metrics         │    │
│ │ 4. Emphasize leadership achievements        │    │
│ └─────────────────────────────────────────────┘    │
│ └─────────────────────────────────────────────────────┘
```

#### **Phase 6: Job Recommendations**
```
┌─────────────────────────────────────────────────────┐
│ User navigates to "/jobs" page                      │
│                                                      │
│ Option A: Get Recommendations (Auto from resume)    │
│  1. Frontend: POST /api/v1/jobs/recommend            │
│     {resume_text, top_k: 5, location?: string}      │
│     ↓                                                │
│  2. Backend extracts skills from resume             │
│     ↓                                                │
│  3. Job Service searches using extracted skills:    │
│     • Query: "Python React AWS Engineer"            │
│     • Simultaneously search: Remotive + Adzuna       │
│     ↓                                                │
│  4. Deduplicate results (same company, similar job) │
│     ↓                                                │
│  5. Return top 5 matching jobs                       │
│                                                      │
│ Option B: Manual Job Search                         │
│  1. Frontend: GET /api/v1/jobs/search?keyword=...   │
│     {keyword, location, job_type, source}           │
│     ↓                                                │
│  2. Query specified job APIs:                        │
│     • Remotive (free, remote jobs)                   │
│     • Adzuna (if API keys configured)                │
│     • Jooble (if API keys configured)                │
│     ↓                                                │
│  3. Return aggregated results                        │
│ └─────────────────────────────────────────────────────┘
```

#### **Phase 7: Job Matching & Match Score**
```
┌─────────────────────────────────────────────────────┐
│ User clicks "Match Resume to This Job"              │
│                                                      │
│ Frontend: POST /api/v1/jobs/match-resume-to-job    │
│ {resume_text, job_description}                      │
│     ↓                                                │
│ Backend calls advanced_ats_scorer again             │
│     ↓                                                │
│ Returns detailed match analysis:                    │
│ • Match percentage                                  │
│ • Matched skills                                    │
│ • Missing skills                                    │
│ • Specific recommendations for THIS job             │
│ └─────────────────────────────────────────────────────┘
```

#### **Phase 8: History & Persistence**
```
┌─────────────────────────────────────────────────────┐
│ User navigates to "/history" page                   │
│                                                      │
│ Backend: GET /api/v1/history/                       │
│  1. Query MongoDB: all resumes for user_id          │
│  2. Query MongoDB: all analysis records for user    │
│  3. Return list with:                               │
│     • Resume filename, upload date                  │
│     • Associated job descriptions analyzed          │
│     • ATS scores from each analysis                 │
│     • Creation date, last accessed                  │
│     ↓                                                │
│ Frontend displays:                                  │
│  • Timeline of submissions                          │
│  • Score trends                                     │
│  • Ability to re-open and compare analyses          │
│  • Delete/archive old submissions                   │
│ └─────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 1. **Resume Processing**
- 📄 Support for PDF, DOCX, and TXT formats
- 🎯 Intelligent text extraction with OCR-ready structure
- 📊 Automatic categorization of resume sections
- 🔍 Structured data extraction (contact, experience, education)

### 2. **ATS Scoring Engine**
- 🤖 **Ensemble ML Models**: Random Forest + Gradient Boosting + Neural Networks
- 🎓 **Skill Matching**: Database of 80+ skills across 7 categories
- 📈 **Semantic Analysis**: TF-IDF vectorization + cosine similarity
- ✍️ **Format Validation**: ATS-friendly document structure checking
- 🏆 **Multi-factor Scoring**: Weighted combination of 4 scoring algorithms

### 3. **Job Recommendations**
- 🔗 **Multi-API Integration**: Remotive + Adzuna + Jooble
- 🎯 **Smart Matching**: Skills-based job suggestions
- 🌍 **Location-based Search**: Remote and location-specific options
- 🚫 **Deduplication**: Eliminate duplicate postings from multiple boards
- 💼 **Rich Job Data**: Title, company, description, salary, posting date

### 4. **Skill Analysis**
- 🏷️ **Skill Categorization**: 7 categories (Programming, Frameworks, Cloud, etc.)
- 📊 **Gap Analysis**: Identify missing required skills
- 💡 **Recommendations**: Personalized improvement suggestions
- 🔑 **Action Verbs**: Leadership keyword extraction

### 5. **Authentication & Authorization**
- 🔐 **OAuth Integration**: Google & GitHub sign-up/login
- 🎫 **JWT Tokens**: Access token + refresh token system
- 🛡️ **Password Security**: bcrypt hashing + passlib validation
- 👤 **User Profiles**: Persistent user data in MongoDB

### 6. **AI-Powered Insights**
- 🧠 **OpenAI Integration**: GPT-powered recommendations (optional)
- 💬 **Natural Language Analysis**: Context-aware improvement tips
- 🎯 **Smart Suggestions**: Prioritized remediations based on impact

### 7. **History & Tracking**
- 📜 **Save Analyses**: All resume submissions saved with timestamps
- 📊 **Score Trends**: Track improvements over time
- 🔄 **Comparison**: View and compare multiple submissions
- 🗂️ **Organized Management**: Archive or delete old submissions

---

## 💻 Tech Stack

### Frontend Technologies
```
Framework              React 18.2.0
Build Tool            react-scripts 5.0.1
Styling               Tailwind CSS 3.3.6 + PostCSS
State Management      Zustand 4.4.5
HTTP Client           Axios 1.6.2
Routing               React Router v6
Charts                Recharts 2.10.0
Icons                 React Icons 4.12.0
PDF Viewing           react-pdf 10.3.0
HTML Sanitization     DOMPurify 3.3.1
UI Components         Lucide React 0.563.0
```

### Backend Technologies
```
Framework             FastAPI 0.104.1
Server               Uvicorn (ASGI) 0.24.0
Data Validation      Pydantic 2.5.0
File Upload          python-multipart 0.0.6
Environment Config   python-dotenv 1.0.0

ML/Data Science:
  Machine Learning   scikit-learn 1.3.2
  Deep Learning      PyTorch 2.5.1
  Transformers       transformers 4.35.2
  Sentence Embedding sentence-transformers 2.2.2
  NLP                NLTK 3.8.1
  Numerical          NumPy 1.26.2, Pandas 2.1.3

PDF Processing:
  PDF Parsing        PyPDF2 3.0.1, pdfplumber 0.10.3
  DOCX Processing    python-docx 0.8.11

External APIs:
  Async HTTP         aiohttp 3.9.1, httpx 0.25.1
  REST Requests      requests 2.31.0
  OpenAI             openai >= 1.0.0

Database:
  MongoDB Driver     motor 3.3.2, pymongo 4.6.1

Security & Auth:
  JWT Tokens         python-jose 3.3.0
  Password Hashing   passlib 1.7.4, bcrypt 4.1.1
  Image Processing   Pillow 10.1.0

Logging:
  JSON Logging       python-json-logger 2.0.7
```

### ML Models & Algorithms
```
Scoring Algorithms    TF-IDF Vectorization + Cosine Similarity
ML Models            Random Forest + Gradient Boosting
Deep Learning        PyTorch Neural Networks (4-layer feedforward)
Word Embeddings      Sentence Transformers
Text Processing      spaCy, NLTK
```

### DevOps & Deployment
```
Containerization     Docker
Orchestration        Docker Compose
Hosting (Optional)   Render.com, Heroku, AWS, Azure
```

---

## 📋 System Requirements

### Minimum Requirements:
- **CPU**: Dual-core processor (4-core recommended for ML models)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 2GB free space (for models and uploads)
- **Python**: 3.9 or higher
- **Node.js**: 16.x or higher
- **Internet**: Required for external APIs

### Recommended (for optimal performance):
- **CPU**: 4+ cores (GPU recommended for neural networks)
- **RAM**: 16GB+
- **Python**: 3.11+
- **Node.js**: 18+
- **CUDA**: 11.8+ (for GPU acceleration)

---

## 🚀 Installation & Setup

### Prerequisites
```bash
# Required installations:
# 1. Python 3.9+
python --version

# 2. Node.js 16+
node --version
npm --version

# 3. Git
git --version
```

### Option 1: Docker Compose (Recommended - Fastest)

```bash
# Navigate to project directory
cd c:\Users\moham\OneDrive\Desktop\intellidiots\intellidiots

# Build and start services
docker-compose up --build

# Access URLs:
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
# ReDoc:     http://localhost:8000/redoc
```

**Troubleshooting Docker:**
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Clean rebuild
docker-compose down -v
docker-compose up --build
```

### Option 2: Local Development Setup

#### Backend Setup

```powershell
# Terminal 1: Backend Setup
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
# OR on macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLP models (spaCy)
python -m spacy download en_core_web_sm

# Create .env file (copy from .env.example)
# Add your API keys here

# Run backend server
cd ..
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Server runs at: http://localhost:8000
# API Docs at: http://localhost:8000/docs
```

#### Frontend Setup

```powershell
# Terminal 2: Frontend Setup
cd frontend

# Install dependencies
npm install

# Create .env file (if n
3eeded)
# REACT_APP_API_URL=http://localhost:8000/api/v1

# Start development server
npm start

# Frontend runs at: http://localhost:3000
# Auto-reload on code changes
```

#### Database Setup (Optional - MongoDB)

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# OR install MongoDB locally and start service
# Windows: mongod.exe
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod

# Verify MongoDB connection
python -c "from motor.motor_asyncio import AsyncClient; print('✓ MongoDB ready')"
```

### Option 3: Train Custom ML Models

```bash
# Setup Kaggle API
# 1. Get API token from https://www.kaggle.com/settings/account
# 2. Place kaggle.json in ~/.kaggle/ directory

# Set environment variables for Kaggle (Windows PowerShell)
$env:KAGGLE_USERNAME = "your-kaggle-username"
$env:KAGGLE_KEY = "your-api-key"

# Navigate to project
cd c:\Users\moham\OneDrive\Desktop\intellidiots\intellidiots

# Train models (this will take 30+ minutes)
python scripts/train_model.py

# Models saved to: ml_models/
#  ├── rf_model.pkl           (Random Forest)
#  ├── gb_model.pkl           (Gradient Boosting)
#  ├── nn_model.pth           (Neural Network)
#  ├── vectorizer.pkl         (TF-IDF Vectorizer)
#  └── scaler.pkl             (Feature Scaler)
```

---

## 🔌 API Endpoints Documentation

### Base URL
```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

### Authentication Endpoints

#### Sign Up (Email/Password)
```http
POST /auth/signup
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_verified": false
  }
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "securePassword123"
}

Response (200 OK):
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {...}
}
```

#### Google OAuth Login
```http
GET /auth/google/login

# Redirects to Google OAuth consent screen
# After approval, redirects back with authorization code
# Frontend handles callback at: /auth/callback/google
```

#### GitHub OAuth Login
```http
GET /auth/github/login

# Redirects to GitHub OAuth authorization
# After approval, redirects back with code
# Frontend handles callback at: /auth/callback/github
```

#### Refresh Token
```http
POST /auth/refresh-token
Content-Type: application/json

Request:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

Response (200 OK):
{
  "access_token": "new-access-token...",
  "token_type": "bearer"
}
```

---

### Resume Upload & Analysis Endpoints

#### Upload Resume
```http
POST /resume/upload
Content-Type: multipart/form-data
Authorization: Bearer {access_token}

Form Data:
  - file: <PDF|DOCX|TXT file>
  - job_description: (optional) "Senior Software Engineer, 5+ years..."

Response (200 OK):
{
  "filename": "my_resume.pdf",
  "resume_text": "John Doe\nSoftware Engineer...",
  "ats_analysis": {
    "overall_score": 78,
    "skill_score": 85,
    "semantic_similarity": 72,
    "format_compliance": 90,
    "ml_score": 75,
    "matched_skills": ["Python", "React", "Docker", "PostgreSQL"],
    "missing_skills": ["Kubernetes", "Azure"],
    "recommendations": [
      "Add Kubernetes experience",
      "Highlight cloud architecture projects"
    ]
  }
  # OR
  "extracted_info": {
    "skills": [...],
    "skills_by_category": {...},
    "experience_years": 8,
    "education": ["BS Computer Science"],
    "contact_info": {...},
    "sections": [...],
    "action_verbs": [...]
  }
}
```

#### Score Resume Against Job
```http
POST /resume/score
Content-Type: application/json
Authorization: Bearer {access_token}

Request:
{
  "resume_text": "John Doe\nSoftware Engineer...",
  "job_description": "We seek a Senior Python Developer with 5+ years experience..."
}

Response (200 OK):
{
  "overall_score": 82,
  "skill_score": 88,
  "semantic_similarity": 78,
  "format_compliance": 92,
  "ml_score": 79,
  "matched_skills": [...],
  "missing_skills": [...],
  "recommendations": [...],
  "improvement_tips": [...]
}
```

#### Extract Skills
```http
POST /resume/extract-skills
Content-Type: application/json
Authorization: Bearer {access_token}

Request:
{
  "resume_text": "John Doe\nPython Expert with 10 years...\nDocker, Kubernetes, AWS..."
}

Response (200 OK):
{
  "skills": ["Python", "Docker", "Kubernetes", "AWS", "React"],
  "skills_by_category": {
    "programming_languages": ["Python"],
    "cloud_devops": ["Docker", "Kubernetes", "AWS"],
    "frameworks_libraries": ["React"]
  },
  "experience_years": 10,
  "education": ["BS Computer Science"],
  "contact_info": {...},
  "sections": ["Experience", "Education", "Skills"],
  "action_verbs": ["Developed", "Implemented", "Architected"]
}
```

---

### Job Endpoints

#### Search Jobs
```http
GET /jobs/search?keyword=Python&location=remote&source=remotive
Authorization: Bearer {access_token}

Query Parameters:
  - keyword (required):  "Python Developer", "React Engineer"
  - location (optional): "remote", "new york", "san francisco"
  - job_type (optional): "full-time", "contract", "part-time"
  - source (optional):   "remotive", "adzuna", "jooble" (default: all)

Response (200 OK):
{
  "keyword": "Python",
  "location": "remote",
  "total_jobs": 125,
  "jobs": [
    {
      "id": "remotive_12345",
      "title": "Senior Python Developer",
      "company": "TechCorp",
      "location": "Remote",
      "description": "We're looking for...",
      "url": "https://remotive.com/remote-jobs/...",
      "type": "Full-time",
      "posted_date": "2024-04-05",
      "source": "remotive",
      "salary": "$120,000 - $150,000"
    },
    ...
  ]
}
```

#### Get Job Recommendations
```http
POST /jobs/recommend
Content-Type: application/json
Authorization: Bearer {access_token}

Request:
{
  "resume_text": "John Doe\nPython Developer...",
  "top_k": 5,
  "location": "remote"
}

Response (200 OK):
{
  "extracted_skills": ["Python", "React", "Docker", "AWS"],
  "total_recommendations": 5,
  "jobs": [
    {
      "id": "...",
      "title": "Senior Python Engineer",
      "company": "StartupXYZ",
      ...
    },
    ...
  ]
}
```

#### Match Resume to Job
```http
POST /jobs/match-resume-to-job
Content-Type: application/json
Authorization: Bearer {access_token}

Request:
{
  "resume_text": "John Doe\nPython Developer...",
  "job_description": "Senior Python Developer needed..."
}

Response (200 OK):
{
  "match_score": 82,
  "matched_skills": [...],
  "missing_skills": [...],
  "job_evaluation": {
    "skill_fit": "Excellent",
    "experience_fit": "Good",
    "format_fit": "Very Good"
  },
  "recommendations": [...]
}
```

---

### History Endpoints

#### Get User History
```http
GET /history/
Authorization: Bearer {access_token}

Response (200 OK):
{
  "total_submissions": 12,
  "submissions": [
    {
      "id": "history_123",
      "resume_filename": "resume_v3.pdf",
      "upload_date": "2024-04-05T10:30:00Z",
      "analyses": [
        {
          "job_title": "Senior Python Developer",
          "score": 82,
          "date": "2024-04-05T10:35:00Z"
        }
      ]
    },
    ...
  ]
}
```

#### Delete History Entry
```http
DELETE /history/{history_id}
Authorization: Bearer {access_token}

Response (200 OK):
{
  "message": "History entry deleted successfully"
}
```

---

### Model Management Endpoints

#### Get Model Status
```http
GET /models/status
Authorization: Bearer {access_token}

Response (200 OK):
{
  "models_loaded": {
    "random_forest": true,
    "gradient_boosting": true,
    "neural_network": false,
    "vectorizer": true
  },
  "ml_pipeline_ready": true,
  "gpu_available": false
}
```

#### Force Model Reload
```http
POST /models/reload
Authorization: Bearer {access_token}

Response (200 OK):
{
  "message": "Models reloaded successfully",
  "status": "ready"
}
```

---

### Health & System Endpoints

#### Health Check
```http
GET /health

Response (200 OK):
{
  "status": "healthy",
  "timestamp": "2024-04-05T10:30:00Z"
}
```

#### API Root
```http
GET /

Response (200 OK):
{
  "message": "Resume ATS Scorer & Job Recommendation System",
  "version": "1.0.0",
  "endpoints": {
    "resume": "/api/v1/resume",
    "jobs": "/api/v1/jobs",
    "models": "/api/v1/models"
  }
}
```

---

### API Documentation
- **Interactive Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🎨 Frontend Components Structure

### Page Components (`/frontend/src/pages/`)
```
Home.jsx                  - Landing page with features, testimonials, CTA
Login.jsx                 - Email/password + OAuth login form
Signup.jsx                - User registration page
Analyzer.jsx              - Resume upload & ATS analysis display
Jobs.jsx                  - Job search & recommendations interface
History.jsx               - View past submissions & analyses
AuthCallback.jsx          - OAuth provider callback handler
```

### UI Components (`/frontend/src/components/`)
```
Navigation.jsx            - Top navigation bar with logo & menu
ProtectedRoute.jsx        - Route guard for authenticated pages
ResumeUpload.jsx          - File upload widget with drag-drop
AdvancedResumeAnalysis.jsx - Display ATS scores & analysis results
ResumeAnalysis.jsx        - Resume structure visualization
Common.jsx                - Reusable utility components
Footer.jsx                - Footer with links & info
JobRecommendations.jsx    - Job recommendations list & filtering
SkillsDemand.jsx          - Market skills trends & demand charts
```

### Home Sub-components (`/frontend/src/components/home/`)
```
Hero.jsx                  - Hero section with main CTA
Features.jsx              - Key features showcase
HowItWorks.jsx            - Step-by-step workflow explanation
HowItHelps.jsx            - Benefits for users
Testimonials.jsx          - User testimonials
CTA.jsx                   - Final call-to-action section
```

### State Management (`/frontend/src/store/`)
```
authStore.js              - Authentication state (Zustand)
  ├─ User data
  ├─ Tokens (access, refresh)
  ├─ Auth methods (signup, login, logout)
  └─ OAuth handlers

index.js                  - Main store export (if additional stores)
```

### API Client (`/frontend/src/api/`)
```
client.js                 - Axios instance
  ├─ Base URL configuration
  ├─ Request/Response interceptors
  ├─ Auth token injection
  └─ Error handling
```

---

## 🧠 ML/AI Pipeline Deep Dive

### Skill Database Structure
```python
SKILLS_DATABASE = {
    "programming_languages": {
        "python", "java", "javascript", "typescript", "c++", ...
    },
    "frameworks_libraries": {
        "react", "angular", "Vue", "django", "fastapi", ...
    },
    "cloud_devops": {
        "aws", "azure", "gcp", "docker", "kubernetes", ...
    },
    "databases": {
        "postgresql", "mongodb", "redis", "elasticsearch", ...
    },
    "data_science_ai": {
        "machine learning", "tensorflow", "pytorch", ...
    },
    "soft_skills": {
        "leadership", "communication", "teamwork", ...
    },
    "tools_platforms": {
        "git", "github", "jira", "figma", ...
    }
}
```

### ATS Scoring Algorithm Flow
```
┌─────────────────────────────────────┐
│ Input: Resume + Job Description     │
└──────────────┬──────────────────────┘
               │
        ┌──────┴───────┬──────────────────────┬─────────────────┐
        │              │                      │                 │
        ▼              ▼                      ▼                 ▼
   Skill Match    Semantic Sim          Format Check      ML Models
   ┌────────┐   ┌──────────┐          ┌─────────┐      ┌──────────┐
   │Database│   │TF-IDF    │          │Structure│      │RF | GB   │
   │Match   │   │Vectorize │          │Check    │      │+ NN      │
   │        │   │Cosine    │          │         │      │          │
   │Score   │   │Similarity│          │Format   │      │Ensemble  │
   │85%     │   │72%       │          │Score    │      │75%       │
   │        │   │          │          │90%      │      │          │
   └────────┘   └──────────┘          └─────────┘      └──────────┘
        │              │                      │                 │
        └──────────────┴──────────────────────┴─────────────────┘
                       │
                       │ Weighted Combination
                       │ 40% + 30% + 10% + 20%
                       │
                   ┌───▼────┐
                   │ Final  │
                   │ Score: │
                   │ 78/100 │
                   └────────┘
```

### Neural Network Architecture
```
Input Layer (500 features)
    │
    ├─► Dense(256 neurons) → ReLU → Dropout(0.3)
    │
    ├─► Dense(128 neurons) → ReLU → Dropout(0.2)
    │
    ├─► Dense(64 neurons) → ReLU
    │
    └─► Dense(1 neuron) → Sigmoid
        │
        └─► Output: Score (0-1, scaled to 0-100)
```

### Model Training Pipeline (if you run train_model.py)
```
1. Data Loading
   ├─ Download Kaggle resume + job matching datasets
   ├─ Parse CSV files
   └─ Split: 70% train, 15% val, 15% test

2. Feature Engineering
   ├─ Concatenate resume + job description
   ├─ TF-IDF vectorization (500 features)
   ├─ Create binary labels (match: 1, no-match: 0)
   └─ Normalize features using StandardScaler

3. Model Training
   ├─ Random Forest: 100 trees, max_depth=15
   ├─ Gradient Boosting: 100 estimators, lr=0.1
   └─ Neural Network: 4 layers with dropout

4. Validation & Evaluation
   ├─ Cross-validation (5-fold)
   ├─ Metrics: Accuracy, Precision, Recall, F1
   └─ Generate performance plots

5. Model Serialization
   ├─ Save as pkl files (RF, GB, scaler)
   ├─ Save as pth file (NN)
   └─ Save vectorizer for later use
```

---

## 💾 Database Schema

### MongoDB Collections

#### Users Collection
```javascript
{
  _id: ObjectId,
  email: "user@example.com",
  full_name: "John Doe",
  password_hash: "bcrypt_hash_here",
  avatar_url: "https://...",
  oauth_provider: "google" | "github" | null,
  oauth_id: "sub_123456",
  is_verified: false,
  created_at: ISODate("2024-04-05T10:00:00Z"),
  last_login: ISODate("2024-04-05T14:30:00Z"),
  preferences: {
    theme: "dark",
    notifications_enabled: true
  }
}
```

#### Resumes Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  filename: "my_resume.pdf",
  original_filename: "John_Doe_Resume.pdf",
  file_path: "/uploads/my_resume.pdf",
  file_size: 145000,
  file_type: "pdf",
  resume_text: "John Doe\nSenior Software Engineer...",
  extracted_data: {
    name: "John Doe",
    email: "john@example.com",
    phone: "+1-555-123-4567",
    skills: ["Python", "React", "Docker"],
    experience_years: 8,
    education: ["BS Computer Science"],
    sections: ["Experience", "Education", "Skills"]
  },
  uploaded_at: ISODate("2024-04-05T10:00:00Z"),
  updated_at: ISODate("2024-04-05T14:30:00Z")
}
```

#### ATS Analyses Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  resume_id: ObjectId,
  job_description: "Senior Python Developer needed...",
  job_title: "Senior Python Developer",
  company_name: "TechCorp",
  analysis_date: ISODate("2024-04-05T10:30:00Z"),
  scores: {
    overall_score: 78,
    skill_score: 85,
    semantic_similarity: 72,
    format_compliance: 90,
    ml_score: 75
  },
  skill_analysis: {
    matched_skills: ["Python", "React", "Docker"],
    missing_skills: ["Kubernetes", "GraphQL"],
    skill_count: {
      matched: 28,
      required: 40
    }
  },
  recommendations: [
    "Add Kubernetes experience to resume",
    "Highlight cloud architecture projects"
  ],
  ai_insights: "Based on your resume...",
  matching_jobs: [
    {
      job_id: "remotive_12345",
      title: "Senior Python Engineer",
      match_score: 82
    }
  ]
}
```

#### Job Listings Collection
```javascript
{
  _id: ObjectId,
  source: "remotive" | "adzuna" | "jooble",
  external_id: "remotive_12345",
  title: "Senior Python Developer",
  company: "TechCorp",
  location: "Remote",
  country: "US",
  job_type: "Full-time",
  seniority: "Senior",
  description: "We're looking for a talented Python developer...",
  required_skills: ["Python", "FastAPI", "Docker"],
  salary: {
    min: 120000,
    max: 150000,
    currency: "USD"
  },
  url: "https://remotive.com/remote-jobs/...",
  posted_date: ISODate("2024-04-05T09:00:00Z"),
  expires_date: ISODate("2024-05-05T09:00:00Z"),
  crawled_at: ISODate("2024-04-05T10:00:00Z")
}
```

#### Job History Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  action: "view" | "apply" | "save" | "delete",
  job_id: ObjectId,
  resume_id: ObjectId,
  match_score: 0-100,
  action_date: ISODate("2024-04-05T14:30:00Z"),
  notes: "Applied for this position"
}
```

#### Audit Log Collection (Optional)
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  action: "resume_upload" | "ats_analysis" | "login" | "logout",
  details: {...},
  ip_address: "192.168.1.100",
  user_agent: "Mozilla/5.0...",
  timestamp: ISODate("2024-04-05T14:30:00Z")
}
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Backend Configuration
PYTHONUNBUFFERED=1

# API Configuration
API_TITLE="Career Pilot - Resume ATS Scorer"
API_VERSION="1.0.0"

# Security
SECRET_KEY="your-super-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:8000"]

# Database - MongoDB
MONGODB_URL="mongodb://localhost:27017"
MONGODB_DB_NAME="career_pilot"

# External OAuth Providers
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
FRONTEND_URL="http://localhost:3000"

# External APIs for Job Search
ADZUNA_APP_ID="your-adzuna-app-id"
ADZUNA_APP_KEY="your-adzuna-api-key"
JOOBLE_API_KEY="your-jooble-api-key"

# OpenAI (for AI-powered recommendations)
OPENAI_API_KEY="sk-your-openai-api-key"

# File Upload
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_EXTENSIONS=["pdf", "txt", "docx"]
UPLOAD_FOLDER="./uploads"

# ML Models
MODEL_FOLDER="./ml_models"

# Kaggle (for training models)
KAGGLE_USERNAME="your-kaggle-username"
KAGGLE_KEY="your-kaggle-api-key"
```

### Frontend Configuration (.env)

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENV=development

# Optional: Analytics, etc.
REACT_APP_VERSION=$npm_package_version
```

---

## 🌐 Deployment

### Deploy to Render.com (Recommended)

1. **Create Render Account**: https://dashboard.render.com

2. **Connect Repository**
   - Push code to GitHub
   - Connect your GitHub account to Render

3. **Deploy Backend (Web Service)**
   ```
   - Name: career-pilot-backend
   - Runtime: Python 3.11
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
   - Environment Variables: (Add all .env variables)
   ```

4. **Deploy Frontend (Static Site)**
   ```
   - Name: career-pilot-frontend
   - Build Command: npm run build
   - Publish Directory: frontend/build
   - Environment Variables:
     - REACT_APP_API_URL=https://your-backend-url/api/v1
   ```

5. **Configure MongoDB Atlas** (for production database)
   - Go to https://www.mongodb.com/cloud/atlas
   - Create cluster
   - Update `MONGODB_URL` in Render env vars

### Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create career-pilot-backend

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set GOOGLE_CLIENT_ID=...

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Deploy to AWS (ECS + Fargate)

```bash
# Create ECR repository
aws ecr create-repository --repository-name career-pilot

# Build and push Docker image
docker build -t career-pilot .
docker tag career-pilot:latest {aws_account}.dkr.ecr.us-east-1.amazonaws.com/career-pilot:latest
docker push {aws_account}.dkr.ecr.us-east-1.amazonaws.com/career-pilot:latest

# Create ECS service (use AWS Console or CLI)
aws ecs create-service --cluster career-pilot --service-name backend --task-definition career-pilot:1 --desired-count 1
```

---

## 🤝 Contributing

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/yourusername/career-pilot.git
cd career-pilot

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes, commit
git commit -m "Add amazing feature"

# Push & create pull request
git push origin feature/amazing-feature
```

### Code Standards
- **Python**: Follow PEP-8, use type hints
- **JavaScript**: Use ES6+, follow Airbnb style guide
- **Comments**: Describe the "why", not the "what"
- **Testing**: Write tests for new features
- **Documentation**: Update README for API changes

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue**: "ModuleNotFoundError: No module named 'backend'"
```bash
# Solution: Run from project root, not backend folder
cd /path/to/project
uvicorn backend.main:app --reload
```

**Issue**: "CORS error when calling API"
```bash
# Solution: Check CORS_ORIGINS in backend/config.py
# Add your frontend URL to the list
CORS_ORIGINS = ["http://localhost:3000", "https://yourfrontend.com"]
```

**Issue**: "Cannot connect to MongoDB"
```bash
# Solution: Start MongoDB or update connection string
docker run -d -p 27017:27017 --name mongodb mongo:latest
# Update MONGODB_URL in .env
```

**Issue**: "ML Models not loading"
```bash
# Solution: Train models first
python scripts/train_model.py
# Or check model folder exists: ./ml_models/
```

### Get Help
- 📧 Email: support@careerpilot.example.com
- 🐛 Report Issues: https://github.com/yourusername/career-pilot/issues
- 💬 Chat Support: Visit our website

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

##📊 System Requirements

**Minimum:**
- Python 3.9+
- Node.js 16+
- 4GB RAM
- 2GB disk space

**Recommended:**
- Python 3.10+
- Node.js 18+
- 8GB RAM
- 5GB disk space (with ML models)

---

## 📁 Project Architecture

### Directory Structure
```
intellidiots/
├── backend/                          # FastAPI REST API
│   ├── main.py                      # Entry point
│   ├── config.py                    # Configuration
│   ├── requirements.txt             # Dependencies
│   ├── routes/
│   │   ├── resume.py               # Resume endpoints
│   │   ├── jobs.py                 # Job endpoints
│   │   └── models.py               # Model endpoints
│   ├── services/
│   │   └── job_service.py          # Job API integration
│   └── utils/
│       ├── pdf_parser.py           # File parsing
│       ├── ats_scorer.py           # Scoring logic
│       ├── advanced_ats_scorer.py  # Advanced scoring
│       └── model_manager.py        # ML model manager
│
├── frontend/                        # React + Tailwind
│   ├── package.json                # Dependencies
│   ├── tailwind.config.js          # Tailwind config
│   ├── src/
│   │   ├── App.jsx                 # Main component
│   │   ├── index.jsx               # Entry point
│   │   ├── api/client.js           # API client
│   │   ├── store/index.js          # State management
│   │   ├── components/             # React components
│   │   │   ├── ResumeUpload.jsx
│   │   │   ├── ResumeAnalysis.jsx
│   │   │   ├── JobRecommendations.jsx
│   │   │   ├── SkillsDemand.jsx
│   │   │   ├── Navigation.jsx
│   │   │   └── Common.jsx
│   │   └── pages/                  # Page views
│   │       ├── Home.jsx
│   │       ├── Analyzer.jsx
│   │       └── Jobs.jsx
│   └── public/index.html           # HTML template
│
├── ml_models/                       # Machine Learning
│   ├── trainer.py                  # Training script
│   ├── rf_model.pkl                # Random Forest
│   ├── gb_model.pkl                # Gradient Boosting
│   ├── nn_model.pth                # Neural Network
│   └── vectorizer.pkl              # TF-IDF vectorizer
│
├── scripts/                         # Utility scripts
│   ├── train_model.py              # Training pipeline
│   └── kaggle_manager.py           # Kaggle integration
│
├── data/                            # Datasets
│   └── training_data.csv           # Training data
│
├── uploads/                         # User uploads
│
├── docker-compose.yml              # Docker setup
├── Dockerfile.backend              # Backend container
├── Dockerfile.frontend             # Frontend container
└── .env                            # Environment variables
```

---

## 🎨 Key Features Explained

### 1. Resume Upload & Parsing
**Location**: `backend/routes/resume.py` + `backend/utils/pdf_parser.py`

**Capabilities**:
- Upload PDF, DOCX, or TXT files
- Automatic text extraction
- Parse contact info, experience, education
- Extract dates, locations, job titles

**How it works**:
```javascript
// Frontend
POST /api/v1/resume/upload -> FormData with file

// Backend
1. Receive file
2. Use PyPDF2/pdfplumber for PDF parsing
3. Use python-docx for DOCX parsing
4. Return extracted text
```

### 2. ATS Scoring Algorithm
**Location**: `backend/utils/ats_scorer.py`

**Scoring Components** (100% total):
- **40%**: Skill matching (does resume contain job skills?)
- **30%**: Content similarity (TF-IDF + cosine similarity)
- **30%**: Keyword matching (exact keyword presence)

**Example Calculation**:
```
Resume: "Python developer with AWS experience"
Job Description: "Python, AWS, Docker, Kubernetes"

Skill Match (40%): Python ✓, AWS ✓ = 2/4 = 50% → 20 points
Content Match (30%): TF-IDF cosine similarity = 75% → 22.5 points
Keyword Match (30%): 2/4 keywords found = 50% → 15 points

Total Score: 20 + 22.5 + 15 = 57.5%
```

### 3. Skill Extraction
**Location**: `backend/utils/ats_scorer.py`

**Process**:
1. Extract all words from resume
2. Match against skill dictionary (500+ skills)
3. Categorize into 7 categories:
   - Programming Languages
   - Frameworks & Libraries
   - Databases
   - Cloud Services
   - Tools & Platforms
   - Soft Skills
   - Other Technologies

### 4. Job Recommendations
**Location**: `backend/services/job_service.py`

**Three Job APIs Integrated**:

**Remotive** (Free - No Auth)
- Endpoint: https://remotive.com/api/remote-jobs
- Returns: Job title, company, location, salary, description
- Limit: 50 results per query

**Adzuna** (Requires API Key)
- Endpoint: https://api.adzuna.com/v1/api/jobs
- Returns: 1,000,000+ job listings
- Credentials: APP_ID, APP_KEY
- Get at: https://developer.adzuna.com/

**Jooble** (Requires API Key)
- Endpoint: https://jooble.org/api/
- Global coverage
- Credentials: API_KEY
- Get at: https://api.jooble.org/

**Deduplication**: Same job posted to multiple locations = removed duplicates

### 5. Machine Learning Models
**Location**: `ml_models/trainer.py`

**Three Models**:
1. **Random Forest Classifier** - Fast, distributed trees
2. **Gradient Boosting Classifier** - Higher accuracy
3. **PyTorch Neural Network** - Deep learning approach

---

## 📡 API Endpoints Reference

### Resume Endpoints

**POST** `/api/v1/resume/upload`
```bash
curl -X POST "http://localhost:8000/api/v1/resume/upload" -F "file=@resume.pdf"
```

**POST** `/api/v1/resume/score`
```bash
curl -X POST "http://localhost:8000/api/v1/resume/score" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python developer...",
    "job_description": "Seeking Python expert..."
  }'
```

**POST** `/api/v1/resume/extract-skills`
```bash
curl -X POST "http://localhost:8000/api/v1/resume/extract-skills" \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Python, React, AWS"}'
```

### Job Endpoints

**GET** `/api/v1/jobs/search?keyword=python&location=remote`
- Search jobs from all 3 APIs

**POST** `/api/v1/jobs/recommend`
- Get personalized job recommendations

**GET** `/api/v1/jobs/trending`
- Get trending jobs in market

**GET** `/api/v1/jobs/skills-demand`
- Get most in-demand skills

### Health Endpoints

**GET** `/health` - Backend health check

**GET** `/` - API info

---

## 🔧 Complete Installation & Setup Guide

### Step 1: Install System Dependencies

**Windows Installation**:

1. **Python 3.10+**
   - Download: https://www.python.org/downloads/
   - Click "Add Python to PATH" during install
   - Verify: Open PowerShell and run `python --version`
   - Expected: `Python 3.10.x` or higher

2. **Node.js 16+**
   - Download: https://nodejs.org/ (LTS version)
   - Install with default options
   - Verify: Open new PowerShell and run `node --version`
   - Expected: `v16.x.x` or higher

3. **Git** (for version control)
   - Download: https://git-scm.com/
   - Use default installation

4. **Docker Desktop** (optional, for containerization)
   - Download: https://www.docker.com/products/docker-desktop
   - Install and restart computer
   - Verify: `docker --version` in PowerShell

**Linux/Mac Installation** (using Homebrew on Mac):
```bash
# Mac
brew install python@3.10 node git docker

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 nodejs npm git docker.io

# Verify
python3 --version
node --version
git --version
docker --version
```

### Step 2: Clone or Extract Project

```powershell
# Navigate to your projects folder
cd c:\Users\moham\OneDrive\Desktop\intellidiots\intellidiots

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"
```

### Step 3: Create Environment Variables File

Create `.env` file in root directory with all credentials:

```env
# ========== JOB API CREDENTIALS (OPTIONAL) ==========
# Get from: https://developer.adzuna.com/
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_APP_KEY=your_adzuna_app_key_here

# Get from: https://api.jooble.org/
JOOBLE_API_KEY=your_jooble_api_key_here

# Remotive doesn't require authentication (free)

# ========== OPENAI (OPTIONAL - for advanced features) ==========
OPENAI_API_KEY=your_openai_api_key_here

# ========== FRONTEND CONFIGURATION ==========
# This tells React where the backend is located
REACT_APP_API_URL=http://localhost:8000/api/v1

# ========== DATABASE (OPTIONAL - for data persistence) ==========
# Local MongoDB
MONGODB_URI=mongodb://localhost:27017/intellidiots

# Or MongoDB Atlas (cloud)
# MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/intellidiots

# ========== JWT SECURITY ==========
# Generate a secure random string for JWT tokens
JWT_SECRET=your_very_secret_key_change_this_in_production

# ========== APPLICATION SETTINGS ==========
DEBUG=false
ENVIRONMENT=development
```

### Step 4: Backend Installation (Detailed)

**Open PowerShell and follow these steps:**

```powershell
# Navigate to backend directory
cd c:\Users\moham\OneDrive\Desktop\intellidiots\intellidiots\backend

# Step 4a: Create Python virtual environment
# This creates an isolated Python environment for this project
python -m venv venv
# You should see a new "venv" folder created

# Step 4b: Activate virtual environment
# On Windows:
venv\Scripts\activate
# You should see (venv) at the beginning of your PowerShell prompt

# On Linux/Mac:
# source venv/bin/activate

# Step 4c: Install Python dependencies
# This installs all required packages listed in requirements.txt
pip install --upgrade pip  # Update pip first (optional but recommended)
pip install -r requirements.txt
# This takes 2-5 minutes. You'll see lots of "Successfully installed" messages

# Step 4d: Download spaCy NLP model
# This downloads the English language model for natural language processing
python -m spacy download en_core_web_sm
# You should see "Successfully installed en_core_web_sm"

# Step 4e: Go back to project root
cd ..

# Step 4f: Start the backend server
# The server will be available at http://localhost:8000
uvicorn backend.main:app --reload --port 8000
```

**You should see output like**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Keep this terminal open. Don't close it.**

### Step 5: Frontend Installation (New PowerShell)

**Open a NEW PowerShell window and follow:**

```powershell
# Navigate to frontend directory
cd c:\Users\moham\OneDrive\Desktop\intellidiots\intellidiots\frontend

# Step 5a: Install Node dependencies
# This downloads all required npm packages
npm install
# This takes 2-3 minutes. You'll see lots of activity.

# Step 5b: Start the React development server
# The app will open automatically in your browser
npm start
```

**You should see**:
```
Compiled successfully!

You can now view resume-ats-frontend in the browser.

  Local:            http://localhost:3000
```

**Browser should open automatically to http://localhost:3000**

### Step 6: Verify Everything is Working

**Check Backend**:
```powershell
# In a new PowerShell window, test the backend
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Or visit in browser:
# http://localhost:8000/docs (Interactive API documentation)
```

**Check Frontend**:
- Browser should show home page with "Resume Analyzer" button
- No red errors in browser console (F12 → Console tab)

**Both running?** ✅ You're ready to use the app!

---

## 🔄 Complete Data & System Flow

### User Journey Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER UPLOADS RESUME                       │
│                  (PDF/DOCX/TXT file)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  FRONTEND (React)           │
        │  ResumeUpload.jsx           │
        │  1. Validate file type/size │
        │  2. Create FormData         │
        │  3. Send to backend         │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  BACKEND (FastAPI)          │
        │  POST /api/v1/resume/upload │
        │  1. Receive FormData        │
        │  2. Save file to uploads/   │
        │  3. Parse PDF/DOCX/TXT      │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  FILE PARSING               │
        │  backend/utils/pdf_parser.py│
        │  1. Use PyPDF2 for PDF      │
        │  2. Use python-docx for DOC │
        │  3. Extract raw text        │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  SKILL EXTRACTION            │
        │  backend/utils/ats_scorer.py │
        │  1. Clean text               │
        │  2. Match 500+ skills        │
        │  3. Categorize by type       │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  RETURN TO FRONTEND          │
        │  Extracted: text, skills,    │
        │  contact info, experience    │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  FRONTEND DISPLAY            │
        │  ResumeAnalysis.jsx          │
        │  Show extracted data in      │
        │  user-friendly format        │
        └────────────────────────────┘
```

### ATS Scoring Flow

```
┌─────────────────────────────────────────────────────────────┐
│        USER ENTERS JOB DESCRIPTION OR PASTES TEXT           │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────┐
  │  FRONTEND                         │
  │  POST /api/v1/resume/score        │
  │  Send: resume_text + job_desc     │
  └────────┬─────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────┐
  │    BACKEND ATS SCORER             │
  │  backend/utils/ats_scorer.py      │
  │                                   │
  │  ┌─ SKILL MATCHING (40%)           │
  │  │  1. Extract skills from resume  │
  │  │  2. Extract skills from job     │
  │  │  3. Count matching skills       │
  │  │  4. Calculate percentage        │
  │  │                                 │
  │  ├─ CONTENT SIMILARITY (30%)       │
  │  │  1. Vectorize resume (TF-IDF)   │
  │  │  2. Vectorize job (TF-IDF)      │
  │  │  3. Calculate cosine similarity │
  │  │  4. Get percentage match        │
  │  │                                 │
  │  └─ KEYWORD MATCHING (30%)         │
  │     1. Count job keywords in resume│
  │     2. Calculate percentage        │
  │                                   │
  │  FINAL SCORE = (40% × s) + (30% × c) + (30% × k)
  └────────┬──────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────┐
  │  RETURN RESULTS TO FRONTEND       │
  │  - Score (0-100%)                 │
  │  - Matching skills                │
  │  - Missing skills                 │
  │  - Score breakdown                │
  └────────┬──────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────┐
  │  DISPLAY TO USER                  │
  │  - Circular progress with score   │
  │  - Green: matching keywords       │
  │  - Red: missing keywords          │
  │  - Detailed breakdown             │
  └──────────────────────────────────┘
```

### Job Recommendation Flow

```
┌─────────────────────────────────────────────────────────────┐
│        USER CLICKS "GET RECOMMENDATIONS"                    │
│        With: resume text + location + top_k                 │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
  ┌──────────────────────────────────┐
  │  FRONTEND                         │
  │  POST /api/v1/jobs/recommend      │
  └────────┬──────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────────────────────────┐
  │    BACKEND JOB SERVICE                               │
  │  backend/services/job_service.py                     │
  │                                                      │
  │  ┌─ REMOTIVE API (Concurrent)                       │
  │  │  URL: https://remotive.com/api/remote-jobs       │
  │  │  Returns: Job listings with descriptions         │
  │  │                                                   │
  │  ├─ ADZUNA API (Concurrent)                         │
  │  │  URL: https://api.adzuna.com/v1/api/jobs         │
  │  │  Returns: Job listings with descriptions         │
  │  │                                                   │
  │  └─ JOOBLE API (Concurrent)                         │
  │     URL: https://jooble.org/api/                    │
  │     Returns: Job listings with descriptions         │
  │                                                      │
  │  (All 3 APIs called simultaneously = Fast!)         │
  └────────┬─────────────────────────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────────────────────────┐
  │  DEDUPLICATION                                        │
  │  1. Remove duplicate jobs (same company name +        │
  │     same description text)                            │
  │  2. Keep one job, remove location duplicates          │
  └────────┬─────────────────────────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────────────────────────┐
  │  SKILL MATCHING RANKING                               │
  │  For each job:                                        │
  │  1. Count how many resume skills found in job desc    │
  │  2. Score = number of matching skills                 │
  │  3. Sort jobs by score (highest first)                │
  └────────┬─────────────────────────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────────────────────────┐
  │  RETURN TOP K JOBS                                    │
  │  1. Take top 5 (or whatever top_k requested)          │
  │  2. Include all job details                           │
  │  3. Send to frontend                                  │
  └────────┬─────────────────────────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────────────────────────┐
  │  FRONTEND DISPLAY                                     │
  │  JobCard.jsx shows:                                   │
  │  - Job title                                          │
  │  - Company name                                       │
  │  - Location                                           │
  │  - Preview of description (first 200 chars)           │
  │  - Source (Remotive/Adzuna/Jooble)                    │
  │  - "View Job" button (opens in new tab)               │
  └──────────────────────────────────────────────────────┘
```

---

## 📦 Machine Learning Models Storage

### Where Models are Stored

```
intellidiots/
├── ml_models/                         # ML models directory
│   ├── trainer.py                    # Training code
│   ├── __init__.py
│   ├── rf_model.pkl                  # Random Forest (250KB)
│   ├── gb_model.pkl                  # Gradient Boosting (300KB)
│   ├── nn_model.pth                  # Neural Network (2MB)
│   └── vectorizer.pkl                # TF-IDF Vectorizer (100KB)
│
└── data/
    └── training_data.csv            # Training dataset (if available)
```

### Model Loading Flow

```
┌────────────────────────────────────────────────────────┐
│  BACKEND STARTUP                                       │
│  backend/main.py                                       │
└─────────────┬──────────────────────────────────────────┘
              │
              ▼
    ┌─────────────────────────────┐
    │ Load Models (Once at startup)│
    │ backend/utils/model_manager  │
    │                              │
    │ 1. Load TF-IDF Vectorizer    │
    │    From: ml_models/vect.pkl  │
    │                              │
    │ 2. Load Random Forest        │
    │    From: ml_models/rf_m.pkl  │
    │                              │
    │ 3. Load Gradient Boosting    │
    │    From: ml_models/gb_m.pkl  │
    │                              │
    │ 4. Load Neural Network       │
    │    From: ml_models/nn_m.pth  │
    │                              │
    │ All stored in memory for     │
    │ fast access during requests  │
    └──────────┬──────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ Models Ready for Predictions │
    │ Reused across all requests   │
    │ No reload on each call       │
    └──────────┬──────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │ User Request Comes In        │
    │ POST /api/v1/resume/score    │
    │                              │
    │ 1. Use loaded vectorizer     │
    │ 2. Use loaded models         │
    │ 3. Calculate score           │
    │ 4. Return result             │
    │ (FAST - all in memory!)      │
    └──────────────────────────────┘
```

### How Models are Created

```
┌────────────────────────────────────────────────────────┐
│  USER RUNS: python scripts/train_model.py              │
└─────────────┬──────────────────────────────────────────┘
              │
              ▼
    ┌──────────────────────────────────────────┐
    │ Step 1: Download Data from Kaggle        │
    │ scripts/kaggle_manager.py                │
    │                                          │
    │ Downloads:                               │
    │ - Resume dataset (50K+ resumes)          │
    │ - Job descriptions (100K+ jobs)          │
    │                                          │
    │ Saves to: data/                          │
    └──────────┬───────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────┐
    │ Step 2: Preprocess Data                  │
    │                                          │
    │ 1. Clean text (remove special chars)     │
    │ 2. Lowercase everything                  │
    │ 3. Remove extra whitespace               │
    │ 4. Tokenize (split into words)           │
    │ 5. Filter short entries                  │
    └──────────┬───────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────┐
    │ Step 3: Create Training Samples          │
    │                                          │
    │ Generate pairs:                          │
    │ (resume_text, job_desc, match_score)     │
    │                                          │
    │ Example:                                 │
    │ ("Python engineer...", "Seeking Pyth..  │
    │  "75%")                                  │
    │                                          │
    │ Create 10,000+ training samples          │
    └──────────┬───────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────┐
    │ Step 4: Train Models                     │
    │ ml_models/trainer.py                     │
    │                                          │
    │ Model 1: Random Forest                   │
    │ - 100 decision trees                     │
    │ - Fast predictions                       │
    │ - Good accuracy                          │
    │                                          │
    │ Model 2: Gradient Boosting               │
    │ - Sequential tree building               │
    │ - Better accuracy than RF                │
    │ - Slower training                        │
    │                                          │
    │ Model 3: Neural Network (PyTorch)        │
    │ - Input layer: 300 features              │
    │ - Hidden 1: 128 neurons                  │
    │ - Hidden 2: 64 neurons                   │
    │ - Hidden 3: 32 neurons                   │
    │ - Output: 1 (match score 0-1)            │
    │ - 100 epochs training                    │
    └──────────┬───────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────┐
    │ Step 5: Evaluate Models                  │
    │                                          │
    │ Metrics calculated:                      │
    │ - Accuracy: % correct predictions        │
    │ - Precision: True positives / all pos    │
    │ - Recall: True positives / actual pos    │
    │ - F1 Score: Balance of P & R             │
    │                                          │
    │ Results printed to console               │
    └──────────┬───────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────────────────┐
    │ Step 6: Save Models                      │
    │                                          │
    │ Save location: ml_models/                │
    │                                          │
    │ Files created:                           │
    │ - rf_model.pkl                           │
    │ - gb_model.pkl                           │
    │ - nn_model.pth                           │
    │ - vectorizer.pkl                         │
    │                                          │
    │ Now backend can load and use them!       │
    └──────────────────────────────────────────┘
```

---

## 🔌 Component Interaction Map

### Frontend Components

```
App.jsx (Main Router)
│
├── Navigation.jsx
│   └── Links to all pages
│
├── Home.jsx (Landing page)
│   └── CTA buttons
│       ├── Go to Analyzer
│       └── Go to Jobs
│
├── Analyzer.jsx (Resume Analysis Page)
│   │
│   ├── ResumeUpload.jsx
│   │   └── Upload file → backend /resume/upload
│   │
│   ├── ResumeAnalysis.jsx
│   │   └── Display extracted data
│   │       - Contact info
│   │       - Experience
│   │       - Skills found
│   │
│   ├── ATSScoreDisplay.jsx
│   │   └── Display score visually
│   │       - Circular progress
│   │       - Percentage
│   │       - Color coding
│   │
│   └── Keyword Matching
│       └── Show matching/missing keywords
│           - Green: found in resume
│           - Red: missing from resume
│
└── Jobs.jsx (Job Recommendations Page)
    │
    ├── SearchControls.jsx
    │   ├── Location input
    │   ├── Top K slider
    │   └── "Get Recommendations" button
    │
    ├── JobCard.jsx (Repeating for each job)
    │   ├── Job title
    │   ├── Company
    │   ├── Location
    │   ├── Description preview
    │   └── "View Job" button
    │
    └── JobDetailsModal
        ├── Full job description (sanitized HTML)
        ├── "Apply Now" button
        └── Close button
```

### Backend Routes

```
FastAPI backend/main.py
│
├── /health
│   └── Returns: {"status": "healthy"}
│
├── / (root)
│   └── Returns: API info message
│
├── /api/v1/resume/upload
│   ├── Input: FormData (file)
│   ├── Process: Parse PDF/DOCX/TXT
│   └── Output: Extracted text
│
├── /api/v1/resume/score
│   ├── Input: resume_text, job_description
│   ├── Process: Run ATS scorer
│   └── Output: Score, skills match, breakdown
│
├── /api/v1/resume/extract-skills
│   ├── Input: resume_text
│   ├── Process: Match against skill dictionary
│   └── Output: Skills list, categories
│
├── /api/v1/jobs/search
│   ├── Input: keyword, location
│   ├── Process: Query all 3 APIs
│   └── Output: Job listings array
│
└── /api/v1/jobs/recommend
    ├── Input: resume_text, top_k, location
    ├── Process: Search + dedup + rank
    └── Output: Top K job listings
```

### Data Flow with Storage

```
User Actions
    │
    ├─ Upload Resume
    │  └─ Saved to: uploads/
    │     └─ File processing
    │        └─ Text extraction (temporary)
    │
    ├─ Request Job Recommendations
    │  └─ Call 3 APIs (temporary in memory)
    │     └─ Deduplicate
    │        └─ Rank by skills
    │           └─ Return to frontend
    │
    └─ Get ATS Score
       └─ Use ML models
          └─ (Models loaded from ml_models/)
             └─ Return score
```

---

---

## 🏗️ Technology Stack & Integration

### How Each Technology Works Together

```
┌─────────────────────────────────────────────────────────────┐
│                       USER BROWSER                           │
│  (Chrome, Firefox, Safari, Edge)                             │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/HTTPS Request
                 │ (REST API calls)
                 ▼
    ┌────────────────────────────────────────────────────┐
    │         FRONTEND (ReactJS + TailwindCSS)            │
    │  Location: frontend/src/                            │
    │                                                     │
    │  Key Files:                                         │
    │  - App.jsx          → Main routing                  │
    │  - index.jsx        → React entry point             │
    │  - components/      → Reusable UI parts             │
    │  - pages/           → Full page components          │
    │  - store/           → State management (Zustand)    │
    │  - api/client.js    → API calls to backend          │
    │                                                     │
    │  Stack:                                             │
    │  - React 18         → UI framework                  │
    │  - TailwindCSS      → Styling                       │
    │  - Zustand          → State (Resume, Jobs)          │
    │  - React Router     → Navigation                    │
    │  - Axios            → HTTP requests                 │
    │  - DOMPurify        → HTML sanitization             │
    │  - Recharts         → Charts/graphs                 │
    │                                                     │
    │  Runs on: http://localhost:3000                     │
    └────────┬───────────────────────────────────────────┘
             │ API Calls to /api/v1/...
             │ (JSON format)
             │
             ▼
    ┌────────────────────────────────────────────────────┐
    │      BACKEND API (FastAPI + Python)                 │
    │  Location: backend/                                 │
    │                                                     │
    │  Key Files:                                         │
    │  - main.py                → FastAPI app setup       │
    │  - config.py              → Settings                │
    │  - routes/resume.py       → /resume endpoints       │
    │  - routes/jobs.py         → /jobs endpoints         │
    │  - routes/models.py       → /models endpoints       │
    │  - services/job_service.py→ Job API integration     │
    │  - utils/ats_scorer.py    → ATS scoring logic       │
    │  - utils/pdf_parser.py    → File parsing            │
    │  - utils/model_manager.py → ML model loading        │
    │                                                     │
    │  Stack:                                             │
    │  - FastAPI          → REST API framework            │
    │  - Uvicorn          → ASGI server                   │
    │  - Pydantic         → Data validation               │
    │  - aiohttp          → Async HTTP calls              │
    │  - requests         → HTTP requests                 │
    │                                                     │
    │  Runs on: http://localhost:8000                     │
    │  Docs at: http://localhost:8000/docs               │
    └────────┬───────────────────────────────────────────┘
             │
             ├─────────────────┬──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  JOB APIs    │  │  ML MODELS   │  │  FILE STORAGE│
    │              │  │              │  │              │
    │  • Remotive  │  │  • RF model  │  │  • uploads/  │
    │  • Adzuna    │  │  • GB model  │  │    (user     │
    │  • Jooble    │  │  • NN model  │  │     files)   │
    │              │  │              │  │              │
    │ External API │  │ ml_models/   │  │ File system  │
    │ 3rd party    │  │ Local files  │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
             │
             └─────────────────┬──────────────────┘
                               │
    ┌──────────────────────────▼─────────────────────────┐
    │        NLP & PROCESSING LIBRARIES                  │
    │                                                    │
    │  Core NLP:                                         │
    │  - spaCy        → Entity extraction                │
    │  - NLTK         → Tokenization, stemming           │
    │  - TF-IDF       → Vectorization                    │
    │  - scikit-learn → Vector operations                │
    │                                                    │
    │  File Processing:                                  │
    │  - PyPDF2       → PDF extraction                   │
    │  - pdfplumber   → PDF table extraction             │
    │  - python-docx  → DOCX parsing                     │
    │  - re (regex)   → Pattern matching                 │
    │                                                    │
    │  ML Models:                                        │
    │  - scikit-learn → RF, GB classifiers               │
    │  - PyTorch      → Neural network                   │
    │  - joblib       → Model serialization              │
    │                                                    │
    │  Utilities:                                        │
    │  - pandas       → Data handling                    │
    │  - numpy        → Numerical operations             │
    └──────────────────────────────────────────────────┘
```

### Technology Breakdown by Feature

#### Feature 1: Resume Upload & Parsing
```
User Action: Clicks "Upload Resume"
│
├─ Frontend
│  └─ ResumeUpload.jsx
│     └─ Uses: <input type="file">
│        └─ Calls: axios.post('/api/v1/resume/upload', formData)
│
└─ Backend
   └─ routes/resume.py → POST /upload
      └─ Receives: FormData with file
      └─ Uses: pdf_parser.py
         ├─ If .pdf: PyPDF2.PdfReader()
         ├─ If .docx: python_docx.Document()
         └─ If .txt: raw read
         └─ Returns: Extracted text
```

#### Feature 2: ATS Scoring
```
User Action: Pastes job description
│
├─ Frontend
│  └─ ResumeAnalysis.jsx
│     └─ Calls: axios.post('/api/v1/resume/score', {
│        resume_text: string,
│        job_description: string
│     })
│
└─ Backend
   └─ routes/resume.py → POST /score
      └─ Uses: ats_scorer.py
         │
         ├─ Extract skills (500+ skill dictionary)
         │  └─ Uses: spaCy for NLP
         │
         ├─ TF-IDF Vectorization
         │  └─ Uses: scikit-learn.TfidfVectorizer
         │
         ├─ Cosine Similarity
         │  └─ Uses: scipy.spatial.distance
         │
         ├─ Calculate 3 scores:
         │  ├─ Skill Match: (matched / total) × 40%
         │  ├─ Content Match: cosine_similarity × 30%
         │  └─ Keyword Match: (matched / total) × 30%
         │
         └─ Return: {score, skills, breakdown}
```

#### Feature 3: Job Recommendations
```
User Action: Clicks "Get Recommendations"
│
├─ Frontend
│  └─ JobRecommendations.jsx
│     └─ Calls: axios.post('/api/v1/jobs/recommend', {
│        resume_text: string,
│        top_k: number,
│        location: string
│     })
│
└─ Backend
   └─ routes/jobs.py → POST /recommend
      └─ Uses: job_service.py
         │
         ├─ Call 3 APIs Concurrently:
         │  ├─ Remotive: https://remotive.com/api/remote-jobs
         │  │  └─ axios.get(url)
         │  ├─ Adzuna: https://api.adzuna.com/v1/api/jobs
         │  │  └─ axios.get(url, {params: {app_id, app_key}})
         │  └─ Jooble: https://jooble.org/api/
         │     └─ axios.post(url, {keywords, location})
         │
         ├─ Merge Results
         │  └─ Array of all jobs from 3 sources
         │
         ├─ Deduplication
         │  └─ Compare: company + description fingerprint
         │     └─ Remove duplicates
         │
         ├─ Rank by Skills
         │  └─ For each job:
         │     ├─ Extract job skills
         │     ├─ Count matching resume skills
         │     └─ Sort by count
         │
         └─ Return: Top K results
```

### Data Flow: From File to Score

```
1. USER UPLOADS RESUME (PDF)
   └─ File stored: uploads/resume_123.pdf

2. BACKEND DETECTS FILE TYPE
   └─ Extension: .pdf
   
3. PDF PARSING
   └─ Use PyPDF2.PdfReader()
   └─ Extract all text from all pages
   └─ Result: "John Doe\nPython developer..."
   
4. SKILL EXTRACTION
   ├─ Split into words
   ├─ Lowercase everything
   ├─ Check against 500+ skill dictionary
   │  ├─ "[python, react, aws, docker]"
   │  └─ Stored in state
   ├─ Categorize:
   │  ├─ Languages: [python]
   │  ├─ Frameworks: [react]
   │  └─ Cloud: [aws]
   └─ Send to frontend
   
5. USER ENTERS JOB DESCRIPTION
   └─ "Looking for Python/React developer with AWS"
   
6. ATS SCORING
   ├─ Skill Matching (40%)
   │  ├─ Resume skills: [python, react, aws]
   │  ├─ Job skills: [python, react, aws, docker]
   │  ├─ Match: 3/4 = 75%
   │  └─ Score: 75% × 40% = 30 points
   │
   ├─ Content Similarity (30%)
   │  ├─ Vectorize resume with TF-IDF
   │  ├─ Vectorize job with TF-IDF
   │  ├─ Calculate cosine similarity: 0.85
   │  └─ Score: 85% × 30% = 25.5 points
   │
   └─ Keyword Matching (30%)
      ├─ Job keywords: [python, react, aws, docker]
      ├─ Found in resume: [python, react, aws] = 3
      ├─ Match: 3/4 = 75%
      └─ Score: 75% × 30% = 22.5 points
      
7. FINAL CALCULATION
   └─ Total = 30 + 25.5 + 22.5 = 78%
   └─ Display in frontend with breakdown
```

### How Models Get Predictions

```
TRAINING PHASE (One-time):
python scripts/train_model.py
│
├─ Download Kaggle datasets
│  └─ 50K resumes + 100K job descriptions
│
├─ Create training pairs:
│  ├─ (Resume A, Job X, 75%)
│  ├─ (Resume B, Job Y, 45%)
│  └─ (Resume C, Job Z, 92%)
│
├─ Train 3 models:
│  ├─ Random Forest (100 trees)
│  ├─ Gradient Boosting (300 trees)
│  └─ Neural Network (3 hidden layers)
│
└─ Save to disk:
   ├─ ml_models/rf_model.pkl (250KB)
   ├─ ml_models/gb_model.pkl (300KB)
   ├─ ml_models/nn_model.pth (2MB)
   └─ ml_models/vectorizer.pkl (100KB)


PREDICTION PHASE (Each API call):
│
├─ Backend loads models on startup
│  └─ Stored in memory (RAM)
│
├─ When scoring request comes:
│  ├─ Vectorize resume text
│  ├─ Vectorize job description
│  ├─ Format as [feature1, feature2, ...]
│  ├─ Pass to loaded model
│  ├─ Model predicts: score (0-1)
│  └─ Convert to percentage (0-100%)
│
└─ Return to frontend immediately
   (All in memory, very fast!)
```

---

### Build and Run
```bash
docker-compose up --build
docker-compose up -d --build          # Run in background
docker-compose down                   # Stop containers
docker-compose logs -f               # View logs
```

---

## 🌐 Cloud Deployment (Render.com)

### Setup

1. **MongoDB Atlas** (Free M0 cluster)
   - https://mongodb.com/atlas
   - Get connection string

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Deploy on Render**
   - Connect GitHub repo
   - Select render.yaml
   - Add environment variables
   - Deploy

**Cost**: ~$7/month backend + free MongoDB Atlas

---

---

## 📂 Complete File Structure & Purpose

### Root Level Files
```
intellidiots/                          # Project root (Main folder)

├── README.md                          # You are here! Complete documentation
├── .env                              # Configuration (API keys, secrets)
├── .gitignore                        # Files to not commit to git
├── docker-compose.yml                # Docker service definitions
├── Dockerfile.backend                # Backend container config
├── Dockerfile.frontend               # Frontend container config
├── render.yaml                       # Render.com deployment config
│
├── examples.py                       # Example usage of the system
├── test_api.py                      # Manual API testing script
│
└── [Directories explained below]
```

### Backend Directory Structure

```
backend/                              # FastAPI application (REST API)
│
├── main.py                          # ⭐ APPLICATION ENTRY POINT
│   ├─ Initializes FastAPI app
│   ├─ Sets up routes
│   ├─ Configures CORS
│   ├─ Loads ML models on startup
│   └─ Defines /health endpoint
│
├── config.py                        # Configuration settings
│   ├─ API keys and credentials
│   ├─ Database connection strings
│   ├─ Environment variables
│   └─ Feature flags
│
├── requirements.txt                 # Python dependencies list
│   ├─ FastAPI==0.104.1
│   ├─ scikit-learn==1.3.2
│   ├─ torch==2.0.1
│   ├─ spacy==3.7.2
│   ├─ pandas==2.0.3
│   └─ 30+ more packages
│
├── routes/                          # API endpoint definitions
│   │
│   ├── __init__.py                 # Package initialization
│   │
│   ├── resume.py                   # Resume-related endpoints
│   │   ├─ POST /api/v1/resume/upload        (Upload file)
│   │   ├─ POST /api/v1/resume/score        (Get ATS score)
│   │   ├─ POST /api/v1/resume/extract-skills (Extract skills)
│   │   └─ POST /api/v1/resume/analyze-advanced (Advanced analysis)
│   │
│   ├── jobs.py                     # Job-related endpoints
│   │   ├─ GET /api/v1/jobs/search          (Search jobs)
│   │   ├─ POST /api/v1/jobs/recommend      (Get recommendations)
│   │   ├─ GET /api/v1/jobs/trending        (Get trending)
│   │   └─ GET /api/v1/jobs/skills-demand   (Skills in demand)
│   │
│   └── models.py                   # ML model endpoints
│       ├─ GET /api/v1/models/list          (List available models)
│       ├─ POST /api/v1/models/predict      (Direct prediction)
│       └─ GET /api/v1/models/info          (Model info)
│
├── services/                        # Business logic layer
│   │
│   ├── __init__.py                 # Package initialization
│   │
│   └── job_service.py              # Job API integration
│       ├─ search_jobs()            (Search across 3 APIs)
│       ├─ _search_remotive()       (Remotive API)
│       ├─ _search_adzuna()         (Adzuna API)
│       ├─ _search_jooble()         (Jooble API)
│       ├─ _deduplicate_jobs()      (Remove duplicates)
│       ├─ get_trending_jobs()      (Trending jobs)
│       └─ get_skills_demand()      (Demand analysis)
│
└── utils/                          # Utility functions
    │
    ├── __init__.py                 # Package initialization
    │
    ├── pdf_parser.py               # File parsing utilities
    │   ├─ parse_pdf()              (Extract from PDF)
    │   ├─ parse_docx()             (Extract from DOCX)
    │   ├─ parse_txt()              (Extract from TXT)
    │   └─ clean_text()             (Text cleaning)
    │
    ├── ats_scorer.py               # ATS scoring algorithm
    │   ├─ ATSScorer class
    │   ├─ score()                  (Calculate score)
    │   ├─ extract_skills()         (Find skills)
    │   ├─ calculate_similarity()    (TF-IDF match)
    │   └─ SKILL_DICTIONARY         (500+ skills)
    │
    ├── advanced_ats_scorer.py      # Advanced scoring
    │   ├─ AdvancedATSScorer class
    │   ├─ Machine learning scoring
    │   └─ Deep learning analysis
    │
    └── model_manager.py            # ML model loading
        ├─ ModelManager class
        ├─ load_models()            (Load at startup)
        ├─ get_model()              (Access model)
        ├─ predict()                (Make prediction)
        └─ Models cached in memory
```

### Frontend Directory Structure

```
frontend/                            # React application (UI)
│
├── package.json                    # NPM dependencies & scripts
│   ├─ react: 18.2.0
│   ├─ tailwindcss: 3.3.0
│   ├─ axios: 1.6.2
│   ├─ zustand: 4.4.1
│   └─ 15+ more packages
│
├── package-lock.json               # Exact dependency versions locked
│
├── postcss.config.js               # CSS processing config
├── tailwind.config.js              # Tailwind CSS config
│
├── public/                         # Static files served as-is
│   ├── index.html                 # Base HTML file
│   └── assets/                    # Images, fonts
│
├── src/                           # React source code (main app)
│   │
│   ├── index.jsx                  # ⭐ ENTRY POINT
│   │   └─ Initializes React app
│   │   └─ Loads into index.html
│   │
│   ├── App.jsx                    # Main app component (router)
│   │   ├─ Defines all routes
│   │   ├─ Layout wrapper
│   │   └─ Global state setup
│   │
│   ├── index.css                  # Global styles
│   │
│   ├── api/
│   │   └── client.js              # API communication layer
│   │       ├─ baseURL: localhost:8000/api/v1
│   │       ├─ uploadResume()
│   │       ├─ scoreResume()
│   │       ├─ extractSkills()
│   │       ├─ searchJobs()
│   │       ├─ getRecommendations()
│   │       └─ All API calls here
│   │
│   ├── store/
│   │   └── index.js               # State management (Zustand)
│   │       ├─ resumeStore         (Resume data)
│   │       │  ├─ resumeText
│   │       │  ├─ extractedData
│   │       │  └─ skills
│   │       ├─ jobsStore           (Jobs data)
│   │       │  ├─ jobs
│   │       │  ├─ selectedJob
│   │       │  └─ filters
│   │       └─ uiStore             (UI state)
│   │          ├─ currentPage
│   │          ├─ loading
│   │          └─ error messages
│   │
│   ├── components/                # Reusable UI components
│   │   │
│   │   ├── Common.jsx             # Shared components
│   │   │   ├─ SafeHTML            (Sanitized HTML rendering)
│   │   │   ├─ LoadingSpinner
│   │   │   ├─ ErrorMessage
│   │   │   └─ Button variants
│   │   │
│   │   ├── Navigation.jsx         # Header/navbar
│   │   │   ├─ Logo
│   │   │   ├─ Menu links
│   │   │   └─ Mobile menu
│   │   │
│   │   ├── Footer.jsx             # Footer
│   │   │   ├─ Links
│   │   │   ├─ Copyright
│   │   │   └─ Contact info
│   │   │
│   │   ├── ResumeUpload.jsx       # File upload component
│   │   │   ├─ File input
│   │   │   ├─ Validation
│   │   │   ├─ Upload progress
│   │   │   └─ Error handling
│   │   │
│   │   ├── ResumeAnalysis.jsx     # Show extracted resume data
│   │   │   ├─ Contact info display
│   │   │   ├─ Experience section
│   │   │   ├─ Skills chips
│   │   │   └─ Education list
│   │   │
│   │   ├── AdvancedResumeAnalysis.jsx  # ML-based analysis
│   │   │   ├─ Model predictions
│   │   │   ├─ Recommendations
│   │   │   └─ Career suggestions
│   │   │
│   │   ├── JobRecommendations.jsx # Job listing page
│   │   │   ├─ Search form
│   │   │   ├─ Job cards grid
│   │   │   ├─ Filters
│   │   │   └─ Pagination
│   │   │
│   │   ├── SkillsDemand.jsx       # Market insights
│   │   │   ├─ Trending skills
│   │   │   ├─ Charts
│   │   │   └─ Statistics
│   │   │
│   │   └── home/                 # Home page components
│   │       ├─ Hero.jsx           (Banner section)
│   │       ├─ Features.jsx       (Feature tiles)
│   │       ├─ HowItWorks.jsx     (Process steps)
│   │       ├─ HowItHelps.jsx     (Benefits)
│   │       ├─ Testimonials.jsx   (User reviews)
│   │       └─ CTA.jsx            (Call to action)
│   │
│   └── pages/                    # Full page components
│       ├─ Home.jsx              (Home page layout)
│       │  └─ Combines home/* components
│       ├─ Analyzer.jsx          (Resume analysis page)
│       │  └─ Upload + Analysis + Scoring
│       └─ Jobs.jsx              (Job search page)
│          └─ Search + Results + Filtering
│
└── build/                        # Compiled production build
    ├─ index.html
    ├─ assets/  (CSS, JS bundles)
    └─ (Generated by: npm run build)
```

### ML Models Directory

```
ml_models/                         # Machine learning models storage
│
├── __init__.py
│
├── trainer.py                    # Training script (run once)
│   ├─ Download datasets from Kaggle
│   ├─ Preprocess data
│   ├─ Train Random Forest
│   ├─ Train Gradient Boosting
│   ├─ Train Neural Network
│   ├─ Evaluate all models
│   └─ Save to .pkl and .pth files
│
├── rf_model.pkl                  # Random Forest (250KB)
│   └─ 100 decision trees
│   └─ Loaded by model_manager.py
│   └─ Used for fast predictions
│
├── gb_model.pkl                  # Gradient Boosting (300KB)
│   └─ 300 sequential trees
│   └─ Higher accuracy than RF
│   └─ Slightly slower than RF
│
├── nn_model.pth                  # Neural Network (2MB)
│   └─ PyTorch format
│   └─ 3 hidden layers (128, 64, 32 neurons)
│   └─ Best accuracy but slowest
│
└── vectorizer.pkl                # TF-IDF Vectorizer (100KB)
    └─ Pre-fitted on training data
    └─ Used to vectorize text before model input
```

### Data & Scripts Directories

```
data/                             # Datasets
├── training_data.csv            # Training set (if available)
└── [Downloaded from Kaggle during training]

scripts/                          # Utility scripts
├── __init__.py
├── train_model.py               # Run this to train models
│   ├─ kaggle_manager.py calls
│   ├─ Preprocesses data
│   ├─ Trains 3 models
│   ├─ Saves to ml_models/
│   └─ Take 2-4 hours
│
└── kaggle_manager.py            # Download Kaggle datasets
    ├─ Requires kaggle.json setup
    ├─ Downloads resumes
    ├─ Downloads job descriptions
    └─ Saves to data/ directory

uploads/                          # User uploaded files (temporary)
├── resume_user1.pdf
├── resume_user2.docx
└── [Files deleted after processing]
```

---

## 🔀 How Data Flows Through the System

### Complete Request Lifecycle: Resume Upload to Score

```
[Time: 0ms] USER CLICKS "UPLOAD RESUME"
│
├─ Browser Event
│  └─ ResumeUpload.jsx triggered
│
├─ Frontend Validation
│  ├─ Check file type (.pdf, .docx, .txt)
│  ├─ Check file size (<50MB)
│  └─ Show error if invalid
│
└─ File Preparation
   └─ Create FormData object
   └─ Attach file from input


[Time: 5ms] SEND REQUEST TO BACKEND
│
├─ api/client.js
│  └─ axios.post('/resume/upload', formData)
│  └─ Headers: 'Content-Type': 'multipart/form-data'
│
└─ HTTP Request Sent
   └─ Network latency: 10-50ms


[Time: 50ms] BACKEND RECEIVES FILE
│
├─ routes/resume.py
│  └─ @app.post('/resume/upload')
│  └─ Receives FormData
│
├─ File Validation
│  ├─ Check MIME type
│  ├─ Check size limit
│  └─ Virus scan (optional)
│
└─ Save File
   └─ Save to: uploads/resume_{timestamp}.{ext}


[Time: 60ms] PARSE FILE CONTENT
│
├─ utils/pdf_parser.py
│  └─ Detect file type
│
├─ If PDF:
│  ├─ PyPDF2.PdfReader()
│  ├─ Iterate through pages
│  ├─ Extract text from each page
│  └─ Result: "John Doe\nPython developer..."
│
├─ If DOCX:
│  ├─ python_docx.Document()
│  ├─ Read paragraphs
│  └─ Result: Full text content
│
└─ If TXT:
   └─ Read file directly
   └─ Result: Raw content


[Time: 100ms] CLEAN & PROCESS TEXT
│
├─ Remove extra whitespace
├─ Convert to lowercase
├─ Remove special characters
├─ Split into tokens
└─ Result: Cleaned text


[Time: 110ms] EXTRACT SKILLS
│
├─ Iterate through tokens
├─ Check against 500+ skill dictionary
│  ├─ Languages: python, javascript, java, c++...
│  ├─ Frameworks: react, django, spring, vue...
│  ├─ Databases: mysql, mongodb, postgres...
│  └─ Clouds: aws, azure, gcp...
│
└─ Result: [python, react, aws, docker]
   └─ Categorized by type


[Time: 150ms] RETURN RESPONSE TO FRONTEND
│
├─ JSON Response:
│  {
│    "success": true,
│    "data": {
│      "resume_text": "John Doe...",
│      "extracted_skills": ["python", "react", "aws"],
│      "file_id": "resume_12345"
│    }
│  }
│
└─ HTTP 200 OK


[Time: 160ms] FRONTEND RECEIVES & DISPLAYS
│
├─ JavaScript Promise resolves
├─ Update Zustand store
│  └─ resumeStore.setResumeText(...)
│  └─ resumeStore.setSkills(...)
│
├─ React component re-renders
├─ Display extracted data
│  ├─ Show text preview
│  ├─ Show skills as chips
│  └─ Show next action button
│
└─ Show success message


===== NOW USER PASTES JOB DESCRIPTION =====

[Time: 5000ms] USER ENTERS JOB DESCRIPTION
│
└─ Shown in textarea on page


[Time: 5500ms] USER CLICKS "GET ATS SCORE"
│
├─ Frontend validation
├─ Prepare request
│  {
│    "resume_text": "John Doe...",
│    "job_description": "Seeking Python..."
│  }
│
└─ axios.post('/resume/score', payload)


[Time: 5550ms] BACKEND SCORES RESUME
│
├─ routes/resume.py
│  └─ @app.post('/resume/score')
│
├─ Extract skills from both texts
├─ Calculate 3 scores:
│
│  [1] Skill Match (40%)
│  ├─ Resume skills: [python, react, aws] (from earlier)
│  ├─ Job skills: [python, react, docker, kubernetes]
│  ├─ Intersection: [python, react] = 2
│  ├─ Total job skills: 4
│  ├─ Match: 2/4 = 50%
│  └─ Score: 50% × 40% = 20 points
│
│  [2] Content Similarity (30%)
│  ├─ Vectorize resume_text with TF-IDF
│  │  └─ 300-dimensional vector
│  ├─ Vectorize job_description with TF-IDF
│  │  └─ 300-dimensional vector
│  ├─ Calculate cosine similarity
│  │  └─ cos(angle) between vectors
│  ├─ Result: 0.75 (75% similar)
│  └─ Score: 75% × 30% = 22.5 points
│
│  [3] Keyword Match (30%)
│  ├─ Job words: ["python", "react", "docker", "k8s"]
│  ├─ Check resume contains each
│  ├─ Matched: ["python", "react"] = 2
│  ├─ Match: 2/4 = 50%
│  └─ Score: 50% × 30% = 15 points
│
└─ Total = 20 + 22.5 + 15 = 57.5%


[Time: 5600ms] RETURN SCORE TO FRONTEND
│
├─ JSON Response:
│  {
│    "score": 57.5,
│    "skill_match": 50,
│    "content_match": 75,
│    "keyword_match": 50,
│    "matching_skills": ["python", "react"],
│    "missing_skills": ["docker", "kubernetes"]
│  }
│
└─ HTTP 200 OK


[Time: 5620ms] FRONTEND DISPLAYS SCORE
│
├─ Update Zustand store
├─ Re-render ResumeAnalysis component
├─ Display score visually:
│  ├─ Circular progress: 57.5%
│  ├─ Color: Yellow (warning - not great match)
│  ├─ Text: "57.5% Match"
│  │
│  ├─ Breakdown:
│  │  ├─ Skill Match: 50%
│  │  ├─ Content: 75%
│  │  └─ Keywords: 50%
│  │
│  ├─ Matching Skills (green):
│  │  ├─ ✓ Python
│  │  └─ ✓ React
│  │
│  └─ Missing Skills (red):
│     ├─ ✗ Docker
│     └─ ✗ Kubernetes


[Time: 5650ms] READY FOR NEXT ACTION
│
├─ User can:
│  ├─ Upload new resume
│  ├─ Try different job description
│  ├─ Get recommendations for this resume
│  └─ Go to jobs page
│
└─ All data stored in browser memory (Zustand)
   └─ Ready for next action instantly
```

---

## 🎬 Component Interaction Sequence

### Scenario: Upload Resume → Get Score → Get Job Recommendations

```
STEP 1: User visits Analyzer page
────────────────────────────────
Frontend                          Backend
│                                 │
├─ Analyzer.jsx                   │
│  ├─ Render navigation           │
│  ├─ Render ResumeUpload         │
│  ├─ Render analysis placeholder │
│  └─ Ready for input             │
│                                 │
└─ All components mounted         │


STEP 2: User uploads resume
────────────────────────────────
Frontend                          Backend
│                                 │
├─ ResumeUpload.jsx               │
│  ├─ <input type="file"> clicked │
│  ├─ File selected: resume.pdf   │
│  └─ On change event fired       │
│                                 │
├─ handleFileUpload()             │
│  ├─ Validate file               │
│  ├─ Create FormData             │
│  ├─ api/client.js               │
│  │  └─ axios.post('/resume/...' ) ──────> routes/resume.py
│  │     │                              POST /upload
│  │     │                              │
│  │     │                              ├─ Receive FormData
│  │     │<──────────────────────────── ├─ Save to uploads/
│  │     │ {"resume_text": "...",      ├─ Parse PDF
│  │     │  "skills": [...]}           ├─ Extract skills
│  │     │                              └─ Return JSON
│  │
│  ├─ Store received data          │
│  │  └─ Zustand resumeStore       │
│  │     .setResumeText()          │
│  │     .setSkills()              │
│  │                               │
│  └─ Trigger re-render            │
│     └─ ResumeAnalysis visible    │


STEP 3: ResumeAnalysis displays results
────────────────────────────────────────
Frontend                          Backend
│                                 │
├─ ResumeAnalysis.jsx             │
│  ├─ {useStore} get resume data  │
│  │  └─ resume_text              │
│  │  └─ skills                   │
│  │                              │
│  └─ Render:                     │
│     ├─ "Extracted Skills:"      │
│     ├─ Skill chips              │
│     ├─ Preview of resume        │
│     ├─ Textarea for job desc    │
│     └─ "Get ATS Score" button   │


STEP 4: User pastes job description & clicks button
────────────────────────────────────
Frontend                          Backend
│                                 │
├─ handleGetScore()               │
│  ├─ Get resume from store       │
│  ├─ Get job description text    │
│  ├─ Validate both exist         │
│  ├─ api/client.js               │
│  │  └─ axios.post('/resume/score')──> routes/resume.py
│  │     {resume_text, job_desc}  POST /score
│  │                              │
│  │                              ├─ ats_scorer.py
│  │                              │  ├─ Extract skills
│  │                              │  ├─ Calculate TF-IDF
│  │                              │  ├─ Calculate similarity
│  │                              │  ├─ Combine scores
│  │                              │  └─ Return {score, breakdown}
│  │                              │
│  │<──────────────────────────- ├─ {"score": 57.5,
│  │ {score, matching, missing}  │    "breakdown": {...}}
│  │
│  └─ Update Zustand store        │
│     .setScore()                 │
│     .setBreakdown()             │


STEP 5: Score visualization
───────────────────────────
Frontend                          Backend
│                                 │
├─ ScoreDisplay component         │
│  ├─ {useStore} get score        │
│  ├─ Render circular progress    │
│  ├─ 57.5% in center             │
│  ├─ Color code: yellow          │
│  ├─ Show breakdown              │
│  ├─ Show matching skills        │
│  └─ Show missing skills         │


STEP 6: User clicks "Get Recommendations"
──────────────────────────────────────────
Frontend                          Backend
│                                 │
├─ handleGetRecommendations()     │
│  ├─ Get resume from store       │
│  ├─ Prepare request             │
│  ├─ api/client.js               │
│  │  └─ axios.post('/jobs/...')──> routes/jobs.py
│  │     {resume_text, top_k, ...} POST /recommend
│  │                              │
│  │                              ├─ job_service.py
│  │                              │
│  │                              ├─ Call Remotive API
│  │                              │  (concurrent)
│  │                              │  └─ axios.get('remotive.com...')
│  │
│  │                              ├─ Call Adzuna API
│  │                              │  (concurrent)
│  │                              │  └─ axios.get('adzuna.com...')
│  │
│  │                              └─ Call Jooble API
│  │                                 (concurrent)
│  │                                 └─ axios.post('jooble.org')
│  │
│  │                              ├─ Merge all results
│  │                              ├─ Deduplicate
│  │                              ├─ Rank by skills
│  │                              ├─ Sort by relevance
│  │                              │
│  │<────────────────────────────├─ Return top 5 jobs
│  │ [{job1}, {job2}, ...]       │


STEP 7: Display job recommendations
────────────────────────────────────
Frontend                          Backend
│                                 │
├─ JobRecommendations.jsx         │
│  ├─ Receive jobs from API       │
│  ├─ Update Zustand              │
│  │  └─ jobsStore.setJobs()      │
│  │                              │
│  └─ Render JobCard for each     │
│     ├─ Title                    │
│     ├─ Company                  │
│     ├─ Location                 │
│     ├─ Description preview      │
│     ├─ Source badge             │
│     └─ "View Job" button        │


STEP 8: User clicks job & views details
────────────────────────────────────────
Frontend                          Backend
│                                 │
├─ handleViewJob(jobId)           │
│  ├─ Set selectedJob in store    │
│  ├─ Open modal/new page         │
│  │                              │
│  └─ Render JobDetails           │
│     ├─ Full description         │
│     │  └─ Sanitized with        │
│     │     DOMPurify             │
│     ├─ All job info             │
│     ├─ "Apply Now" button       │
│     │  └─ Opens job site        │
│     └─ "Back" button            │
```

---

## 🔍 Real Example: Python Developer Resume

### Input
```
Resume Text:
"John Doe
Python Developer with 5 years experience.
Skilled in Python, Django, React, PostgreSQL, AWS
Experience with Docker, Kubernetes
Worked at Tech Company and Startup"

Job Description:
"Seeking Senior Python Developer experienced with:
Python, FastAPI, React, AWS, Docker, Kubernetes,
Git, PostgreSQL, Linux"
```

### Processing Steps

```
[BACKEND SKILL EXTRACTION]

Resume Skills Found:
├─ Languages: Python ✓
├─ Frameworks: Django ✓, React ✓
├─ Databases: PostgreSQL ✓
├─ Cloud: AWS ✓
└─ Tools: Docker ✓, Kubernetes ✓

Job Skills Found:
├─ Languages: Python ✓
├─ Frameworks: FastAPI ✓, React ✓
├─ Databases: PostgreSQL ✓
├─ Cloud: AWS ✓
└─ Tools: Docker ✓, Kubernetes ✓, Git ✓, Linux ✓


[SKILL MATCHING - 40%]

Resume Skills: {Python, Django, React, PostgreSQL, AWS, Docker, Kubernetes}
Job Skills: {Python, FastAPI, React, AWS, Docker, Kubernetes, Git, PostgreSQL, Linux}

Intersection (matching): {Python, React, AWS, Docker, Kubernetes, PostgreSQL}
Count: 6 out of 9 job skills = 66.7%

Score: 66.7% × 40% = 26.7 points


[CONTENT SIMILARITY - 30%]

Resume vectorized:       [0.1, 0.2, 0.3, ...]  (300 dimensions)
Job description vector: [0.2, 0.25, 0.35, ...]

Cosine similarity: 0.82 (82% similar)

Score: 82% × 30% = 24.6 points


[KEYWORD MATCHING - 30%]

Job keywords: [python, fastapi, react, aws, docker, kubernetes, git, postgresql, linux]
Found in resume: [python, react, aws, docker, kubernetes, postgresql]

Count: 6 out of 9 = 66.7%

Score: 66.7% × 30% = 20 points


[FINAL CALCULATION]

Total Score = 26.7 + 24.6 + 20 = 71.3%

Color Code: Green (71% is good match)

Breakdown:
├─ Skill Match: 66.7%
├─ Content: 82%
└─ Keywords: 66.7%

Matching Skills (✓ Found in resume):
├─ Python
├─ React
├─ AWS
├─ Docker
├─ Kubernetes
└─ PostgreSQL

Missing Skills (✗ Not in resume):
├─ FastAPI (but knows Django)
├─ Git (assumed)
└─ Linux (assumed)
```

### Frontend Display
```
Score Card:
┌─────────────────────────┐
│      ATS Score          │
│                         │
│        (71.3%)          │
│         ⭕               │ ← Circular progress bar
│                         │
│  Score: 71.3% (Good)    │
│                         │
│  Breakdown:             │
│  ├─ Skill Match: 66.7%  │
│  ├─ Content: 82%        │
│  └─ Keywords: 66.7%     │
└─────────────────────────┘

Matching Skills:
[Python] [React] [AWS] [Docker] [Kubernetes] [PostgreSQL]
  (✓)     (✓)   (✓)     (✓)        (✓)          (✓)

Missing Skills:
[FastAPI] [Git] [Linux]
   (✗)    (✗)    (✗)
```

---

### Test API Endpoints

```bash
# Resume Upload
curl -X POST "http://localhost:8000/api/v1/resume/upload" -F "file=@resume.pdf"

# ATS Score
curl -X POST "http://localhost:8000/api/v1/resume/score" \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Python developer", "job_description": "Python engineer"}'

# Job Search
curl "http://localhost:8000/api/v1/jobs/search?keyword=Python&location=remote"

# Job Recommendations
curl -X POST "http://localhost:8000/api/v1/jobs/recommend" \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Python React AWS", "top_k": 5}'
```

---

## 🔍 Core Code Explanations

### How ATS Scoring Works

```python
class ATSScorer:
    def score(self, resume_text, job_description):
        # 1. Extract skills
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        
        # 2. Calculate skill match (40%)
        skill_match = len(resume_skills & job_skills) / len(job_skills)
        
        # 3. Calculate content similarity (30%)
        content_match = self.cosine_similarity(resume_text, job_description)
        
        # 4. Calculate keyword match (30%)
        keyword_match = self.keyword_overlap(resume_text, job_description)
        
        # 5. Weighted combination
        score = (0.4 * skill_match) + (0.3 * content_match) + (0.3 * keyword_match)
        return score * 100
```

### How Job Recommendations Work

```python
async def get_recommendations(self, skills, top_k=5):
    # 1. Search for jobs
    jobs = await self.search_jobs(skills[0])
    
    # 2. Score each job
    def skill_match_score(job):
        desc = job['description'].lower()
        return sum(1 for skill in skills if skill.lower() in desc)
    
    # 3. Sort by relevance
    jobs.sort(key=skill_match_score, reverse=True)
    
    # 4. Return top K
    return jobs[:top_k]
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use**:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Module 'spacy' not found**:
```bash
python -m spacy download en_core_web_sm
```

**CORS error**:
- Backend running on http://localhost:8000?
- Check REACT_APP_API_URL in .env
- CORS middleware enabled?

### Frontend Issues

**npm not found**:
- Install Node.js from https://nodejs.org/
- Restart terminal

**Port 3000 already in use**:
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**React won't load**:
1. Clear browser cache
2. Check console for errors
3. Restart npm start
4. Verify backend is running

### API Issues

**500 error**:
- Check backend console
- Verify environment variables
- Check API credentials

**No jobs returning**:
- Verify job API credentials
- Check network connectivity
- Try without location parameter

**File upload fails**:
- Check file size (<50MB)
- Verify format (PDF/DOCX/TXT)
- Check uploads/ directory permissions

---

## 📊 Performance Tips

### Backend
```python
# Concurrent API calls
async def search_jobs(self, keyword):
    tasks = [
        self._search_remotive(keyword),
        self._search_adzuna(keyword),
        self._search_jooble(keyword)
    ]
    return await asyncio.gather(*tasks)
```

### Frontend
```javascript
// React.memo for expensive components
export const JobCard = React.memo(({ job }) => {...});

// useCallback for handlers
const handleSearch = useCallback(() => {...}, [dependencies]);

// Lazy load components
const Jobs = lazy(() => import('./Jobs'));
```

---

## 🚀 Advanced Features

### Custom Model Training

```bash
# Setup Kaggle API
https://www.kaggle.com/settings/account
# Place kaggle.json in ~/.kaggle/

# Run training
python scripts/train_model.py
```

**What it does**:
1. Downloads datasets from Kaggle
2. Preprocesses data
3. Trains 3 models (RF, GB, NN)
4. Evaluates performance
5. Saves to ml_models/

### Custom Integrations

**MongoDB**: Store analyses, bookmarks
- Set MONGODB_URI in .env

**OpenAI API**: Advanced features
- Set OPENAI_API_KEY in .env
- Generate descriptions, cover letters, insights

---

## 📝 Development Guide

### Adding New Job API

```python
async def _search_new_api(self, keyword, location):
    # Implement API call
    return [{
        'id': id,
        'title': title,
        'company': company,
        'location': location,
        'description': desc,
        'url': url,
        'source': 'api_name'
    }]
```

### Adding Frontend Component

```jsx
export const MyComponent = () => {
  return <div>Component content</div>;
};
```

Then in App.jsx:
```jsx
import { MyComponent } from './components/MyComponent';
<Route path="/my-route" element={<MyComponent />} />
```

---

## ✅ Project Checklist

### Setup
- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] Docker installed (optional)
- [ ] .env file created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed

### Running
- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:3000
- [ ] Can upload resume
- [ ] Can get ATS score
- [ ] Can search jobs
- [ ] API docs at /docs work

### Customization (Optional)
- [ ] Added job API keys
- [ ] Trained custom ML models
- [ ] Modified skill dictionary
- [ ] Changed scoring weights
- [ ] Deployed to cloud

---

## 🎉 Next Steps

1. **Test** - Upload resume, try ATS scoring
2. **Add API keys** - Get from Adzuna, Jooble
3. **Train models** - Run `python scripts/train_model.py`
4. **Deploy** - Use Docker or Render
5. **Customize** - Modify scoring, add features

---

## 📚 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **PyTorch**: https://pytorch.org/
- **scikit-learn**: https://scikit-learn.org/

---

## 📞 Support

### Check These First
1. Backend running? (`http://localhost:8000/health`)
2. Frontend running? (`http://localhost:3000`)
3. API keys in .env?
4. MongoDB running? (if using)

### Common Issues

| Issue | Solution |
|-------|----------|
| Module not found | Run `pip install -r requirements.txt` or `npm install` |
| Port in use | Kill process or change port |
| CORS error | Check REACT_APP_API_URL in .env |
| Invalid API key | Get new key from provider |
| Upload fails | Check file format/size |
| No jobs | Check API credentials, network |
| Low score | Resume must match job skills |

---

**Built with ❤️ - Resume ATS Scorer & Job Recommendation System**

Version 1.0.0 | Created February 2024 | Last Updated February 2026
