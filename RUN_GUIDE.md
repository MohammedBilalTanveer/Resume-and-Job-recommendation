# 🚀 How to Run the Resume ATS Scorer & Job Recommendation Website

Your complete application is ready! Follow these steps to get it running.

## Prerequisites

Make sure you have installed:
- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Docker** (optional, for containerized setup) - [Download](https://www.docker.com/)

---

## Option 1: Run Locally (Recommended for Development)

### Step 1: Setup API Keys

Before starting, add your API keys. Create or update the `.env` file in the root directory:

```bash
# Copy the template (if exists) or create a new .env file
```

Add these environment variables:
```env
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
JOOBLE_API_KEY=your_jooble_api_key
```

**Where to get API keys:**
- **Adzuna**: https://developer.adzuna.com/
- **Jooble**: https://api.jooble.org/
- **Remotive** (free): Used as fallback (no key needed)

---

### Step 2: Start the Backend

Open PowerShell/Terminal and navigate to your project folder:

```powershell
cd c:\Users\moham\OneDrive\Desktop\intellidiots\intellidiots
```

Install Python dependencies:
```powershell
pip install -r backend/requirements.txt
```

Start the FastAPI backend server:
```powershell
uvicorn backend.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ Backend is now running at: **http://localhost:8000**

---

### Step 3: Start the Frontend

Open a **NEW** PowerShell/Terminal window:

```powershell
cd c:\Users\moham\OneDrive\Desktop\intellidiots\intellidiots\frontend
```

Install Node dependencies:
```powershell
npm install
```

Start the React frontend:
```powershell
npm start
```

The browser will automatically open to:
✅ Frontend is now running at: **http://localhost:3000**

---

## Option 2: Run with Docker (Production-Ready)

### Step 1: Setup API Keys

Create a `.env` file in the root directory:
```env
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
JOOBLE_API_KEY=your_jooble_api_key
```

### Step 2: Start with Docker Compose

Open PowerShell in your project folder:

```powershell
cd c:\Users\moham\OneDrive\Desktop\intellidiots\intellidiots
docker-compose up --build
```

This will:
- Build the backend image
- Build the frontend image
- Start both services automatically

Wait for both services to start (you'll see "Service running" messages).

✅ Frontend: **http://localhost:3000**
✅ Backend: **http://localhost:8000**

To stop:
```powershell
docker-compose down
```

---

## Testing the Application

### Check Backend Health

Open your browser or use PowerShell:

```powershell
# Health check endpoint
Invoke-WebRequest -Uri http://localhost:8000/health

# API endpoints available
Invoke-WebRequest -Uri http://localhost:8000/
```

Expected response:
```json
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

### View API Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Main Features

1. **Resume Upload & Analysis**
   - Upload PDF, DOCX, or TXT resumes
   - Get ATS score and feedback
   - Analyze skills and keywords

2. **Job Recommendations**
   - Get job recommendations based on resume
   - Fetches from Adzuna, Jooble, and Remotive APIs
   - Filter by keywords, location, salary

3. **Skills Demand**
   - View trending skills in the market
   - Compare your skills with demand

---

## Troubleshooting

### Backend won't start
```powershell
# Verify Python version
python --version

# Install missing dependencies
pip install -r backend/requirements.txt --upgrade

# Check if port 8000 is in use
netstat -ano | findstr :8000
```

### Frontend won't start
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -r node_modules
npm install

# Verify Node version
node --version
```

### API Keys not working
- Double-check your `.env` file is in the root directory
- Verify API keys are correct
- Restart the backend after updating `.env`
- Check backend logs for error messages

### Port already in use
```powershell
# Backend (port 8000)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Frontend (port 3000)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

## Project Structure

```
intellidiots/
├── backend/                 # FastAPI server
│   ├── main.py             # Entry point
│   ├── requirements.txt     # Python dependencies
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   └── utils/              # Helper functions
├── frontend/               # React app
│   ├── package.json        # Node dependencies
│   ├── src/                # React components
│   └── public/             # Static files
├── ml_models/              # ML model files
├── scripts/                # Training scripts
├── docker-compose.yml      # Docker setup
└── .env                    # API keys (create this)
```

---

## Next Steps

1. ✅ Upload a resume to test ATS scoring
2. ✅ Get job recommendations
3. ✅ Train the ML model with your data
4. ✅ Deploy to cloud (Azure, AWS, Heroku)

---

**Happy analyzing!** 🎉

