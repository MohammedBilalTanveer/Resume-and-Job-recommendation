"""
Advanced ATS Scoring System with AI-Powered Analysis
Provides comprehensive resume analysis, scoring, and improvement recommendations
"""

import re
import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import torch
import torch.nn as nn

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[INFO] OpenAI not installed. AI-powered analysis will use fallback.")


class ATSNeuralNetwork(nn.Module):
    """Neural Network model for ATS scoring - matches trained model structure"""
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


class AdvancedATSScorer:
    """
    Advanced ATS Scoring System with:
    - ML/NN-based scoring
    - AI-powered analysis (OpenAI)
    - Section-by-section analysis
    - Detailed improvement recommendations
    - Industry-specific keyword matching
    - Format and structure analysis
    """
    
    # Comprehensive skills database by category
    SKILLS_DATABASE = {
        "programming_languages": [
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "golang",
            "rust", "swift", "kotlin", "php", "scala", "r", "matlab", "perl", "shell", "bash",
            "sql", "html", "css", "sass", "less", "dart", "lua", "haskell", "elixir"
        ],
        "frameworks_libraries": [
            "react", "angular", "vue", "vue.js", "node.js", "nodejs", "express", "django",
            "flask", "fastapi", "spring", "spring boot", ".net", "asp.net", "rails", "laravel",
            "nextjs", "next.js", "nuxt", "gatsby", "svelte", "redux", "mobx", "graphql",
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "opencv",
            "jquery", "bootstrap", "tailwind", "material-ui", "chakra-ui"
        ],
        "cloud_devops": [
            "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "jenkins",
            "terraform", "ansible", "puppet", "chef", "ci/cd", "gitlab", "github actions",
            "circleci", "travis", "cloudformation", "lambda", "ec2", "s3", "rds", "eks",
            "ecs", "fargate", "heroku", "digitalocean", "nginx", "apache", "linux", "unix"
        ],
        "databases": [
            "mysql", "postgresql", "postgres", "mongodb", "redis", "elasticsearch", "cassandra",
            "dynamodb", "firebase", "sqlite", "oracle", "sql server", "mariadb", "neo4j",
            "couchdb", "influxdb", "memcached", "snowflake", "bigquery", "redshift"
        ],
        "data_science_ai": [
            "machine learning", "deep learning", "nlp", "natural language processing",
            "computer vision", "data analysis", "data visualization", "statistics",
            "a/b testing", "neural networks", "random forest", "regression", "classification",
            "clustering", "time series", "reinforcement learning", "transformers", "bert",
            "gpt", "llm", "langchain", "hugging face", "mlops", "feature engineering"
        ],
        "soft_skills": [
            "leadership", "communication", "teamwork", "problem-solving", "analytical",
            "project management", "agile", "scrum", "kanban", "collaboration", "mentoring",
            "presentation", "stakeholder management", "time management", "critical thinking",
            "adaptability", "creativity", "attention to detail", "decision making"
        ],
        "tools_platforms": [
            "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack", "trello",
            "asana", "notion", "figma", "sketch", "adobe", "photoshop", "illustrator",
            "vs code", "intellij", "pycharm", "postman", "swagger", "grafana", "prometheus",
            "datadog", "splunk", "new relic", "sentry", "tableau", "power bi", "excel"
        ],
        "certifications": [
            "aws certified", "azure certified", "gcp certified", "pmp", "scrum master",
            "cissp", "comptia", "cka", "ckad", "terraform certified", "docker certified"
        ]
    }
    
    # ATS-friendly format keywords
    FORMAT_KEYWORDS = {
        "sections": ["experience", "education", "skills", "projects", "certifications",
                    "summary", "objective", "achievements", "awards", "publications"],
        "action_verbs": ["developed", "implemented", "designed", "led", "managed", "created",
                       "built", "improved", "increased", "reduced", "achieved", "delivered",
                       "launched", "optimized", "automated", "collaborated", "mentored",
                       "analyzed", "architected", "engineered", "deployed", "integrated"]
    }
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.rf_model = None
        self.gb_model = None
        self.nn_model = None
        self.vectorizer = None
        self.openai_client = None
        
        self._load_trained_models()
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client if API key is available"""
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY", "")
            if api_key:
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    print("[OK] OpenAI client initialized")
                except Exception as e:
                    print(f"[WARN] Failed to initialize OpenAI: {e}")
                    self.openai_client = None
            else:
                print("[INFO] No OpenAI API key found. Using rule-based analysis.")
    
    def _load_trained_models(self):
        """Load pre-trained ML models"""
        model_dir = Path(__file__).parent.parent.parent / 'ml_models'
        
        try:
            rf_path = model_dir / 'rf_model.pkl'
            if rf_path.exists():
                self.rf_model = joblib.load(rf_path)
                print(f"[OK] Loaded Random Forest model")
            
            gb_path = model_dir / 'gb_model.pkl'
            if gb_path.exists():
                self.gb_model = joblib.load(gb_path)
                print(f"[OK] Loaded Gradient Boosting model")
            
            vec_path = model_dir / 'vectorizer.pkl'
            if vec_path.exists():
                self.vectorizer = joblib.load(vec_path)
                print(f"[OK] Loaded TF-IDF Vectorizer")
            
            nn_path = model_dir / 'nn_model.pth'
            if nn_path.exists() and self.vectorizer:
                try:
                    input_size = len(self.vectorizer.get_feature_names_out())
                    self.nn_model = ATSNeuralNetwork(input_size=input_size).to(self.device)
                    self.nn_model.load_state_dict(torch.load(nn_path, map_location=self.device))
                    self.nn_model.eval()
                    print(f"[OK] Loaded Neural Network model")
                except Exception as e:
                    print(f"[WARN] Failed to load NN model: {e}")
                    self.nn_model = None
            
            print(f"[OK] ML Models Status: RF={bool(self.rf_model)}, GB={bool(self.gb_model)}, NN={bool(self.nn_model)}")
        
        except Exception as e:
            print(f"[WARN] Error loading models: {e}")
    
    def comprehensive_analysis(self, resume_text: str, job_description: str) -> Dict:
        """
        Perform comprehensive ATS analysis
        Returns detailed scoring, analysis, and recommendations
        """
        # Basic extraction
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        # 1. Extract all components
        resume_skills = self._extract_all_skills(resume_lower)
        job_skills = self._extract_all_skills(job_lower)
        resume_sections = self._analyze_resume_structure(resume_text)
        action_verbs = self._extract_action_verbs(resume_text)
        experience_years = self._extract_experience_years(resume_lower)
        education = self._extract_education(resume_lower)
        contact_info = self._extract_contact_info(resume_text)
        
        # 2. Calculate various scores
        skill_analysis = self._analyze_skills(resume_skills, job_skills)
        keyword_analysis = self._analyze_keywords(resume_lower, job_lower)
        format_score = self._analyze_format(resume_text, resume_sections, action_verbs)
        content_similarity = self._calculate_similarity(resume_text, job_description)
        
        # 3. Get ML prediction
        ml_result = self._get_ml_prediction(resume_text)
        
        # 4. Calculate overall ATS score
        overall_score = self._calculate_overall_score(
            skill_analysis["score"],
            keyword_analysis["score"],
            format_score["score"],
            content_similarity,
            ml_result["score"]
        )
        
        # 5. Generate detailed analysis and recommendations
        analysis = self._generate_detailed_analysis(
            resume_text, job_description,
            skill_analysis, keyword_analysis, format_score,
            resume_sections, action_verbs, experience_years
        )
        
        # 6. Get AI-powered recommendations if available
        ai_recommendations = self._get_ai_recommendations(
            resume_text, job_description, overall_score, skill_analysis
        )
        
        # 7. Generate improvement action items
        action_items = self._generate_action_items(
            skill_analysis, keyword_analysis, format_score,
            resume_sections, action_verbs
        )
        
        return {
            "overall_score": round(overall_score, 3),
            "score_percentage": round(overall_score * 100, 1),
            "grade": self._get_grade(overall_score),
            "method": ml_result["method"],
            
            "score_breakdown": {
                "skill_match": round(skill_analysis["score"], 3),
                "keyword_match": round(keyword_analysis["score"], 3),
                "format_score": round(format_score["score"], 3),
                "content_similarity": round(content_similarity, 3),
                "ml_prediction": round(ml_result["score"], 3) if ml_result["score"] else None
            },
            
            "skills_analysis": {
                "matched_skills": skill_analysis["matched"],
                "missing_skills": skill_analysis["missing"],
                "extra_skills": skill_analysis["extra"],
                "match_percentage": round(skill_analysis["score"] * 100, 1),
                "skills_by_category": skill_analysis["by_category"]
            },
            
            "keyword_analysis": {
                "matched_keywords": keyword_analysis["matched"],
                "missing_keywords": keyword_analysis["missing"],
                "keyword_density": keyword_analysis["density"]
            },
            
            "format_analysis": {
                "sections_found": resume_sections,
                "action_verbs_used": action_verbs,
                "action_verbs_count": len(action_verbs),
                "format_issues": format_score["issues"],
                "format_suggestions": format_score["suggestions"]
            },
            
            "extracted_info": {
                "experience_years": experience_years,
                "education": education,
                "contact_info": contact_info,
                "total_skills_found": len(resume_skills["all"])
            },
            
            "detailed_analysis": analysis,
            "ai_recommendations": ai_recommendations,
            "action_items": action_items,
            
            "score_explanation": self._generate_score_explanation(
                overall_score, skill_analysis, keyword_analysis, 
                format_score, content_similarity
            )
        }
    
    def _extract_all_skills(self, text: str) -> Dict:
        """Extract skills by category"""
        skills_found = {"all": [], "by_category": {}}
        
        for category, skills_list in self.SKILLS_DATABASE.items():
            category_skills = []
            for skill in skills_list:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    category_skills.append(skill)
                    skills_found["all"].append(skill)
            
            skills_found["by_category"][category] = category_skills
        
        skills_found["all"] = list(set(skills_found["all"]))
        return skills_found
    
    def _analyze_resume_structure(self, text: str) -> List[str]:
        """Analyze resume sections/structure"""
        sections_found = []
        text_lower = text.lower()
        
        for section in self.FORMAT_KEYWORDS["sections"]:
            # Look for section headers
            patterns = [
                rf'\b{section}\b\s*[:\-]',
                rf'\b{section}\b\s*$',
                rf'^\s*{section}\s*$'
            ]
            for pattern in patterns:
                if re.search(pattern, text_lower, re.MULTILINE | re.IGNORECASE):
                    sections_found.append(section.title())
                    break
        
        return list(set(sections_found))
    
    def _extract_action_verbs(self, text: str) -> List[str]:
        """Extract action verbs used in resume"""
        verbs_found = []
        text_lower = text.lower()
        
        for verb in self.FORMAT_KEYWORDS["action_verbs"]:
            pattern = r'\b' + verb + r'(ed|ing|s)?\b'
            if re.search(pattern, text_lower):
                verbs_found.append(verb)
        
        return list(set(verbs_found))
    
    def _analyze_skills(self, resume_skills: Dict, job_skills: Dict) -> Dict:
        """Analyze skill match between resume and job"""
        resume_set = set(resume_skills["all"])
        job_set = set(job_skills["all"])
        
        matched = resume_set & job_set
        missing = job_set - resume_set
        extra = resume_set - job_set
        
        score = len(matched) / len(job_set) if job_set else 0.5
        
        # Category-wise analysis
        by_category = {}
        for category in self.SKILLS_DATABASE.keys():
            resume_cat = set(resume_skills["by_category"].get(category, []))
            job_cat = set(job_skills["by_category"].get(category, []))
            
            if job_cat:
                by_category[category] = {
                    "matched": list(resume_cat & job_cat),
                    "missing": list(job_cat - resume_cat),
                    "score": len(resume_cat & job_cat) / len(job_cat)
                }
        
        return {
            "matched": sorted(list(matched)),
            "missing": sorted(list(missing)),
            "extra": sorted(list(extra)),
            "score": min(score, 1.0),
            "by_category": by_category
        }
    
    def _analyze_keywords(self, resume: str, job_desc: str) -> Dict:
        """Analyze keyword matching"""
        # Extract meaningful keywords from job description
        job_words = set(re.findall(r'\b[a-z]{3,}\b', job_desc))
        resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume))
        
        # Filter out common stopwords
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'has', 'will',
                    'with', 'this', 'that', 'from', 'they', 'been', 'have', 'its', 'was', 'were',
                    'their', 'what', 'about', 'which', 'when', 'make', 'like', 'just', 'over'}
        
        job_words = job_words - stopwords
        resume_words = resume_words - stopwords
        
        matched = job_words & resume_words
        missing = job_words - resume_words
        
        score = len(matched) / len(job_words) if job_words else 0.5
        
        # Calculate keyword density
        total_words = len(resume.split())
        keyword_count = sum(1 for word in resume.split() if word.lower() in job_words)
        density = keyword_count / total_words if total_words > 0 else 0
        
        return {
            "matched": sorted(list(matched))[:30],  # Top 30
            "missing": sorted(list(missing))[:20],  # Top 20
            "score": min(score, 1.0),
            "density": round(density * 100, 2)
        }
    
    def _analyze_format(self, text: str, sections: List[str], action_verbs: List[str]) -> Dict:
        """Analyze resume format and structure"""
        issues = []
        suggestions = []
        score = 1.0
        
        # Check for important sections
        important_sections = ["experience", "education", "skills"]
        for section in important_sections:
            if section.title() not in sections:
                issues.append(f"Missing '{section.title()}' section")
                suggestions.append(f"Add a clear '{section.title()}' section")
                score -= 0.1
        
        # Check action verbs
        if len(action_verbs) < 5:
            issues.append("Limited use of action verbs")
            suggestions.append("Use more action verbs like 'developed', 'implemented', 'led', 'achieved'")
            score -= 0.1
        
        # Check length
        word_count = len(text.split())
        if word_count < 200:
            issues.append("Resume appears too short")
            suggestions.append("Add more detail about your experience and achievements")
            score -= 0.15
        elif word_count > 1000:
            issues.append("Resume may be too long")
            suggestions.append("Consider condensing to highlight key achievements")
            score -= 0.05
        
        # Check for quantifiable achievements
        has_numbers = bool(re.search(r'\b\d+[%+]?\b', text))
        if not has_numbers:
            issues.append("No quantifiable achievements found")
            suggestions.append("Add metrics like '20% improvement' or 'managed team of 5'")
            score -= 0.1
        
        # Check contact info
        has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
        has_phone = bool(re.search(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', text))
        
        if not has_email:
            issues.append("No email address found")
            suggestions.append("Include your professional email address")
            score -= 0.05
        
        if not has_phone:
            issues.append("No phone number found")
            suggestions.append("Include your phone number")
            score -= 0.05
        
        return {
            "score": max(score, 0.0),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _calculate_similarity(self, resume: str, job_desc: str) -> float:
        """Calculate content similarity using TF-IDF"""
        try:
            if self.vectorizer:
                resume_vec = self.vectorizer.transform([resume]).toarray()
                job_vec = self.vectorizer.transform([job_desc]).toarray()
            else:
                temp_vec = TfidfVectorizer(stop_words='english', max_features=100)
                vectors = temp_vec.fit_transform([resume, job_desc]).toarray()
                resume_vec = vectors[0].reshape(1, -1)
                job_vec = vectors[1].reshape(1, -1)
            
            similarity = cosine_similarity(resume_vec, job_vec)[0][0]
            return float(similarity)
        except:
            return 0.5
    
    def _get_ml_prediction(self, resume_text: str) -> Dict:
        """Get ML model prediction"""
        ml_score = None
        method = "rule_based"
        
        if self.nn_model and self.vectorizer:
            try:
                with torch.no_grad():
                    features = self.vectorizer.transform([resume_text]).toarray()
                    tensor = torch.FloatTensor(features).to(self.device)
                    ml_score = self.nn_model(tensor).item()
                method = "neural_network"
            except Exception as e:
                print(f"[WARN] NN prediction failed: {e}")
        
        elif self.gb_model and self.vectorizer:
            try:
                features = self.vectorizer.transform([resume_text]).toarray()
                ml_score = self.gb_model.predict_proba(features)[0][1]
                method = "gradient_boosting"
            except:
                pass
        
        elif self.rf_model and self.vectorizer:
            try:
                features = self.vectorizer.transform([resume_text]).toarray()
                ml_score = self.rf_model.predict_proba(features)[0][1]
                method = "random_forest"
            except:
                pass
        
        return {"score": ml_score, "method": method}
    
    def _calculate_overall_score(self, skill_score: float, keyword_score: float,
                                  format_score: float, similarity: float,
                                  ml_score: Optional[float]) -> float:
        """Calculate weighted overall ATS score"""
        if ml_score is not None:
            # With ML model
            score = (
                ml_score * 0.30 +       # ML prediction
                skill_score * 0.30 +     # Skill matching
                keyword_score * 0.20 +   # Keyword matching
                format_score * 0.10 +    # Format quality
                similarity * 0.10        # Content similarity
            )
        else:
            # Without ML model
            score = (
                skill_score * 0.40 +
                keyword_score * 0.30 +
                format_score * 0.15 +
                similarity * 0.15
            )
        
        return min(max(score, 0.0), 1.0)
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.90:
            return "A+"
        elif score >= 0.85:
            return "A"
        elif score >= 0.80:
            return "A-"
        elif score >= 0.75:
            return "B+"
        elif score >= 0.70:
            return "B"
        elif score >= 0.65:
            return "B-"
        elif score >= 0.60:
            return "C+"
        elif score >= 0.55:
            return "C"
        elif score >= 0.50:
            return "C-"
        elif score >= 0.40:
            return "D"
        else:
            return "F"
    
    def _generate_detailed_analysis(self, resume: str, job_desc: str,
                                    skill_analysis: Dict, keyword_analysis: Dict,
                                    format_score: Dict, sections: List[str],
                                    action_verbs: List[str], experience: int) -> Dict:
        """Generate detailed text analysis"""
        strengths = []
        weaknesses = []
        
        # Analyze strengths
        if skill_analysis["score"] >= 0.7:
            strengths.append("Strong skill alignment with job requirements")
        if len(skill_analysis["extra"]) > 5:
            strengths.append(f"Has {len(skill_analysis['extra'])} additional relevant skills")
        if len(action_verbs) >= 10:
            strengths.append("Excellent use of action verbs")
        if experience >= 3:
            strengths.append(f"{experience}+ years of experience demonstrated")
        if "Experience" in sections and "Skills" in sections:
            strengths.append("Well-structured resume with clear sections")
        
        # Analyze weaknesses
        if skill_analysis["score"] < 0.5:
            weaknesses.append("Low skill match with job requirements")
        if len(skill_analysis["missing"]) > 5:
            weaknesses.append(f"Missing {len(skill_analysis['missing'])} key skills from job description")
        if len(action_verbs) < 5:
            weaknesses.append("Limited action verb usage")
        if format_score["score"] < 0.7:
            weaknesses.append("Resume format needs improvement")
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "summary": self._generate_summary(skill_analysis, keyword_analysis, format_score)
        }
    
    def _generate_summary(self, skill_analysis: Dict, keyword_analysis: Dict, 
                         format_score: Dict) -> str:
        """Generate analysis summary"""
        avg_score = (skill_analysis["score"] + keyword_analysis["score"] + format_score["score"]) / 3
        
        if avg_score >= 0.8:
            return "Excellent resume! You have strong alignment with the job requirements. Focus on fine-tuning specific keywords and quantifying achievements."
        elif avg_score >= 0.6:
            return "Good foundation! Your resume shows relevant experience but could be strengthened by adding missing skills and optimizing keywords."
        elif avg_score >= 0.4:
            return "Needs improvement. Consider adding more relevant skills, using industry keywords, and restructuring for better ATS compatibility."
        else:
            return "Significant changes needed. Your resume needs substantial updates to match job requirements. Focus on skills alignment and keyword optimization."
    
    def _get_ai_recommendations(self, resume: str, job_desc: str, 
                                score: float, skill_analysis: Dict) -> List[str]:
        """Get AI-powered recommendations using OpenAI"""
        recommendations = []
        
        if self.openai_client:
            try:
                prompt = f"""Analyze this resume against the job description and provide 5 specific, actionable recommendations to improve ATS compatibility.

Current ATS Score: {score*100:.1f}%
Matched Skills: {', '.join(skill_analysis['matched'][:10])}
Missing Skills: {', '.join(skill_analysis['missing'][:10])}

Job Description Summary:
{job_desc[:1000]}

Resume Summary:
{resume[:1500]}

Provide exactly 5 concise, specific recommendations. Each should be actionable and focused on improving ATS score. Format as a numbered list."""

                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert ATS optimization consultant. Provide specific, actionable advice."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                ai_text = response.choices[0].message.content
                # Parse numbered recommendations
                lines = ai_text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # Remove numbering/bullets
                        clean_line = re.sub(r'^[\d\.\-\*]+\s*', '', line)
                        if clean_line:
                            recommendations.append(clean_line)
                
            except Exception as e:
                print(f"[WARN] OpenAI API error: {e}")
                recommendations = self._get_fallback_recommendations(skill_analysis)
        else:
            recommendations = self._get_fallback_recommendations(skill_analysis)
        
        return recommendations[:5]  # Limit to 5
    
    def _get_fallback_recommendations(self, skill_analysis: Dict) -> List[str]:
        """Generate recommendations without AI"""
        recommendations = []
        
        # Skill-based recommendations
        missing = skill_analysis.get("missing", [])
        if missing:
            top_missing = missing[:3]
            recommendations.append(f"Add these high-priority skills to your resume: {', '.join(top_missing)}")
        
        # Category-specific recommendations
        by_category = skill_analysis.get("by_category", {})
        for cat, data in by_category.items():
            if data.get("missing") and data.get("score", 1) < 0.5:
                cat_name = cat.replace("_", " ").title()
                recommendations.append(f"Strengthen your {cat_name} section by adding: {', '.join(data['missing'][:3])}")
        
        # General recommendations
        recommendations.extend([
            "Quantify your achievements with specific numbers and percentages",
            "Use keywords from the job description naturally throughout your resume",
            "Ensure your resume has clear sections: Summary, Experience, Skills, Education",
            "Start bullet points with strong action verbs like 'Developed', 'Led', 'Implemented'",
            "Remove graphics, tables, and complex formatting that ATS systems may not parse"
        ])
        
        return recommendations[:5]
    
    def _generate_action_items(self, skill_analysis: Dict, keyword_analysis: Dict,
                               format_score: Dict, sections: List[str],
                               action_verbs: List[str]) -> List[Dict]:
        """Generate prioritized action items"""
        items = []
        
        # High priority: Missing critical skills
        if skill_analysis["missing"]:
            items.append({
                "priority": "high",
                "category": "Skills Gap",
                "action": f"Add these missing skills: {', '.join(skill_analysis['missing'][:5])}",
                "impact": "Could improve score by 10-20%"
            })
        
        # High priority: Missing keywords
        if keyword_analysis["missing"]:
            items.append({
                "priority": "high", 
                "category": "Keywords",
                "action": f"Incorporate these keywords: {', '.join(keyword_analysis['missing'][:5])}",
                "impact": "Could improve ATS parsing by 15%"
            })
        
        # Medium priority: Format issues
        for issue in format_score.get("issues", [])[:3]:
            items.append({
                "priority": "medium",
                "category": "Format",
                "action": issue,
                "impact": "Improves readability and ATS compatibility"
            })
        
        # Low priority: Action verbs
        if len(action_verbs) < 8:
            items.append({
                "priority": "low",
                "category": "Language",
                "action": "Use more action verbs to describe achievements",
                "impact": "Makes resume more impactful"
            })
        
        return items
    
    def _generate_score_explanation(self, overall_score: float, skill_analysis: Dict,
                                    keyword_analysis: Dict, format_score: Dict,
                                    similarity: float) -> str:
        """Generate human-readable score explanation"""
        explanations = []
        
        # Overall assessment
        if overall_score >= 0.8:
            explanations.append("Your resume is highly optimized for this position.")
        elif overall_score >= 0.6:
            explanations.append("Your resume has good potential but needs some optimization.")
        else:
            explanations.append("Your resume needs significant improvements for this role.")
        
        # Skill analysis
        skill_pct = skill_analysis["score"] * 100
        matched_count = len(skill_analysis["matched"])
        missing_count = len(skill_analysis["missing"])
        
        explanations.append(
            f"Skills Match ({skill_pct:.0f}%): You have {matched_count} matching skills. "
            f"{'Consider adding ' + str(missing_count) + ' missing skills.' if missing_count > 0 else 'Great skill alignment!'}"
        )
        
        # Keyword analysis
        keyword_pct = keyword_analysis["score"] * 100
        explanations.append(
            f"Keyword Match ({keyword_pct:.0f}%): "
            f"{'Good keyword density.' if keyword_pct >= 60 else 'Add more relevant keywords from the job description.'}"
        )
        
        # Format analysis
        format_pct = format_score["score"] * 100
        if format_pct >= 80:
            explanations.append(f"Format ({format_pct:.0f}%): Well-structured resume with clear sections.")
        else:
            issues = format_score.get("issues", [])
            explanations.append(f"Format ({format_pct:.0f}%): {issues[0] if issues else 'Some formatting improvements needed.'}")
        
        return " ".join(explanations)
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract years of experience from resume text"""
        patterns = [
            r'(\d+)\+?\s*years?\s*of\s*(?:professional\s*)?experience',
            r'(\d+)\+?\s*(?:years?\s*)?experience',
            r'total\s*(?:of\s*)?(\d+)\s*years?',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:industry|field|sector)',
            r'over\s*(\d+)\s*years?',
            r'more\s*than\s*(\d+)\s*years?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Try to calculate from date ranges (e.g., "2018 - 2024" or "2018 - Present")
        date_patterns = [
            r'(\d{4})\s*[-–—]\s*(\d{4}|present|current|now)',
            r'(\d{4})\s*to\s*(\d{4}|present|current|now)',
        ]
        
        years_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for start, end in matches:
                start_year = int(start)
                if end.lower() in ['present', 'current', 'now']:
                    end_year = 2026  # Current year
                else:
                    end_year = int(end)
                if 1980 <= start_year <= 2026 and start_year <= end_year <= 2030:
                    years_found.append(end_year - start_year)
        
        if years_found:
            return max(years_found)  # Return the longest duration found
        
        return 0
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education qualifications from resume text"""
        education = []
        text_lower = text.lower()
        
        # Look for education section first to avoid false matches from job descriptions
        edu_section_pattern = r'education[\s\S]*?(?=experience|skills|projects|work|interest|honors|$)'
        edu_section_match = re.search(edu_section_pattern, text_lower, re.IGNORECASE)
        edu_text = edu_section_match.group() if edu_section_match else text_lower
        
        # Specific degree patterns - more precise matching with word boundaries
        degree_mappings = [
            # BCA - Bachelor of Computer Applications (with field variations)
            (r'\bbca\s+in\s+([\w\s]+?)(?:\s+with|\s+cgpa|\s+gpa|\s+an|\n|$)', "BCA"),
            (r'\bbca\b(?!\s+in)', "BCA"),
            (r"bachelor'?s?\s+(?:of|in)\s+computer\s+application[s]?", "Bachelor's in Computer Applications"),
            
            # BBA
            (r'\bbba\b', "BBA"),
            (r"bachelor'?s?\s+(?:of|in)\s+business\s+administration", "Bachelor's in Business Administration"),
            
            # B.Tech (must have space/period before tech)
            (r'\bb\.?\s*tech\s+in\s+([\w\s]+?)(?:\s+with|\s+cgpa|\n|$)', "B.Tech"),
            (r'\bb\.?\s*tech\b(?!\s+in)', "B.Tech"),
            
            # B.E. (must be standalone or followed by specific words)
            (r'\bb\.?\s*e\.?\s+in\s+([\w\s]+?)(?:\s+with|\s+cgpa|\n|$)', "B.E."),
            
            # B.Sc
            (r'\bb\.?\s*sc\s+in\s+([\w\s]+?)(?:\s+with|\s+cgpa|\n|$)', "B.Sc"),
            (r'\bb\.?\s*sc\b(?!\s+in)', "B.Sc"),
            (r"bachelor'?s?\s+of\s+science", "B.Sc"),
            
            # B.Com
            (r'\bb\.?\s*com\b', "B.Com"),
            (r"bachelor'?s?\s+of\s+commerce", "Bachelor's in Commerce"),
            
            # MCA
            (r'\bmca\s+in\s+([\w\s]+?)(?:\s+with|\s+cgpa|\n|$)', "MCA"),
            (r'\bmca\b(?!\s+in)', "MCA"),
            (r"master'?s?\s+(?:of|in)\s+computer\s+application[s]?", "Master's in Computer Applications"),
            
            # MBA
            (r'\bmba\b', "MBA"),
            (r"master'?s?\s+(?:of|in)\s+business\s+administration", "MBA"),
            
            # M.Tech (must have space/period before tech)
            (r'\bm\.?\s*tech\s+in\s+([\w\s]+?)(?:\s+with|\s+cgpa|\n|$)', "M.Tech"),
            (r'\bm\.?\s*tech\b(?!\s+in)', "M.Tech"),
            
            # M.E. - skip, too error prone
            
            # M.Sc
            (r'\bm\.?\s*sc\s+in\s+([\w\s]+?)(?:\s+with|\s+cgpa|\n|$)', "M.Sc"),
            (r'\bm\.?\s*sc\b(?!\s+in)', "M.Sc"),
            (r"master'?s?\s+of\s+science", "M.Sc"),
            
            # PhD
            (r'\bph\.?\s*d\.?\b', "PhD"),
            (r'\bdoctorate\b', "Doctorate"),
            
            # Pre-University / 12th - look for specific phrases
            (r'pre[\s-]*university', "Pre-University"),
            (r'\bpuc\b', "Pre-University"),
            (r'\b12th\b', "12th Grade"),
            (r'\bhsc\b', "Higher Secondary"),
            (r'\bintermediate\b', "Intermediate"),
            
            # 10th / Secondary
            (r'\b10th\b', "10th Grade"),
            (r'\bssc\b', "Secondary School"),
            
            # Diploma - must be followed by 'in'
            (r'\bdiploma\s+in\s+([\w\s]+?)(?:\s+with|\s+cgpa|\n|$)', "Diploma"),
        ]
        
        for pattern, degree_name in degree_mappings:
            match = re.search(pattern, edu_text, re.IGNORECASE)
            if match:
                # Check if there's a captured group (field of study)
                if match.lastindex and match.group(1):
                    field = match.group(1).strip()
                    # Clean up field - remove common trailing words and short garbage
                    field = re.sub(r'\s*(with|cgpa|gpa|an|overall|the|currently|pursuing).*$', '', field, flags=re.IGNORECASE).strip()
                    field = field.title()
                    # Only add field if it's meaningful (more than 3 chars and not garbage)
                    if field and len(field) > 3 and not any(x in field.lower() for x in ['ngaluru', 'ster', 'lore', 'india', 'august', 'june', 'july']):
                        education.append(f"{degree_name} in {field}")
                    else:
                        education.append(degree_name)
                else:
                    education.append(degree_name)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_education = []
        for ed in education:
            # Normalize for comparison
            ed_normalized = ed.lower()
            if ed_normalized not in seen:
                seen.add(ed_normalized)
                unique_education.append(ed)
        
        return unique_education if unique_education else []
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information"""
        contact = {}
        
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if email_match:
            contact["email"] = email_match.group()
        
        phone_match = re.search(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', text)
        if phone_match:
            contact["phone"] = phone_match.group()
        
        linkedin_match = re.search(r'linkedin\.com/in/[^\s]+', text)
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group()
        
        github_match = re.search(r'github\.com/[^\s]+', text)
        if github_match:
            contact["github"] = github_match.group()
        
        return contact


# Create singleton instance
advanced_ats_scorer = AdvancedATSScorer()
