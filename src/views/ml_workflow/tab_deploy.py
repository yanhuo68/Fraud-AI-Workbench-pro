import streamlit as st
import os

from ml.deployment_templates import (
    DOCKER_TEMPLATE, FASTAPI_APP_TEMPLATE, DOCKER_COMPOSE_TEMPLATE,
    REQUIREMENTS_TEMPLATE, DEPLOY_SH_TEMPLATE, AZURE_SCORE_TEMPLATE,
    AWS_INFERENCE_TEMPLATE, GCP_PREDICTOR_TEMPLATE
)

def render_deploy_tab(can_control):
    st.header("Step 5: Deploy Your Model 🚀")
    st.info("Generate production-ready deployment scripts for various platforms.")
    
    model_dir = "data/models"
    if not os.path.exists(model_dir) or not os.listdir(model_dir):
        st.warning("⚠️ No trained model found! Train a model in Tab 2 first.")
        st.stop()
    
    st.subheader("5.1 Select Deployment Target")
    deployment_target = st.selectbox(
        "Choose Platform",
        ["Docker (Local Container)", "FastAPI (REST API Server)", "Azure ML", "AWS SageMaker", "GCP Vertex AI"],
        key="deploy_target"
    )
    
    if can_control:
        deploy_btn = st.button("🎯 Generate Deployment Package", type="primary")
    else:
        st.button("🎯 Generate Deployment Package", type="primary", disabled=True, help="Admin access required")
        deploy_btn = False

    if deploy_btn:
        st.success(f"✅ Generated deployment package for: {deployment_target}")
        
        if deployment_target == "Docker (Local Container)":
            st.subheader("📦 Dockerfile")
            st.code(DOCKER_TEMPLATE, language="dockerfile")
            
            st.subheader("📦 docker-compose.yml")
            st.code(DOCKER_COMPOSE_TEMPLATE, language="yaml")
            
            st.subheader("📦 app.py (FastAPI Server)")
            st.code(FASTAPI_APP_TEMPLATE, language="python")
            
            st.subheader("📦 requirements.txt")
            st.code(REQUIREMENTS_TEMPLATE, language="text")
            
            st.subheader("📦 deploy.sh")
            st.code(DEPLOY_SH_TEMPLATE, language="bash")
            
            st.markdown("---")
            st.subheader("🧪 Test Your Deployment")
            st.code("""# Example API Call
curl -X POST "http://localhost:8000/predict" \\
  -H "Content-Type: application/json" \\
  -d '{
    "features": {
      "Transaction_Amount": 50000,
      "Time_of_Transaction": 15,
      "Previous_Fraudulent_Transactions": 0,
      "Account_Age": 90,
      "Number_of_Transactions_Last_24H": 1
    }
  }'
""", language="bash")
            
        elif deployment_target == "FastAPI (REST API Server)":
            st.subheader("📦 app.py")
            st.code(FASTAPI_APP_TEMPLATE, language="python")
            
            st.subheader("📦 requirements.txt")
            st.code(REQUIREMENTS_TEMPLATE, language="text")
            
            st.subheader("📦 run.sh")
            st.code("""#!/bin/bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
""", language="bash")
            
        elif deployment_target == "Azure ML":
            st.subheader("📦 score.py (Azure Entry Script)")
            st.code(AZURE_SCORE_TEMPLATE, language="python")
            
            st.subheader("📦 conda.yml")
            st.code("""name: fraud_env
dependencies:
  - python=3.9
  - pip:
    - azureml-defaults
    - scikit-learn==1.3.2
    - pandas==2.1.3
    - joblib==1.3.2
""", language="yaml")
            
            st.subheader("📦 deploy_azure.sh")
            st.code("""#!/bin/bash
# Azure ML Deployment Script

# Register model
az ml model register \\
  --name fraud_model \\
  --model-path ./data/models/best_model.pkl \\
  --workspace-name YOUR_WORKSPACE

# Deploy to Azure Container Instance
az ml model deploy \\
  --name fraud-api \\
  --model fraud_model:1 \\
  --inference-config-file inference-config.yml \\
  --deploy-config-file deploy-config.yml \\
  --workspace-name YOUR_WORKSPACE
""", language="bash")
            
        elif deployment_target == "AWS SageMaker":
            st.subheader("📦 inference.py (SageMaker Handler)")
            st.code(AWS_INFERENCE_TEMPLATE, language="python")
            
            st.subheader("📦 deploy_sagemaker.py")
            st.code("""import boto3
import sagemaker
from sagemaker.sklearn.model import SKLearnModel

# Initialize SageMaker session
sagemaker_session = sagemaker.Session()
role = sagemaker.get_execution_role()

# Package and deploy
sklearn_model = SKLearnModel(
    model_data='s3://your-bucket/model.tar.gz',
    role=role,
    entry_point='inference.py',
    framework_version='1.0-1',
    py_version='py3'
)

predictor = sklearn_model.deploy(
    instance_type='ml.t2.medium',
    initial_instance_count=1,
    endpoint_name='fraud-detection-endpoint'
)

print(f"Endpoint deployed: {predictor.endpoint_name}")
""", language="python")
            
        elif deployment_target == "GCP Vertex AI":
            st.subheader("📦 predictor.py")
            st.code(GCP_PREDICTOR_TEMPLATE, language="python")
            
            st.subheader("📦 deploy_gcp.sh")
            st.code("""#!/bin/bash
# GCP Vertex AI Deployment

# Upload model to GCS
gsutil cp ./data/models/best_model.pkl gs://your-bucket/fraud-model/

# Deploy to Vertex AI
gcloud ai models upload \\
  --region=us-central1 \\
  --display-name=fraud-detection \\
  --artifact-uri=gs://your-bucket/fraud-model/ \\
  --container-image-uri=gcr.io/cloud-aiplatform/prediction/sklearn-cpu.1-0:latest

# Create endpoint
gcloud ai endpoints create \\
  --region=us-central1 \\
  --display-name=fraud-endpoint

# Deploy model to endpoint
gcloud ai endpoints deploy-model ENDPOINT_ID \\
  --region=us-central1 \\
  --model=MODEL_ID \\
  --display-name=fraud-v1 \\
  --machine-type=n1-standard-2 \\
  --min-replica-count=1 \\
  --max-replica-count=3
""", language="bash")
