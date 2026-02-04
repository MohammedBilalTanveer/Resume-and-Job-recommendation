"""
Example: How to use the Resume ATS System
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def example_1_upload_and_analyze():
    """Example 1: Upload resume and analyze"""
    print("\n" + "="*60)
    print("Example 1: Upload and Analyze Resume")
    print("="*60)
    
    # Sample resume
    resume_text = """
    Senior Software Engineer
    
    SUMMARY
    Experienced software engineer with 6+ years in full-stack development.
    Expertise in Python, JavaScript, React, and cloud technologies.
    
    SKILLS
    - Programming: Python, JavaScript, TypeScript, Java
    - Frontend: React, Vue.js, Tailwind CSS
    - Backend: FastAPI, Django, Node.js, Express
    - Databases: PostgreSQL, MongoDB, Redis
    - Cloud: AWS, Google Cloud, Azure
    - DevOps: Docker, Kubernetes, CI/CD
    - Tools: Git, Jenkins, Docker
    
    EXPERIENCE
    Senior Engineer, Tech Company (2020-Present)
    - Led team of 5 engineers
    - Architected microservices using Python and FastAPI
    - Implemented ML pipeline for data processing
    - Improved API performance by 40%
    
    Junior Engineer, StartUp Inc (2018-2020)
    - Built React-based web applications
    - Developed RESTful APIs using Django
    - Maintained PostgreSQL databases
    
    EDUCATION
    B.Tech Computer Science, University (2018)
    """
    
    # Sample job description
    job_description = """
    Senior Full Stack Engineer
    
    We are looking for a Senior Engineer with:
    - 5+ years of software development experience
    - Strong Python and JavaScript skills
    - Experience with React or Vue.js
    - FastAPI or Django experience
    - AWS or cloud platform experience
    - Docker and Kubernetes knowledge
    - Leadership and mentoring experience
    
    Nice to have:
    - Machine Learning knowledge
    - Microservices architecture
    - CI/CD pipeline setup
    """
    
    # Call API
    payload = {
        "resume_text": resume_text,
        "job_description": job_description
    }
    
    response = requests.post(
        f"{API_BASE_URL}/resume/score",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nATS Score: {result['ats_score']:.1%}")
        print(f"Match Percentage: {result['match_percentage']}%")
        print(f"\nMatching Keywords: {', '.join(result['matching_keywords'])}")
        print(f"\nMissing Keywords: {', '.join(result['missing_keywords'])}")
        print(f"\nScore Breakdown: {json.dumps(result['score_breakdown'], indent=2)}")
    else:
        print(f"Error: {response.text}")

def example_2_extract_skills():
    """Example 2: Extract skills from resume"""
    print("\n" + "="*60)
    print("Example 2: Extract Skills from Resume")
    print("="*60)
    
    resume_text = """
    Full Stack Developer with expertise in:
    Python, JavaScript, React, Django, FastAPI, AWS, Docker, PostgreSQL
    Strong in Machine Learning and Data Science
    """
    
    payload = {"resume_text": resume_text}
    response = requests.post(
        f"{API_BASE_URL}/resume/extract-skills",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nExtracted Skills ({len(result['skills'])}): {', '.join(result['skills'])}")
        print(f"Experience: {result['experience_years']}+ years")
        print(f"Education: {', '.join(result['education'])}")
    else:
        print(f"Error: {response.text}")

def example_3_search_jobs():
    """Example 3: Search for jobs"""
    print("\n" + "="*60)
    print("Example 3: Search for Jobs")
    print("="*60)
    
    params = {
        "keyword": "Python Developer",
        "location": "remote",
        "source": None  # Will search all sources
    }
    
    response = requests.get(
        f"{API_BASE_URL}/jobs/search",
        params=params
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nFound {result['total_jobs']} jobs")
        
        for job in result['jobs'][:3]:  # Show first 3
            print(f"\n- {job['title']}")
            print(f"  Company: {job['company']}")
            print(f"  Location: {job['location']}")
            print(f"  Source: {job['source']}")
    else:
        print(f"Error: {response.text}")

def example_4_get_recommendations():
    """Example 4: Get personalized job recommendations"""
    print("\n" + "="*60)
    print("Example 4: Get Job Recommendations")
    print("="*60)
    
    resume_text = """
    Senior Python Developer
    Skills: Python, FastAPI, Django, PostgreSQL, AWS, Docker
    Experience: 6 years
    """
    
    payload = {
        "resume_text": resume_text,
        "top_k": 5,
        "location": "remote"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/jobs/recommend",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nExtracted Skills: {', '.join(result['extracted_skills'])}")
        print(f"\nRecommended Jobs ({result['total_recommendations']}):")
        
        for job in result['jobs'][:3]:
            print(f"\n- {job['title']}")
            print(f"  Company: {job['company']}")
            print(f"  Location: {job['location']}")
    else:
        print(f"Error: {response.text}")

def example_5_trending_jobs():
    """Example 5: Get trending jobs"""
    print("\n" + "="*60)
    print("Example 5: Trending Jobs")
    print("="*60)
    
    params = {
        "limit": 10,
        "location": "remote"
    }
    
    response = requests.get(
        f"{API_BASE_URL}/jobs/trending",
        params=params
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nTrending Jobs: {result['location']}")
        for i, job in enumerate(result['jobs'][:5], 1):
            print(f"{i}. {job['title']} - {job['company']}")
    else:
        print(f"Error: {response.text}")

def example_6_skills_demand():
    """Example 6: Get skills demand analysis"""
    print("\n" + "="*60)
    print("Example 6: Most In-Demand Skills")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/jobs/skills-demand")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nTop Skills Demand:")
        for i, (skill, count) in enumerate(result['top_skills'][:10], 1):
            print(f"{i}. {skill.title()}: {count} mentions")
    else:
        print(f"Error: {response.text}")

def example_7_health_check():
    """Example 7: Health check"""
    print("\n" + "="*60)
    print("Example 7: API Health Check")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health")
    
    if response.status_code == 200:
        print(f"\n✓ API is healthy: {response.json()}")
    else:
        print(f"✗ API is down")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RESUME ATS SYSTEM - API EXAMPLES")
    print("="*60)
    print("\nMake sure the backend is running: uvicorn backend.main:app --reload")
    
    try:
        # Run examples
        example_7_health_check()
        example_2_extract_skills()
        example_1_upload_and_analyze()
        example_3_search_jobs()
        # example_4_get_recommendations()
        # example_5_trending_jobs()
        # example_6_skills_demand()
        
        print("\n" + "="*60)
        print("✓ All examples completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to API")
        print("Make sure backend is running: uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"\n✗ Error: {e}")
