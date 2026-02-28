# ml/live_preprocessing.py

import pandas as pd
import json
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

from agents.fraud_risk_agent import add_fraud_risk_score
from agents.anomaly_agent import detect_anomalies_iqr


def prepare_live_data(df: pd.DataFrame, metadata_path="data/ml/metadata.json", features_path="data/ml/features.json"):
    """
    Apply same preprocessing steps used during training dataset creation.
    Strictly aligns columns to match 'features.json' (SimpleImputer input).
    """

    # Load metadata
    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    # Load expected features
    with open(features_path, "r") as f:
        expected_features = json.load(f)

    numeric_cols = metadata["numeric_columns"]
    categorical_cols = metadata["categorical_columns"]

    # ---------------------------------------------------------------------
    # 1. Add risk score
    # ---------------------------------------------------------------------
    df = add_fraud_risk_score(df)

    # ---------------------------------------------------------------------
    # 2. Add anomaly flag
    # ---------------------------------------------------------------------
    anomalies, thresholds = detect_anomalies_iqr(df)
    df["anomaly_flag"] = False
    if anomalies is not None and len(anomalies):
        df.loc[anomalies.index, "anomaly_flag"] = True

    # ---------------------------------------------------------------------
    # 3. Prepare Feature DataFrame
    # ---------------------------------------------------------------------
    # Ensure all required raw columns exist (fill 0/NaN if missing in live data)
    for col in numeric_cols + categorical_cols:
        if col not in df.columns:
            if col in numeric_cols:
                df[col] = 0
            else:
                df[col] = "unknown"

    # Convert anomaly_flag to string if it was categorical in training (indicated by anomaly_flag_True)
    # Checking features.json, we see "anomaly_flag_False", "anomaly_flag_True".
    # This implies it was treated as categorical/dummies.
    
    subset = df[numeric_cols + categorical_cols].copy()
    subset["anomaly_flag"] = df["anomaly_flag"]
    
    # ---------------------------------------------------------------------
    # 4. One-Hot Encode & Align
    # ---------------------------------------------------------------------
    # Use pandas get_dummies which is what Training Builder likely used (or equivalent OHE)
    # If training used OHE from sklearn, names might be different. 
    # But features.json names look like "Col_Value" (Pandas style) rather than "x0_Value".
    
    df_encoded = pd.get_dummies(subset)
    
    # ALIGNMENT: Reindex forces the columns to match expected_features
    # - Adds missing columns (fill_value=0)
    # - Drops extra columns (not in expected)
    # - Sorts to match order
    df_aligned = df_encoded.reindex(columns=expected_features, fill_value=0)
    
    # Return as numpy array for pipeline
    return df_aligned.values, df
