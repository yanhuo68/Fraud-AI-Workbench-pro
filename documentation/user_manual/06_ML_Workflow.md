# 🔄 ML Workflow — User Manual

**Page:** ML Workflow (`pages/6_🔄_ML_Workflow.py (wrapper for src/views/ml_workflow/)`)  
**Access Level:** Authenticated Users (data_scientist / admin)

---

## Overview

The **ML Workflow** page provides a full machine-learning pipeline for training, evaluating, and deploying fraud detection models. It supports XGBoost and RandomForest classifiers with hyperparameter search, SHAP explainability, dataset versioning, model versioning, and one-click API deployment.

---

## Tab Structure

```
Tab 1: 📂 Dataset   →  Tab 2: 🔧 Train   →  Tab 3: 📊 Evaluate   →  Tab 4: 🚀 Deploy
```

---

## Tab 1 — 📂 Dataset Preparation

### Selecting Training Data
1. Choose a **SQL table** from the dropdown — this becomes the training dataset.
2. Optionally select a **label column** (the fraud indicator, e.g. `is_fraud`, `label`).
3. Select **feature columns** from the multi-select list (or use "Select All").
4. Click **Preview** to see a sample of the selected data.

### Dataset Versioning
- Each trained model tracks which table and columns were used.
- Use the **Dataset Version** dropdown to select or name a saved dataset configuration.
- Click **💾 Save Dataset Config** to persist the selection for reproducibility.

### Train / Validation / Test Split
Use the sliders to configure the data split ratios:
- **Train %** — default 70%
- **Validation %** — default 15%
- **Test %** — default 15%

---

## Tab 2 — 🔧 Train Model

### Algorithm Selection
Choose a classifier:
- **XGBoost** — gradient boosting, best for tabular fraud data
- **RandomForest** — ensemble of decision trees, fast and interpretable

### Hyperparameter Configuration

| Parameter | XGBoost | RandomForest |
|---|---|---|
| n_estimators | ✅ | ✅ |
| max_depth | ✅ | ✅ |
| learning_rate | ✅ | — |
| subsample | ✅ | — |
| min_samples_split | — | ✅ |

### Training
1. Click **▶ Train Model**.
2. A progress bar shows training epochs/iterations.
3. On completion, accuracy, precision, recall, and F1 score are displayed.

### Model Versioning
- Each trained model is automatically saved with a version tag (e.g. `xgboost_v3`).
- Use the **Model Registry** dropdown to compare or reload previous versions.

---

## Tab 3 — 📊 Evaluate

### Metrics Dashboard
After training, the evaluation panel shows:

| Metric | Description |
|---|---|
| Accuracy | Fraction of correct predictions |
| Precision | True positive rate among predicted positives |
| Recall | True positive rate among actual positives |
| F1 Score | Harmonic mean of precision and recall |
| ROC-AUC | Area under the ROC curve |

### Confusion Matrix
Heatmap showing true positives, false positives, true negatives, and false negatives.

### SHAP Explainability
Click **🔍 Generate SHAP Explanation** to produce:
- **Feature importance bar chart** — ranked contribution of each input feature
- **SHAP beeswarm plot** — shows direction and magnitude of each feature's impact per prediction
- **Individual prediction waterfall** — explain a single prediction

### Cross-Model Comparison
If multiple model versions exist, the evaluation panel shows a side-by-side comparison table.

---

## Tab 4 — 🚀 Deploy

### Generate Scoring API
Click **🚀 Deploy as API** to register the selected model version with the backend.  
The model becomes callable via `POST /ml/score` (see API Integration Hub).

### Test the Endpoint
An inline form lets you enter feature values and call the scoring endpoint directly from this page to verify the deployment.

---

## Tips

- Always check SHAP explanations to understand *why* the model flags certain transactions.
- Use the **Validation Loss** chart to detect overfitting — if validation loss rises while training loss falls, reduce `n_estimators` or increase regularization.
- The **Model Registry** stores all versions — you can roll back to a previous model at any time.
- For highly imbalanced datasets (common in fraud), check Recall and F1 — not just Accuracy.
