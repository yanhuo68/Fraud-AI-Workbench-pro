# 07. ML Workflow (Auto-Training)

The **ML Studio** is where raw transaction data is transformed into predictive models. Sentinel provides a full pipeline from feature engineering to production deployment.

## 🧪 1. Data Preparation

1. **Dataset Selection**: Choose a processed table or uploaded CSV to serve as the training source.
2. **Feature Selection**: Use the **Auto-Feature** tool to identify and engineer relevant signals (e.g., Transaction Amount, Time Frequency, Account Age).
3. **Data Splitting**: The system automatically splits data into Training, Validation, and Test sets (typically 80/10/10).

## 🤖 2. Auto-Training Pipeline

- **Algorithm Support**: Sentinel supports leading fraud detection algorithms including **Random Forest**, **XGBoost**, and **Logistic Regression**.
- **Hyperparameter Optimization**: Click **Start Auto-Train** to let the system automatically search for the best model settings to minimize false positives.
- **Evaluation Metrics**: Models are ranked by their **F1 Score** and **Precision-Recall AUC**, critical metrics in the imbalanced world of fraud data.

## 🚀 3. Model Deployment

Once a model meets your quality standard, you can:
- **Register Version**: Tag the model for production use.
- **Deploy to Live API**: 1-click generation of a REST endpoint for real-time fraud scoring.
- **SHAP Interpretation**: View AI-generated explanations for WHY the model flagged a specific transaction.

> [!TIP]
> Use the **Training History** tab to compare performance across different datasets or model versions.
