# ml/models.py
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import numpy as np
import logging

logger = logging.getLogger(__name__)

def train_isolation_forest(X_train, contamination: float = 0.02):
    logger.info("Training IsolationForest...")
    iso = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    iso.fit(X_train)
    return iso

def predict_iforest_scores(model: IsolationForest, X):
    # Higher score -> more normal; convert to anomaly score
    scores = -model.score_samples(X)
    return scores

def train_random_forest(X_train, y_train):
    logger.info("Training RandomForestClassifier...")
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced_subsample",
    )
    rf.fit(X_train, y_train)
    return rf

def evaluate_classifier(model, X_test, y_test):
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)
    report = classification_report(y_test, y_pred, output_dict=True)
    auc = roc_auc_score(y_test, y_prob)
    logger.info(f"Classifier AUC={auc:.4f}")
    return report, auc, y_prob, y_pred
