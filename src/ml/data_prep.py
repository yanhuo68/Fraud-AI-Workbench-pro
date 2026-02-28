# ml/data_prep.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

CATEGORICAL_COLS = ["type", "Transaction_Type", "Device_Used", "Location", "Payment_Method"]
DROP_COLS = ["nameOrig", "nameDest", "Transaction_ID", "User_ID"]
# Support both PaySim ('isFraud') and the project's own dataset ('Fraudulent')
_LABEL_COLS = ["isFraud", "Fraudulent"]

def load_raw_data(csv_path: str | Path) -> pd.DataFrame:
    csv_path = Path(csv_path)
    logger.info(f"Loading raw data from {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns")
    return df

def preprocess(df: pd.DataFrame):
    """Encode, drop IDs, scale numerics, split X/y."""
    df = df.copy()

    # Encode categorical columns as integer codes
    for cat_col in CATEGORICAL_COLS:
        if cat_col in df.columns:
            df[cat_col] = df[cat_col].astype("category").cat.codes

    # Drop identifier columns
    for col in DROP_COLS:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Detect the label column (support multiple dataset schemas)
    label_col = None
    for candidate in _LABEL_COLS:
        if candidate in df.columns:
            label_col = candidate
            break
    if label_col is None:
        raise KeyError(
            f"No target column found. Expected one of {_LABEL_COLS}. "
            f"Available columns: {list(df.columns)}"
        )

    # Target
    y = df[label_col].astype(int)
    X = df.drop(columns=[label_col])

    numeric_cols = X.columns
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    return X_train, X_test, y_train, y_test, scaler, numeric_cols
