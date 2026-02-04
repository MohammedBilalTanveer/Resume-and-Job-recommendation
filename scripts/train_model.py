"""
Training Script - Run this to train the ATS model
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import torch
from torch.utils.data import DataLoader

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_models.trainer import ATSModelTrainer, ResumesDataset
from scripts.kaggle_manager import KaggleDatasetManager

def main():
    print("=" * 60)
    print("ATS Model Training Pipeline")
    print("=" * 60)
    
    # Setup paths
    data_dir = './data'
    model_dir = './ml_models'
    
    # Check if datasets exist
    if not os.path.exists(os.path.join(data_dir, 'training_data.csv')):
        print("\n⚠️  Training data not found. Attempting to download from Kaggle...")
        print("\nNote: You need to setup Kaggle API credentials first:")
        print("1. Install: pip install kaggle")
        print("2. Get API key: https://www.kaggle.com/settings/account")
        print("3. Place kaggle.json in ~/.kaggle/")
        
        try:
            manager = KaggleDatasetManager()
            manager.download_datasets(data_dir)
            resumes_df = manager.preprocess_resume_data(data_dir)
            jobs_df = manager.preprocess_job_data(data_dir)
            
            if resumes_df is not None and jobs_df is not None:
                training_df = manager.create_training_data(resumes_df, jobs_df)
            else:
                print("\n✗ Failed to download datasets. Using sample data instead...")
                training_df = create_sample_training_data(data_dir)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("\nUsing sample training data...")
            training_df = create_sample_training_data(data_dir)
    else:
        print(f"\n✓ Loading training data from {data_dir}/training_data.csv")
        training_df = pd.read_csv(os.path.join(data_dir, 'training_data.csv'))
    
    if training_df is None or len(training_df) == 0:
        print("✗ No training data available. Exiting.")
        return
    
    print(f"\n✓ Loaded {len(training_df)} training samples")
    
    # Prepare data
    print("\nPreparing data...")
    X = training_df['resume_text'].values
    y = (training_df['relevance_score'].values > 0.5).astype(int)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Vectorize
    print("Vectorizing text data...")
    vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train).toarray()
    X_test_vec = vectorizer.transform(X_test).toarray()
    
    print(f"✓ Feature matrix shape: {X_train_vec.shape}")
    
    # Initialize trainer
    trainer = ATSModelTrainer(model_dir)
    
    # Train sklearn models
    print("\n" + "=" * 60)
    print("Training scikit-learn models...")
    print("=" * 60)
    sklearn_scores = trainer.train_sklearn_models(
        X_train_vec, y_train, X_test_vec, y_test
    )
    
    # Train neural network
    print("\n" + "=" * 60)
    print("Training Neural Network model...")
    print("=" * 60)
    
    # Create PyTorch datasets
    train_dataset = ResumesDataset(X_train, y_train, vectorizer=vectorizer)
    test_dataset = ResumesDataset(X_test, y_test, vectorizer=vectorizer)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Get input size from vectorizer
    input_size = len(vectorizer.get_feature_names_out())
    print(f"✓ Neural Network input size: {input_size}")
    
    # Train
    nn_model = trainer.train_neural_network(
        train_loader, test_loader, input_size=input_size, epochs=20, lr=0.001
    )
    
    # Save vectorizer
    import joblib
    joblib.dump(vectorizer, os.path.join(model_dir, 'vectorizer.pkl'))
    
    print("\n" + "=" * 60)
    print("✓ Training Complete!")
    print("=" * 60)
    print(f"\nModels saved in: {model_dir}/")
    print("- rf_model.pkl (Random Forest)")
    print("- gb_model.pkl (Gradient Boosting)")
    print("- nn_model.pth (Neural Network)")
    print("- vectorizer.pkl (TF-IDF Vectorizer)")

def create_sample_training_data(data_dir):
    """Create sample training data for demonstration"""
    print("\nGenerating sample training data...")
    
    sample_resumes = [
        "Python developer with 5+ years of experience in Django and FastAPI. Expert in Machine Learning and data science.",
        "Senior Full Stack Engineer. Expertise: React, Node.js, AWS, Docker, PostgreSQL. 8 years experience.",
        "Data Scientist with strong background in ML/AI. Python, TensorFlow, PyTorch, Pandas, NumPy.",
        "DevOps Engineer. Experience with Kubernetes, Docker, CI/CD, AWS, GCP, Terraform.",
        "Frontend Developer. React, TypeScript, Tailwind CSS, Vue.js. 3 years in web development.",
    ]
    
    sample_descriptions = [
        "Seeking Python developer experienced with FastAPI, Django, and cloud deployment.",
        "Full Stack Engineer needed. Must know React, Node.js, and modern DevOps practices.",
        "Machine Learning Engineer position. Requirements: Python, TensorFlow, PyTorch.",
        "DevOps specialist required. Kubernetes, Docker, AWS experience essential.",
        "Frontend Developer wanted. React and TypeScript skills required.",
    ]
    
    # Create sample data
    training_data = []
    for i, resume in enumerate(sample_resumes):
        for j, job_desc in enumerate(sample_descriptions):
            # Simple relevance: higher if indices match
            relevance = 0.8 if i == j else np.random.uniform(0.2, 0.6)
            training_data.append({
                'resume_text': resume,
                'job_description': job_desc,
                'relevance_score': relevance
            })
    
    df = pd.DataFrame(training_data)
    output_path = os.path.join(data_dir, 'training_data.csv')
    os.makedirs(data_dir, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✓ Created sample training data: {len(df)} samples")
    return df

if __name__ == '__main__':
    main()
