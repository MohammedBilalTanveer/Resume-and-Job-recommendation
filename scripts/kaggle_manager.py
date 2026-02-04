"""
Kaggle Dataset Integration Script
Download and preprocess resume and job description datasets
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

class KaggleDatasetManager:
    """Manager for Kaggle datasets"""
    
    RESUME_DATASETS = {
        'resume_dataset_1': 'gauravduttakiit/resume-dataset',
        'resume_dataset_2': 'snehaanbhawal/resume-dataset',
        'resume_dataset_3': 'tejashvi14/hr-resume-dataset',
    }
    
    JOB_DATASETS = {
        'job_descriptions': 'jithinjoseph/job-description-dataset',
        'indeed_jobs': 'PromptCloudHQ/indeed-job-postings',
    }
    
    @staticmethod
    def download_datasets(data_dir='./data'):
        """
        Download datasets from Kaggle
        Note: Requires kaggle API credentials (~/.kaggle/kaggle.json)
        """
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
        except ImportError:
            print("Install kaggle: pip install kaggle")
            return
        
        api = KaggleApi()
        api.authenticate()
        
        os.makedirs(data_dir, exist_ok=True)
        
        # Download resume datasets
        print("Downloading resume datasets...")
        for name, dataset in KaggleDatasetManager.RESUME_DATASETS.items():
            dataset_path = os.path.join(data_dir, 'resumes', name)
            os.makedirs(dataset_path, exist_ok=True)
            try:
                api.dataset_download_files(dataset, path=dataset_path, unzip=True)
                print(f"✓ Downloaded {name}")
            except Exception as e:
                print(f"✗ Failed to download {name}: {e}")
        
        # Download job datasets
        print("\nDownloading job description datasets...")
        for name, dataset in KaggleDatasetManager.JOB_DATASETS.items():
            dataset_path = os.path.join(data_dir, 'jobs', name)
            os.makedirs(dataset_path, exist_ok=True)
            try:
                api.dataset_download_files(dataset, path=dataset_path, unzip=True)
                print(f"✓ Downloaded {name}")
            except Exception as e:
                print(f"✗ Failed to download {name}: {e}")
    
    @staticmethod
    def preprocess_resume_data(data_dir='./data'):
        """Preprocess and combine resume datasets"""
        resumes = []
        resume_dir = os.path.join(data_dir, 'resumes')
        
        if not os.path.exists(resume_dir):
            print(f"Resume directory not found: {resume_dir}")
            return None
        
        # Look for CSV files with resume data
        for root, dirs, files in os.walk(resume_dir):
            for file in files:
                if file.endswith('.csv'):
                    filepath = os.path.join(root, file)
                    try:
                        df = pd.read_csv(filepath)
                        # Try to find resume column
                        text_col = None
                        for col in ['Resume', 'resume', 'text', 'description', 'content']:
                            if col in df.columns:
                                text_col = col
                                break
                        
                        if text_col:
                            resumes.append(df[[text_col]].rename(columns={text_col: 'resume_text'}))
                            print(f"✓ Loaded {len(df)} resumes from {file}")
                    except Exception as e:
                        print(f"✗ Error loading {file}: {e}")
        
        if resumes:
            combined_df = pd.concat(resumes, ignore_index=True)
            # Remove duplicates
            combined_df = combined_df.drop_duplicates(subset=['resume_text'])
            output_path = os.path.join(data_dir, 'processed_resumes.csv')
            combined_df.to_csv(output_path, index=False)
            print(f"\n✓ Saved {len(combined_df)} unique resumes to {output_path}")
            return combined_df
        
        return None
    
    @staticmethod
    def preprocess_job_data(data_dir='./data'):
        """Preprocess and combine job description datasets"""
        jobs = []
        job_dir = os.path.join(data_dir, 'jobs')
        
        if not os.path.exists(job_dir):
            print(f"Job directory not found: {job_dir}")
            return None
        
        for root, dirs, files in os.walk(job_dir):
            for file in files:
                if file.endswith('.csv'):
                    filepath = os.path.join(root, file)
                    try:
                        df = pd.read_csv(filepath)
                        jobs.append(df)
                        print(f"✓ Loaded {len(df)} jobs from {file}")
                    except Exception as e:
                        print(f"✗ Error loading {file}: {e}")
        
        if jobs:
            combined_df = pd.concat(jobs, ignore_index=True)
            combined_df = combined_df.drop_duplicates()
            output_path = os.path.join(data_dir, 'processed_jobs.csv')
            combined_df.to_csv(output_path, index=False)
            print(f"\n✓ Saved {len(combined_df)} unique jobs to {output_path}")
            return combined_df
        
        return None
    
    @staticmethod
    def create_training_data(resumes_df, jobs_df, output_path='./data/training_data.csv'):
        """
        Create training data by matching resumes to jobs
        """
        if resumes_df is None or jobs_df is None:
            print("Missing data for training")
            return None
        
        # Sample and create pairs
        training_data = []
        
        for idx, resume in resumes_df.iterrows():
            # Sample some random jobs for each resume
            random_jobs = jobs_df.sample(min(5, len(jobs_df)))
            
            for _, job in random_jobs.iterrows():
                # Create training pair (resume, job, relevance_score)
                # In real scenario, this would be labeled manually or using heuristics
                training_data.append({
                    'resume_text': resume.get('resume_text', ''),
                    'job_description': job.get('description', ''),
                    'relevance_score': np.random.uniform(0.3, 0.9)  # Dummy score
                })
        
        training_df = pd.DataFrame(training_data)
        training_df.to_csv(output_path, index=False)
        print(f"✓ Created training data with {len(training_df)} pairs")
        return training_df

# Usage instructions
if __name__ == '__main__':
    print("Kaggle Dataset Manager")
    print("======================")
    print("\n1. Install Kaggle API: pip install kaggle")
    print("2. Setup credentials: https://github.com/Kaggle/kaggle-api#api-credentials")
    print("3. Run this script to download and preprocess datasets")
    
    # Example usage
    # manager = KaggleDatasetManager()
    # manager.download_datasets()
    # resumes = manager.preprocess_resume_data()
    # jobs = manager.preprocess_job_data()
    # training_data = manager.create_training_data(resumes, jobs)
