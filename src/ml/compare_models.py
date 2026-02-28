# ml/compare_models.py

import streamlit as st
import pandas as pd
import numpy as np

from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)
from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
from io import BytesIO

from agents.llm_router import init_llm
from ml.report_generator import generate_model_comparison_pdf


def compute_supervised_metrics(model, X_test, y_test):
    prob = model.predict_proba(X_test)[:, 1]
    pred = (prob >= 0.5).astype(int)

    return {
        "Precision": precision_score(y_test, pred, zero_division=0),
        "Recall": recall_score(y_test, pred, zero_division=0),
        "F1": f1_score(y_test, pred, zero_division=0),
        "AUC": roc_auc_score(y_test, prob),
        "Confusion Matrix": confusion_matrix(y_test, pred),
        "proba": prob,  # keep for ROC
    }


def compute_unsupervised_metrics(scores, y_true):
    k = max(1, int(0.01 * len(scores)))  # top 1% anomalies
    idx = np.argsort(scores)[::-1][:k]
    precision_at_k = float(np.mean(y_true.iloc[idx] == 1))

    return {
        "Precision@K": precision_at_k,
        "Top-K Count": k,
    }


def run_model_comparison():
    st.title("📊 Model Comparison Dashboard")

    if "uploaded_df" not in st.session_state:
        st.warning("Please upload dataset in the Data Hub tab first.")
        return

    df = st.session_state.uploaded_df.copy()

    if "isFraud" not in df.columns:
        st.error("Dataset must contain `isFraud`.")
        return

    # Basic preprocessing
    df = df.fillna(0)
    X = df.drop(columns=["isFraud"])
    y = df["isFraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Dataset summary for report
    dataset_summary = {
        "Rows": len(df),
        "Fraud Rate": f"{(y.mean() * 100):.3f}%",
        "Num Features": X.shape[1],
    }

    st.subheader("📌 Training Models...")

    results = {}

    # ---------- Supervised models ----------
    rf = RandomForestClassifier(n_estimators=200, random_state=42)
    rf.fit(X_train, y_train)
    results["Random Forest"] = compute_supervised_metrics(rf, X_test, y_test)

    gb = GradientBoostingClassifier(random_state=42)
    gb.fit(X_train, y_train)
    results["Gradient Boosting"] = compute_supervised_metrics(gb, X_test, y_test)

    lr = LogisticRegression(max_iter=2000)
    lr.fit(X_train, y_train)
    results["Logistic Regression"] = compute_supervised_metrics(lr, X_test, y_test)

    # ---------- Unsupervised models ----------
    if_model = IsolationForest(contamination=y.mean(), random_state=42)
    if_model.fit(X_train)
    if_scores = -if_model.decision_function(X_test)
    results["Isolation Forest"] = compute_unsupervised_metrics(if_scores, y_test)

    lof = LocalOutlierFactor(n_neighbors=30, novelty=True)
    lof.fit(X_train)
    lof_scores = -lof.score_samples(X_test)
    results["Local Outlier Factor"] = compute_unsupervised_metrics(lof_scores, y_test)

    oc = OneClassSVM(kernel="rbf", gamma="scale")
    oc.fit(X_train)
    oc_scores = -oc.score_samples(X_test)
    results["One-Class SVM"] = compute_unsupervised_metrics(oc_scores, y_test)

    # ---------- Display comparison ----------
    st.subheader("📊 Model Performance Comparison")
    # For display, drop the 'proba' arrays
    display_results = {}
    for model_name, metrics in results.items():
        display_results[model_name] = {
            k: v for k, v in metrics.items() if k not in ("proba",)
        }

    st.dataframe(pd.DataFrame(display_results).T)

    # ---------- ROC Curves ----------
    st.subheader("📈 ROC Curves (Supervised Models)")

    fig = plt.figure(figsize=(7, 4))
    for name, model in [("Random Forest", rf), ("Gradient Boosting", gb), ("Logistic Regression", lr)]:
        prob = results[name]["proba"]
        fpr, tpr, _ = roc_curve(y_test, prob)
        plt.plot(fpr, tpr, label=name)

    plt.plot([0, 1], [0, 1], "--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    st.pyplot(fig)

    # ---------- LLM Interpretation ----------
    st.subheader("🧠 LLM Interpretation of Results")

    llm = init_llm(st.session_state.get("selected_llm", "openai:gpt-4o-mini"))

    results_md = pd.DataFrame(display_results).T.to_markdown()

    summary_prompt = f"""
    You are a senior fraud analytics and ML expert.

    Below is a model comparison table for fraud detection:

    {results_md}

    Dataset summary:
    - Rows: {dataset_summary["Rows"]}
    - Fraud Rate: {dataset_summary["Fraud Rate"]}
    - Num Features: {dataset_summary["Num Features"]}

    Using the guidelines in the fraud knowledge-base (e.g., ml_evaluation_metrics, fraud_risk_rules, model_interpretation),
    provide a concise but rich report that explains:

    1. Which supervised model performs best and why.
    2. How the anomaly detection models (Isolation Forest, LOF, One-Class SVM) should be interpreted.
    3. Trade-offs between false positives and false negatives.
    4. A recommendation for which model(s) to use in production and how to combine them.

    Use clear headings and bullet points.
    """

    with st.spinner("Generating analysis with LLM..."):
        llm_response = llm.invoke(summary_prompt)

    llm_text = llm_response.content
    st.markdown(llm_text)

    # Store for PDF generation
    st.session_state["model_comparison_results"] = display_results
    st.session_state["model_comparison_dataset_summary"] = dataset_summary
    st.session_state["model_comparison_llm_text"] = llm_text
    st.session_state["model_comparison_roc_fig"] = fig

    # ---------- PDF Export ----------
    st.subheader("📄 Export Model Comparison Report")

    if st.button("📥 Generate PDF Report"):
        with st.spinner("Generating PDF report..."):
            # Create PDF in a temp buffer, then offer as download
            tmp_path = "data/reports/model_comparison_report.pdf"
            pdf_path = generate_model_comparison_pdf(
                results=display_results,
                roc_fig=fig,
                dataset_summary=dataset_summary,
                llm_text=llm_text,
                output_path=tmp_path,
            )
            # Read back into memory
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

        st.success("PDF report generated.")
        st.download_button(
            label="⬇️ Download Model Comparison Report (PDF)",
            data=pdf_bytes,
            file_name="model_comparison_report.pdf",
            mime="application/pdf",
        )
