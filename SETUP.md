# SETUP GUIDE

## Complete Setup Instructions

### System Requirements
- Python 3.10 or higher
- Node.js 16 or higher
- 4GB RAM minimum
- 2GB free disk space

---

## Windows Setup

### 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Go back to root and start backend
cd ..
uvicorn backend.main:app --reload
```

### 2. Frontend Setup (New Terminal)

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## Linux/Mac Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Go back to root and start backend
cd ..
uvicorn backend.main:app --reload
```

### 2. Frontend Setup (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## Docker Setup (All Platforms)

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Steps

```bash
# Build and start all services
docker-compose up --build

# In browser:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

## Model Training Setup

### Prerequisites
```bash
pip install kaggle

# Download API credentials from: https://www.kaggle.com/settings/account
# Extract and place kaggle.json in ~/.kaggle/ directory
```

### Run Training

```powershell
# Windows
cd scripts
python train_model.py
```

```bash
# Linux/Mac
cd scripts
python3 train_model.py
```

---

## Environment Configuration

### Create .env file in root directory:

```env
# Adzuna API (optional)
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

# Jooble API (optional)
JOOBLE_API_KEY=your_api_key

# Frontend API URL
REACT_APP_API_URL=http://localhost:8000/api/v1
```

---

## Verification

### Check Backend
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### Check Frontend
- Open http://localhost:3000 in browser
- You should see the home page

### Check API Documentation
- Visit http://localhost:8000/docs
- You should see Swagger UI with all endpoints

---

## Troubleshooting

### Python not found
- Ensure Python 3.10+ is installed
- Add Python to PATH
- Use `python3` instead of `python` on Linux/Mac

### npm not found
- Ensure Node.js 16+ is installed
- Restart terminal after installation

### Port already in use
```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill process (Windows)
taskkill /PID <PID> /F
```

### Spacy model not found
```bash
python -m spacy download en_core_web_sm
```

### API connection errors
- Ensure backend is running on http://localhost:8000
- Check frontend .env file has correct API_URL
- Check browser console for errors

---

## Next Steps

1. **Upload a Resume**: Go to Resume Analyzer page
2. **Get ATS Score**: Paste a job description to see match
3. **Find Jobs**: Use Job Search to find matching positions
4. **Train Model**: Run train_model.py to improve predictions

---

## Support

For issues or questions, check:
1. README.md for overview
2. API documentation at http://localhost:8000/docs
3. Browser console for frontend errors
4. Terminal output for backend errors
