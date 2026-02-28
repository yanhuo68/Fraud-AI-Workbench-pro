# Tab 5 and 6 Deployment Templates
# This file contains templates for deployment scripts

DOCKER_TEMPLATE = """FROM python:3.9-slim

WORKDIR /app

# Copy model and dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY data/models/ ./models/
COPY data/ml/features.json ./data/ml/

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
"""

FASTAPI_APP_TEMPLATE = """from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import json
from typing import List, Dict, Any

app = FastAPI(title="Fraud Detection API", version="1.0.0")

# Load model and features
MODEL_PATH = "models/best_model.pkl"
FEATURES_PATH = "data/ml/features.json"

model = None
feature_names = []

@app.on_event("startup")
async def load_model():
    global model, feature_names
    model = joblib.load(MODEL_PATH)
    with open(FEATURES_PATH, 'r') as f:
        feature_names = json.load(f)
    print(f"Model loaded: {MODEL_PATH}")
    print(f"Expected features ({len(feature_names)}): {feature_names[:5]}...")

class Transaction(BaseModel):
    features: Dict[str, Any]

class PredictionResponse(BaseModel):
    fraud_probability: float
    is_fraud: bool
    model_version: str = "1.0.0"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionResponse)
async def predict(transaction: Transaction):
    try:
        # Convert to DataFrame with correct feature order
        df = pd.DataFrame([transaction.features])
        
        # Align columns to expected features
        df_aligned = df.reindex(columns=feature_names, fill_value=0)
        
        # Predict
        prob = model.predict_proba(df_aligned.values)[:, 1][0]
        
        return PredictionResponse(
            fraud_probability=float(prob),
            is_fraud=bool(prob > 0.5)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Fraud Detection API", "docs": "/docs"}
"""

DOCKER_COMPOSE_TEMPLATE = """version: '3.8'

services:
  fraud-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/app/models/best_model.pkl
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
"""

REQUIREMENTS_TEMPLATE = """fastapi==0.104.1
uvicorn[standard]==0.24.0
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
joblib==1.3.2
pydantic==2.5.0
"""

DEPLOY_SH_TEMPLATE = """#!/bin/bash
# Deployment script for Docker

echo "Building Docker image..."
docker build -t fraud-detection-api:latest .

echo "Starting container..."
docker-compose up -d

echo "Checking health..."
sleep 5
curl http://localhost:8000/health

echo ""
echo "API is running at: http://localhost:8000"
echo "API Docs at: http://localhost:8000/docs"
echo ""
echo "Test with:"
echo 'curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '"'"'{"features": {...}}'"'"''
"""

AZURE_SCORE_TEMPLATE = """import json
import joblib
import pandas as pd
from azureml.core.model import Model

def init():
    global model, feature_names
    model_path = Model.get_model_path('fraud_model')
    model = joblib.load(model_path)
    
    # Load features
    with open('features.json', 'r') as f:
        feature_names = json.load(f)

def run(raw_data):
    try:
        data = json.loads(raw_data)
        df = pd.DataFrame([data])
        df_aligned = df.reindex(columns=feature_names, fill_value=0)
        
        prob = model.predict_proba(df_aligned.values)[:, 1][0]
        
        return json.dumps({
            'fraud_probability': float(prob),
            'is_fraud': bool(prob > 0.5)
        })
    except Exception as e:
        return json.dumps({'error': str(e)})
"""

AWS_INFERENCE_TEMPLATE = """import json
import joblib
import pandas as pd
import os

model = None
feature_names = []

def model_fn(model_dir):
    global model, feature_names
    model = joblib.load(os.path.join(model_dir, 'model.pkl'))
    with open(os.path.join(model_dir, 'features.json'), 'r') as f:
        feature_names = json.load(f)
    return model

def input_fn(request_body, content_type='application/json'):
    if content_type == 'application/json':
        data = json.loads(request_body)
        return pd.DataFrame([data])
    raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model):
    global feature_names
    df_aligned = input_data.reindex(columns=feature_names, fill_value=0)
    prob = model.predict_proba(df_aligned.values)[:, 1][0]
    return {'fraud_probability': float(prob), 'is_fraud': bool(prob > 0.5)}

def output_fn(prediction, accept='application/json'):
    if accept == 'application/json':
        return json.dumps(prediction), accept
    raise ValueError(f"Unsupported accept type: {accept}")
"""

GCP_PREDICTOR_TEMPLATE = """from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import pandas as pd
import joblib
import json

class FraudPredictor:
    def __init__(self):
        self.model = joblib.load('model.pkl')
        with open('features.json', 'r') as f:
            self.feature_names = json.load(f)
    
    def predict(self, instances):
        results = []
        for instance in instances:
            df = pd.DataFrame([instance])
            df_aligned = df.reindex(columns=self.feature_names, fill_value=0)
            prob = self.model.predict_proba(df_aligned.values)[:, 1][0]
            results.append({
                'fraud_probability': float(prob),
                'is_fraud': bool(prob > 0.5)
            })
        return results
"""
