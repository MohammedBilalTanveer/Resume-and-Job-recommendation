#!/usr/bin/env python3
"""
API Test Suite - Complete Testing Guide
Run this after starting the backend: uvicorn backend.main:app --reload
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

def test_health_check():
    """Test 1: Health Check"""
    print_header("Test 1: Health Check")
    
    try:
        response = requests.get(f"http://localhost:8000/health")
        if response.status_code == 200:
            print_success("Backend is healthy")
            print(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to backend: {e}")
        return False

def test_root_endpoint():
    """Test 2: Root Endpoint"""
    print_header("Test 2: Root Endpoint")
    
    try:
        response = requests.get(f"http://localhost:8000/")
        if response.status_code == 200:
            print_success("Root endpoint working")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print_error(f"Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_extract_skills():
    """Test 3: Extract Skills"""
    print_header("Test 3: Extract Skills from Resume")
    
    resume = """
    Senior Python Developer
    Skills: Python, FastAPI, Django, PostgreSQL, AWS, Docker, Kubernetes
    Experience: 6 years in software development
    Education: B.Tech Computer Science
    Certifications: AWS Solutions Architect
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/resume/extract-skills",
            json={"resume_text": resume}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Skills extracted successfully")
            print(f"Skills found: {data['skills']}")
            print(f"Experience: {data['experience_years']} years")
            print(f"Education: {data['education']}")
            return True
        else:
            print_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_ats_score():
    """Test 4: Calculate ATS Score"""
    print_header("Test 4: Calculate ATS Score")
    
    resume = """
    Senior Python Developer with 6+ years experience.
    Skills: Python, Django, FastAPI, PostgreSQL, AWS, Docker.
    Developed microservices, led team of engineers.
    """
    
    job_desc = """
    Senior Python Developer
    Required: Python, Django, 5+ years, AWS
    Nice to have: Docker, Kubernetes, Microservices
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/resume/score",
            json={
                "resume_text": resume,
                "job_description": job_desc
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("ATS score calculated")
            print(f"Score: {data['score']:.1%}")
            print(f"Percentage: {data['score_percentage']}%")
            print(f"Matching Keywords: {data['matching_keywords']}")
            print(f"Missing Keywords: {data['missing_keywords']}")
            return True
        else:
            print_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_search_jobs():
    """Test 5: Search Jobs"""
    print_header("Test 5: Search for Jobs")
    
    try:
        params = {
            "keyword": "Python Developer",
            "location": "remote"
        }
        
        response = requests.get(
            f"{BASE_URL}/jobs/search",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data['total_jobs']} jobs")
            
            if data['jobs']:
                for i, job in enumerate(data['jobs'][:3], 1):
                    print(f"\n  Job {i}:")
                    print(f"    Title: {job['title']}")
                    print(f"    Company: {job['company']}")
                    print(f"    Location: {job['location']}")
                    print(f"    Source: {job['source']}")
            return True
        else:
            print_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_recommendations():
    """Test 6: Get Job Recommendations"""
    print_header("Test 6: Get Job Recommendations")
    
    resume = """
    Senior Python Developer
    Skills: Python, FastAPI, React, AWS, Docker
    Experience: 6 years
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/jobs/recommend",
            json={
                "resume_text": resume,
                "top_k": 5,
                "location": "remote"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data['total_recommendations']} recommendations")
            print(f"Extracted Skills: {data['extracted_skills']}")
            
            if data['jobs']:
                for i, job in enumerate(data['jobs'][:2], 1):
                    print(f"\n  Job {i}: {job['title']} at {job['company']}")
            return True
        else:
            print_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_sample_score():
    """Test 7: Get Sample Score"""
    print_header("Test 7: Get Sample ATS Score")
    
    try:
        response = requests.get(f"{BASE_URL}/resume/sample-score")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Sample score retrieved")
            print(f"ATS Score: {data['ats_score']:.1%}")
            print(f"Matching: {data['matching_keywords']}")
            print(f"Missing: {data['missing_keywords']}")
            return True
        else:
            print_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_trending_jobs():
    """Test 8: Get Trending Jobs"""
    print_header("Test 8: Get Trending Jobs")
    
    try:
        response = requests.get(
            f"{BASE_URL}/jobs/trending",
            params={"limit": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data['jobs'])} trending jobs")
            
            for i, job in enumerate(data['jobs'][:3], 1):
                print(f"{i}. {job['title']} - {job['company']}")
            return True
        else:
            print_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_skills_demand():
    """Test 9: Get Skills Demand"""
    print_header("Test 9: Get Skills Demand Analysis")
    
    try:
        response = requests.get(f"{BASE_URL}/jobs/skills-demand")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Skills demand data retrieved")
            
            if data.get('top_skills'):
                print("Top 5 In-Demand Skills:")
                for i, (skill, count) in enumerate(data['top_skills'][:5], 1):
                    print(f"{i}. {skill.title()}: {count} mentions")
            return True
        else:
            print_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_model_status():
    """Test 10: Get Model Status"""
    print_header("Test 10: Get Model Status")
    
    try:
        response = requests.get(f"{BASE_URL}/models/status")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Model status retrieved")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print_header("RESUME ATS API TEST SUITE")
    print_info("Running 10 comprehensive API tests...")
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Extract Skills", test_extract_skills),
        ("ATS Scoring", test_ats_score),
        ("Job Search", test_search_jobs),
        ("Job Recommendations", test_recommendations),
        ("Sample Score", test_sample_score),
        ("Trending Jobs", test_trending_jobs),
        ("Skills Demand", test_skills_demand),
        ("Model Status", test_model_status),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            results.append((name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {name:<25} [{status}]")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Results: {Colors.GREEN}{passed}{Colors.END}/{total} tests passed")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    print(f"\n{Colors.YELLOW}Make sure backend is running:{Colors.END}")
    print(f"  uvicorn backend.main:app --reload\n")
    
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}\n")
        sys.exit(1)
