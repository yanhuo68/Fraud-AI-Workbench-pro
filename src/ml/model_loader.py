# ml/model_loader.py

import pickle
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

def load_model(model_path="models/best_model_random_forest.pkl"):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model


def load_features(features_path="data/ml/features.json"):
    with open(features_path, "r") as f:
        return json.load(f)


def build_preprocessor(numeric_cols, categorical_cols):
    """
    Create a ColumnTransformer using same logic as training.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
        ],
        remainder="drop",
    )
    return preprocessor
