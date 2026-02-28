# tests/test_data_prep.py
from pathlib import Path
from ml.data_prep import load_raw_data, preprocess

def test_preprocess_shapes():
    csv_path = Path("data/raw/Fraud Detection Dataset.csv")
    df = load_raw_data(csv_path)
    X_train, X_test, y_train, y_test, scaler, feats = preprocess(df)

    assert X_train.shape[0] > 0
    assert X_test.shape[0] > 0
    assert X_train.shape[1] == X_test.shape[1]
    assert len(y_train) == X_train.shape[0]
    assert len(feats) == X_train.shape[1]
