# ml/training_dataset_builder.py
from __future__ import annotations

import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split

from agents.anomaly_agent import detect_anomalies_iqr
from agents.fraud_risk_agent import add_fraud_risk_score


def build_training_dataset(
    df: pd.DataFrame,
    output_dir="data/ml",
    label_column: str | None = None,
):
    """
    Creates ML-ready dataset:
    - engineered features
    - anomaly score
    - risk score
    - encoded categoricals
    - train/val/test split
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if df is None or df.empty:
        raise ValueError("DataFrame is empty — cannot build ML dataset.")

    df = df.copy()

    # --------------------------------------------------------
    # 1. Add Fraud Risk Score (already defined in your pipeline)
    # --------------------------------------------------------
    df = add_fraud_risk_score(df)

    # --------------------------------------------------------
    # 2. Add Anomaly Score
    # --------------------------------------------------------
    anomalies, threshold_info = detect_anomalies_iqr(df)
    df["anomaly_flag"] = False
    if anomalies is not None and len(anomalies):
        df.loc[anomalies.index, "anomaly_flag"] = True

    # --------------------------------------------------------
    # 3. Create Label (if not exists → auto pseudo-label)
    # --------------------------------------------------------
    if label_column and label_column in df.columns:
        y = df[label_column].astype(int)
    else:
        # pseudo-label: combine anomaly_flag and high risk
        df["pseudo_label"] = (
            (df["fraud_risk_score"] > 0.7)
            | (df["anomaly_flag"])
        ).astype(int)
        y = df["pseudo_label"]

    # --------------------------------------------------------
    # 4. Identify numeric + categorical columns
    # --------------------------------------------------------
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

    # Remove label from features
    if label_column in numeric_cols:
        numeric_cols.remove(label_column)
    if "pseudo_label" in numeric_cols:
        numeric_cols.remove("pseudo_label")

    # --------------------------------------------------------
    # 5. Feature Engineering (Scaler + OneHotEncoder)
    # --------------------------------------------------------
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
        ],
        remainder="drop",
    )

    X = preprocessor.fit_transform(df)

    # Feature names
    num_features = numeric_cols
    cat_features = list(preprocessor.named_transformers_["cat"].get_feature_names_out(categorical_cols))
    feature_names = num_features + cat_features

    # --------------------------------------------------------
    # 6. Train / Val / Test Split
    # --------------------------------------------------------
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42)

    # --------------------------------------------------------
    # 7. Save datasets
    # --------------------------------------------------------
    pd.DataFrame(X_train, columns=feature_names).assign(label=y_train).to_csv(f"{output_dir}/train.csv", index=False)
    pd.DataFrame(X_val, columns=feature_names).assign(label=y_val).to_csv(f"{output_dir}/validation.csv", index=False)
    pd.DataFrame(X_test, columns=feature_names).assign(label=y_test).to_csv(f"{output_dir}/test.csv", index=False)

    # save feature names
    with open(f"{output_dir}/features.json", "w") as f:
        json.dump(feature_names, f, indent=2)

    # Save metadata (thresholds, risk scoring rules, etc.)
    metadata = {
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "thresholds": threshold_info,
        "feature_names": feature_names,
        "label_column": label_column or "pseudo_label",
        "feature_stats": df[numeric_cols].agg(['min', 'max', 'mean', 'std']).to_dict()
    }
    with open(f"{output_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return {
        "train_path": f"{output_dir}/train.csv",
        "val_path": f"{output_dir}/validation.csv",
        "test_path": f"{output_dir}/test.csv",
        "features_path": f"{output_dir}/features.json",
        "metadata_path": f"{output_dir}/metadata.json",
    }
