from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd
import logging

from ml.model_loader import load_model, load_features
from ml.live_preprocessing import prepare_live_data
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Model cache to avoid reloading
model_cache = {}


class ScoreRequest(BaseModel):
    """ML scoring request."""
    model_path: str
    features_path: str
    row: Dict[str, Any]


@router.post("/score")
def score(data: ScoreRequest):
    """
    Score a single row using a trained model.
    
    Args:
        data: Scoring request with model path, features path, and row data
    
    Returns:
        JSON with fraud probability and features
    """
    try:
        logger.info(f"Scoring request for model: {data.model_path}")
        
        # Validate paths
        model_path = data.model_path
        features_path = data.features_path
        
        # Load model (with caching)
        try:
            if model_path not in model_cache:
                logger.info(f"Loading model from {model_path}")
                model_cache[model_path] = load_model(model_path)
            model = model_cache[model_path]
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Model not found: {model_path}"
            )
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load model: {str(e)}"
            )
        
        # Load features
        try:
            feature_names = load_features(features_path)
            logger.info(f"Loaded {len(feature_names)} features")
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Features file not found: {features_path}"
            )
        except Exception as e:
            logger.error(f"Failed to load features: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load features: {str(e)}"
            )
        
        # Prepare data
        try:
            df = pd.DataFrame([data.row])
            X, df_aug = prepare_live_data(df, "data/ml/metadata.json")
            logger.info(f"Data prepared: {X.shape}")
        except Exception as e:
            logger.error(f"Failed to prepare data: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to prepare data: {str(e)}"
            )
        
        # Predict
        try:
            if hasattr(model, "predict_proba"):
                prob = model.predict_proba(X)[0][1]
            else:
                # For models without predict_proba
                pred = model.predict(X)[0]
                prob = float(pred)
            
            logger.info(f"Prediction: {prob:.4f}")
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {str(e)}"
            )
        
        return {
            "fraud_probability": float(prob),
            "features": df_aug.iloc[0].to_dict() if not df_aug.empty else {}
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Scoring failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Scoring failed: {str(e)}"
        )
