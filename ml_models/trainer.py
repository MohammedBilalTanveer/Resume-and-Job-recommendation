"""
ML Model Training Pipeline
Trains ATS scoring models using ML/NN approaches
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import joblib
import os
from pathlib import Path

class ResumesDataset(Dataset):
    """Custom PyTorch Dataset for resume data"""
    def __init__(self, resumes, labels, vectorizer=None):
        self.resumes = resumes
        self.labels = labels
        if vectorizer is None:
            self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
            self.X = self.vectorizer.fit_transform(resumes).toarray()
        else:
            self.vectorizer = vectorizer
            self.X = self.vectorizer.transform(resumes).toarray()
        self.X = torch.FloatTensor(self.X)
        self.labels = torch.FloatTensor(labels)
    
    def __len__(self):
        return len(self.resumes)
    
    def __getitem__(self, idx):
        return self.X[idx], self.labels[idx]


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


class ATSModelTrainer:
    """Trainer for ATS models"""
    def __init__(self, model_dir='./ml_models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def train_sklearn_models(self, X_train, y_train, X_test, y_test):
        """Train sklearn models (Random Forest, Gradient Boosting)"""
        print("Training Random Forest...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf_model.fit(X_train, y_train)
        rf_score = rf_model.score(X_test, y_test)
        print(f"Random Forest Accuracy: {rf_score:.4f}")
        
        # Save model
        joblib.dump(rf_model, os.path.join(self.model_dir, 'rf_model.pkl'))
        
        print("Training Gradient Boosting...")
        gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        gb_model.fit(X_train, y_train)
        gb_score = gb_model.score(X_test, y_test)
        print(f"Gradient Boosting Accuracy: {gb_score:.4f}")
        
        # Save model
        joblib.dump(gb_model, os.path.join(self.model_dir, 'gb_model.pkl'))
        
        return {'rf': rf_score, 'gb': gb_score}
    
    def train_neural_network(self, train_loader, val_loader, input_size=500, epochs=20, lr=0.001):
        """Train neural network model"""
        model = ATSNeuralNetwork(input_size=input_size).to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        criterion = nn.BCELoss()
        
        best_val_loss = float('inf')
        patience = 5
        patience_counter = 0
        
        print("Training Neural Network...")
        for epoch in range(epochs):
            model.train()
            train_loss = 0.0
            
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_X).squeeze()
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validation
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                    outputs = model(batch_X).squeeze()
                    loss = criterion(outputs, batch_y)
                    val_loss += loss.item()
            
            train_loss /= len(train_loader)
            val_loss /= len(val_loader)
            
            print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                torch.save(model.state_dict(), os.path.join(self.model_dir, 'nn_model.pth'))
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print("Early stopping triggered")
                    break
        
        return model
