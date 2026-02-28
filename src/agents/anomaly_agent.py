import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
import numpy as np
from agents.llm_router import init_llm


def detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    """
    Detects anomalies in a DataFrame using Isolation Forest.
    
    Args:
        df (pd.DataFrame): Input dataframe.
        contamination (float): The amount of contamination of the data set, 
                               i.e. the proportion of outliers in the data set.

    Returns:
        pd.DataFrame: DataFrame with added columns:
                      - 'is_anomaly': -1 for anomaly, 1 for normal
                      - 'anomaly_score': lower is more anomalous
                      - 'anomaly_label': 'Anomaly' or 'Normal'
    """
    if df is None or df.empty:
        return df

    # 1. Select numeric columns for training
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        # Cannot run numeric anomaly detection without numeric data
        return df

    # 2. Handle missing values (Simple Imputation)
    # IsolationForest requires no NaN
    imputer = SimpleImputer(strategy='mean')
    X = imputer.fit_transform(numeric_df)

    # 3. Train Isolation Forest
    # n_jobs=-1 uses all processors
    iso_forest = IsolationForest(contamination=contamination, random_state=42, n_jobs=-1)
    
    # Predict (-1 = anomaly, 1 = normal)
    preds = iso_forest.fit_predict(X)
    
    # Decision function (average anomaly score) - lower is more abnormal
    scores = iso_forest.decision_function(X)

    # 4. Attach results to a copy of original DF
    result_df = df.copy()
    result_df['is_anomaly_code'] = preds
    result_df['anomaly_score'] = scores
    result_df['anomaly_label'] = result_df['is_anomaly_code'].apply(lambda x: 'Anomaly' if x == -1 else 'Normal')
    
    return result_df

def detect_anomalies_iqr(df: pd.DataFrame, factor: float = 1.5) -> pd.DataFrame:
    """
    Detects anomalies using Interquartile Range (IQR) method.
    Adds 'is_outlier' column.
    """
    if df is None: return df
    
    outlier_indices = set()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - (factor * IQR)
        upper_bound = Q3 + (factor * IQR)
        
        # Get indices of outliers
        col_outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index
        outlier_indices.update(col_outliers)
        
    # Mark in dataframe
    result = df.copy()
    result['is_outlier'] = 0
    result.loc[list(outlier_indices), 'is_outlier'] = 1
    
    
    return result[result['is_outlier'] == 1], {"factor": factor, "method": "IQR"}

def anomaly_narrative(question: str, df: pd.DataFrame, anomalies: pd.DataFrame, thresholds: dict, schema_text: str, llm_id: str = "gpt-4o-mini") -> str:
    """
    Generates a narrative explanation of the detected anomalies using the LLM.
    """
    if anomalies is None or anomalies.empty:
        return "No anomalies detected to analyze."

    llm = init_llm(llm_id)
    
    # Summarize anomalies
    num_anomalies = len(anomalies)
    total_rows = len(df)
    percent = (num_anomalies / total_rows) * 100 if total_rows > 0 else 0
    
    sample_anomalies = anomalies.head(5).to_markdown(index=False)
    
    prompt = (
        f"You are a data analyst. I have detected {num_anomalies} anomalies ({percent:.1f}% of data) "
        "using outlier detection (IQR rule).\n\n"
        f"User Question: {question}\n\n"
        f"Schema context:\n{schema_text}\n\n"
        f"Sample Anomalous Rows:\n{sample_anomalies}\n\n"
        "Please provide a brief, professional summary of these anomalies. "
        "Are they likely data errors or significant outliers relevant to the user's question? "
        "Suggest what the user should investigate."
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Could not generate anomaly narrative: {e}"

