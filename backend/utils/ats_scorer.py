import re
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib
import torch
import torch.nn as nn
import os
from pathlib import Path

import os
from pathlib import Path

class ATSNeuralNetwork(nn.Module):
    """Neural Network model for ATS scoring"""
    def __init__(self, input_size=500, hidden_size=256):
        super(ATSNeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, min(hidden_size, input_size // 2))
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.3)
        
        self.fc2 = nn.Linear(min(hidden_size, input_size // 2), 128)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.2)
        
        self.fc3 = nn.Linear(128, 64)
        self.relu3 = nn.ReLU()
        
        self.fc4 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.dropout1(x)
        
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.dropout2(x)
        
        x = self.fc3(x)
        x = self.relu3(x)
        
        x = self.fc4(x)
        x = self.sigmoid(x)
        
        return x

class ATSScorer:
    """
    ATS Score calculator using TF-IDF and skill matching.
    Computes match between resume and job description.
    """
    
    # Comprehensive skill dictionary
    SKILLS_DICT = {
        "programming_languages": [
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "php", "ruby", "kotlin", "swift", "scala", "r", "matlab", "perl", "dart"
        ],
        "web_frameworks": [
            "react", "angular", "vue", "django", "flask", "fastapi", "express",
            "spring", "asp.net", "laravel", "rails", "nextjs", "nuxt", "gatsby"
        ],
        "databases": [
            "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
            "dynamodb", "firestore", "oracle", "sql server", "mariadb", "sqlite"
        ],
        "cloud_platforms": [
            "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean",
            "linode", "ibm cloud", "oracle cloud", "alibaba cloud"
        ],
        "devops_tools": [
            "docker", "kubernetes", "jenkins", "gitlab", "github", "bitbucket",
            "terraform", "ansible", "puppet", "chef", "circleci", "travis",
            "gitlab ci", "github actions"
        ],
        "data_science": [
            "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
            "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "plotly",
            "nlp", "computer vision", "cv", "neural networks", "nns", "lstm",
            "cnn", "rnn", "regression", "classification", "clustering"
        ],
        "soft_skills": [
            "leadership", "communication", "teamwork", "problem solving",
            "time management", "project management", "agile", "scrum",
            "critical thinking", "analytical skills", "attention to detail"
        ]
    }
    
    # Weight multipliers for different skill categories
    SKILL_WEIGHTS = {
        "programming_languages": 1.0,
        "web_frameworks": 1.2,
        "databases": 0.8,
        "cloud_platforms": 1.0,
        "devops_tools": 1.0,
        "data_science": 1.5,
        "soft_skills": 0.5
    }
    
    def __init__(self):
        """Initialize ATS Scorer with trained ML/NN models."""
        self.nlp = None  # Spacy not used
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize ML models as None
        self.rf_model = None
        self.gb_model = None
        self.nn_model = None
        self.vectorizer = None
        
        # Load trained models if they exist
        self._load_trained_models()
    
    def _load_trained_models(self):
        """Load trained ML/NN models from disk."""
        model_dir = Path(__file__).parent.parent.parent / 'ml_models'
        
        try:
            # Load Random Forest model
            rf_path = model_dir / 'rf_model.pkl'
            if rf_path.exists():
                self.rf_model = joblib.load(rf_path)
                print(f"[OK] Loaded Random Forest model from {rf_path}")
            
            # Load Gradient Boosting model
            gb_path = model_dir / 'gb_model.pkl'
            if gb_path.exists():
                self.gb_model = joblib.load(gb_path)
                print(f"[OK] Loaded Gradient Boosting model from {gb_path}")
            
            # Load TF-IDF Vectorizer
            vec_path = model_dir / 'vectorizer.pkl'
            if vec_path.exists():
                self.vectorizer = joblib.load(vec_path)
                print(f"[OK] Loaded TF-IDF Vectorizer from {vec_path}")
            
            # Load Neural Network model
            nn_path = model_dir / 'nn_model.pth'
            if nn_path.exists() and self.vectorizer:
                try:
                    input_size = len(self.vectorizer.get_feature_names_out())
                    self.nn_model = ATSNeuralNetwork(input_size=input_size).to(self.device)
                    self.nn_model.load_state_dict(torch.load(nn_path, map_location=self.device))
                    self.nn_model.eval()
                    print(f"[OK] Loaded Neural Network model from {nn_path}")
                except Exception as e:
                    print(f"[WARN] Failed to load Neural Network model: {e}")
                    self.nn_model = None
            
            print(f"[OK] ML Models Status: RF={bool(self.rf_model)}, GB={bool(self.gb_model)}, NN={bool(self.nn_model)}")
        
        except Exception as e:
            print(f"[WARN] Error loading trained models: {e}")
            print("[WARN] Using rule-based ATS scoring as fallback")
    
    def extract_resume_info(self, resume_text: str) -> Dict:
        """
        Extract structured information from resume.
        Returns: skills, experience, education, contact info, etc.
        """
        resume_text_lower = resume_text.lower()
        
        extracted = {
            "skills": self._extract_skills(resume_text_lower),
            "experience_years": self._extract_experience_years(resume_text_lower),
            "education": self._extract_education(resume_text_lower),
            "certifications": self._extract_certifications(resume_text_lower),
            "contact_info": self._extract_contact_info(resume_text),
            "raw_text": resume_text
        }
        
        return extracted
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text."""
        skills_found = []
        
        for category, skills_list in self.SKILLS_DICT.items():
            for skill in skills_list:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    skills_found.append(skill)
        
        # Remove duplicates and sort
        return sorted(list(set(skills_found)))
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract years of experience."""
        # Look for patterns like "5+ years" or "5 years of experience"
        patterns = [
            r'(\d+)\+?\s*years?\s*of\s*(?:professional\s*)?experience',
            r'(\d+)\+?\s*(?:years?\s*)?experience',
            r'total\s*(?:of\s*)?(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education qualifications."""
        education = []
        
        degrees = ["bachelor", "master", "phd", "b.tech", "m.tech", "b.s", "m.s",
                   "b.a", "m.a", "diploma", "b.com", "m.com"]
        
        for degree in degrees:
            if degree in text:
                education.append(degree.title())
        
        return list(set(education))
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications."""
        certifications = []
        
        cert_keywords = [
            "aws certified", "google certified", "azure certified",
            "scrum master", "pmp", "certified", "certification",
            "license"
        ]
        
        for cert in cert_keywords:
            if cert in text:
                # Try to extract the full certification name
                pattern = r'[^.]*' + re.escape(cert) + r'[^.]*'
                matches = re.findall(pattern, text, re.IGNORECASE)
                certifications.extend(matches)
        
        return list(set(certifications))
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information."""
        contact = {}
        
        # Email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact["email"] = email_match.group()
        
        # Phone (basic pattern)
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact["phone"] = phone_match.group()
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[^\s]+'
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group()
        
        return contact
    
    def calculate_ats_score(self, resume_text: str, job_description: str) -> Dict:
        """
        Calculate ATS score using trained ML/NN models or rule-based fallback.
        
        Returns:
            {
                "score": 0-1,
                "matching_keywords": [],
                "missing_keywords": [],
                "breakdown": {},
                "method": "neural_network" | "random_forest" | "gradient_boosting" | "rule_based"
            }
        """
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        # Extract skills from both
        resume_skills = self._extract_skills(resume_lower)
        job_skills = self._extract_skills(job_lower)
        
        # Calculate skill match
        matching_skills = set(resume_skills) & set(job_skills)
        missing_skills = set(job_skills) - set(resume_skills)
        
        # Calculate skill-based score
        if job_skills:
            skill_score = len(matching_skills) / len(job_skills)
        else:
            skill_score = 0.5
        
        # Calculate TF-IDF similarity
        try:
            if self.vectorizer:
                # Use trained vectorizer
                resume_vec = self.vectorizer.transform([resume_text]).toarray()
                job_vec = self.vectorizer.transform([job_description]).toarray()
            else:
                # Fallback to new vectorizer
                temp_vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
                vectors = temp_vectorizer.fit_transform([resume_text, job_description]).toarray()
                resume_vec = vectors[0].reshape(1, -1)
                job_vec = vectors[1].reshape(1, -1)
            
            tfidf_similarity = cosine_similarity(resume_vec, job_vec)[0][0]
        except:
            tfidf_similarity = 0.5
        
        # Calculate keyword matching score
        keywords_score = self._calculate_keyword_score(resume_lower, job_lower)
        
        # Try to use trained ML models
        ml_score = None
        method = "rule_based"
        
        if self.nn_model and self.vectorizer:
            try:
                # Use Neural Network for prediction
                with torch.no_grad():
                    resume_features = self.vectorizer.transform([resume_text]).toarray()
                    resume_tensor = torch.FloatTensor(resume_features).to(self.device)
                    nn_output = self.nn_model(resume_tensor)
                    ml_score = nn_output.item()
                method = "neural_network"
            except Exception as e:
                print(f"⚠ NN prediction failed: {e}")
                ml_score = None
        
        elif self.gb_model and self.vectorizer:
            try:
                # Use Gradient Boosting for prediction
                resume_features = self.vectorizer.transform([resume_text]).toarray()
                ml_score = self.gb_model.predict_proba(resume_features)[0][1]
                method = "gradient_boosting"
            except Exception as e:
                print(f"⚠ GB prediction failed: {e}")
                ml_score = None
        
        elif self.rf_model and self.vectorizer:
            try:
                # Use Random Forest for prediction
                resume_features = self.vectorizer.transform([resume_text]).toarray()
                ml_score = self.rf_model.predict_proba(resume_features)[0][1]
                method = "random_forest"
            except Exception as e:
                print(f"⚠ RF prediction failed: {e}")
                ml_score = None
        
        # Combine scores
        if ml_score is not None:
            # Use ML model score with skill and keyword matching
            final_score = (
                ml_score * 0.5 +           # ML model prediction (highest weight)
                skill_score * 0.25 +       # Skill matching
                keywords_score * 0.25      # Keyword matching
            )
        else:
            # Fallback to rule-based scoring
            final_score = (
                skill_score * 0.4 +
                tfidf_similarity * 0.3 +
                keywords_score * 0.3
            )
        
        # Ensure score is between 0 and 1
        final_score = min(max(final_score, 0), 1)
        
        return {
            "score": round(final_score, 3),
            "score_percentage": round(final_score * 100, 2),
            "matching_keywords": sorted(list(matching_skills)),
            "missing_keywords": sorted(list(missing_skills)),
            "breakdown": {
                "skill_match": round(skill_score, 3),
                "content_similarity": round(tfidf_similarity, 3),
                "keyword_score": round(keywords_score, 3),
                "ml_model_score": round(ml_score, 3) if ml_score else None
            },
            "method": method  # Show which method was used
        }
    
    def _calculate_keyword_score(self, resume: str, job_desc: str) -> float:
        """Calculate keyword matching score."""
        # Extract important keywords from job description
        job_words = set(re.findall(r'\b[a-z]{3,}\b', job_desc))
        resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume))
        
        common_words = job_words & resume_words
        
        if not job_words:
            return 0.5
        
        return len(common_words) / len(job_words)
