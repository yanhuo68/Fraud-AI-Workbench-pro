# ml/auto_trainer.py

"""
Auto-training pipeline for fraud detection.

- Loads processed train/validation/test CSVs
- Trains several baseline models
- Evaluates them
- Picks the best one
- Saves model + metrics
"""

from pathlib import Path
import json
import pickle

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def _load_split(path: str):
    df = pd.read_csv(path)
    if "label" not in df.columns:
        raise ValueError(f"'label' column not found in {path}")
    # Drop rows with missing labels
    if df["label"].isnull().any():
        df = df.dropna(subset=["label"])
    
    X = df.drop(columns=["label"]).values
    y = df["label"].values.astype(int) # Ensure integer labels
    return X, y


def _evaluate_model(model, X_val, y_val) -> dict:
    y_pred = model.predict(X_val)
    y_proba = None
    try:
        y_proba = model.predict_proba(X_val)[:, 1]
    except Exception:
        pass

    metrics = {
        "accuracy": float(accuracy_score(y_val, y_pred)),
        "precision": float(precision_score(y_val, y_pred, zero_division=0)),
        "recall": float(recall_score(y_val, y_pred, zero_division=0)),
        "f1": float(f1_score(y_val, y_pred, zero_division=0)),
    }

    if y_proba is not None and len(np.unique(y_val)) == 2:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_val, y_proba))
        except Exception:
            metrics["roc_auc"] = None
    else:
        metrics["roc_auc"] = None

    metrics["classification_report"] = classification_report(
        y_val, y_pred, zero_division=0
    )

    return metrics


def train_models(
    train_path="data/ml/train.csv",
    val_path="data/ml/validation.csv",
    test_path="data/ml/test.csv",
    features_path="data/ml/features.json",
    output_dir="models",
    optimize_hyperparameters=False,
    custom_config=None,
):
    """
    Train baseline models on train split, evaluate on validation, and pick best.

    Returns dict:
    {
      "best_model_name": str,
      "metrics": {model_name: metrics_dict},
      "saved_model_path": str,
      "features_path": str
    }
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    X_train, y_train = _load_split(train_path)
    X_val, y_val = _load_split(val_path)
    X_test, y_test = _load_split(test_path)

    # 2. Define models
    # 2. Define pipelines with Custom Config
    # Default configs
    rf_params = {"n_estimators": 100, "max_depth": 10, "random_state": 42}
    gb_params = {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 5, "random_state": 42}
    lr_params = {"max_iter": 1000, "random_state": 42}

    # Override defaults if custom_config provided
    if custom_config:
        rf_params.update(custom_config.get("random_forest", {}))
        gb_params.update(custom_config.get("gradient_boosting", {}))
        lr_params.update(custom_config.get("logistic_regression", {}))

    models = {
        "random_forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(**rf_params))
        ]),
        "gradient_boosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", GradientBoostingClassifier(**gb_params))
        ]),
        "logistic_regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(**lr_params))
        ])
    }

    all_metrics = {}
    best_model_name = None
    best_score = -1.0
    best_model = None
    
    # Param Grids
    param_grids = {
        "logistic_regression": {
            "clf__C": [0.01, 0.1, 1.0, 10.0],
            "clf__penalty": ["l2"],
        },
        "random_forest": {
            "clf__n_estimators": [50, 100, 200],
            "clf__max_depth": [None, 10, 20],
            "clf__min_samples_split": [2, 5, 10],
        },
        "gradient_boosting": {
            "clf__n_estimators": [50, 100, 200],
            "clf__learning_rate": [0.01, 0.1, 0.2],
            "clf__max_depth": [3, 5, 7],
        }
    }

    # 3. Train + validate
    for name, model in models.items():
        if optimize_hyperparameters and name in param_grids:
            print(f"Optimizing {name}...")
            search = RandomizedSearchCV(
                model, 
                param_grids[name], 
                n_iter=5, # Keep it fast for demo
                cv=3, 
                scoring="f1", 
                n_jobs=-1, 
                random_state=42
            )
            search.fit(X_train, y_train)
            model = search.best_estimator_
        else:
            model.fit(X_train, y_train)
            
        metrics = _evaluate_model(model, X_val, y_val)
        all_metrics[name] = metrics

        # use F1 as primary criterion, fall back to accuracy
        score = metrics.get("f1", 0.0)
        if score > best_score:
            best_score = score
            best_model_name = name
            best_model = model

    # 4. Evaluate best model on test set (for info)
    test_metrics = {}
    if best_model is not None:
        test_metrics = _evaluate_model(best_model, X_test, y_test)
        all_metrics[f"{best_model_name}_test"] = test_metrics

    # 5. Save best model
    saved_model_path = str(output_dir / f"best_model_{best_model_name}.pkl")
    with open(saved_model_path, "wb") as f:
        pickle.dump(best_model, f)

    # 6. Save metrics
    metrics_path = str(output_dir / "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)

    return {
        "best_model_name": best_model_name,
        "metrics": all_metrics,
        "saved_model_path": saved_model_path,
        "metrics_path": metrics_path,
        "features_path": features_path,
    }
