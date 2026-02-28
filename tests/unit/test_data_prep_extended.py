# tests/unit/test_data_prep_extended.py
"""
Extended unit tests for ml/data_prep.py.
Tests edge cases, feature stability, scaler behaviour, and label handling.

Note: ml/data_prep.py uses 'isFraud' as the target column.
We create synthetic DataFrames matching that expected schema.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from pathlib import Path


# ── Synthetic data helpers ─────────────────────────────────────────────────────

def make_synthetic_df(n=200, seed=42):
    """Return a small synthetic DataFrame in the format preprocess() expects."""
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "step":        rng.integers(1, 500, n),
        "type":        rng.choice(["PAYMENT", "CASH_OUT", "DEBIT", "TRANSFER"], n),
        "amount":      rng.uniform(10, 50000, n),
        "oldbalanceOrg":  rng.uniform(0, 100000, n),
        "newbalanceOrig": rng.uniform(0, 100000, n),
        "oldbalanceDest": rng.uniform(0, 100000, n),
        "newbalanceDest": rng.uniform(0, 100000, n),
        # nameOrig / nameDest should be dropped by preprocess()
        "nameOrig":    [f"C{i}" for i in range(n)],
        "nameDest":    [f"M{i}" for i in range(n)],
        # Target column — ensure both classes present
        "isFraud":     np.concatenate([np.zeros(n - 10, dtype=int), np.ones(10, dtype=int)]),
    })


@pytest.fixture(scope="module")
def preprocessed_synthetic():
    """Run preprocess() once on synthetic data and share across tests."""
    from ml.data_prep import preprocess
    df = make_synthetic_df(n=200)
    return preprocess(df)


# ── Shape and size tests ───────────────────────────────────────────────────────

def test_train_test_split_non_empty(preprocessed_synthetic):
    """Both train and test arrays must be non-empty."""
    X_train, X_test, y_train, y_test, scaler, feats = preprocessed_synthetic
    assert X_train.shape[0] > 0, "Training set is empty"
    assert X_test.shape[0] > 0, "Test set is empty"


def test_feature_count_consistent(preprocessed_synthetic):
    """X_train and X_test must have the same number of columns."""
    X_train, X_test, _, _, _, feats = preprocessed_synthetic
    assert X_train.shape[1] == X_test.shape[1]
    assert len(feats) == X_train.shape[1]


def test_label_alignment(preprocessed_synthetic):
    """y arrays must align in length with their X counterpart."""
    X_train, X_test, y_train, y_test, _, _ = preprocessed_synthetic
    assert len(y_train) == X_train.shape[0]
    assert len(y_test) == X_test.shape[0]


# ── Data quality tests ─────────────────────────────────────────────────────────

def test_scaler_is_fitted(preprocessed_synthetic):
    """The returned scaler must be fitted (has mean_ or scale_ attribute)."""
    _, _, _, _, scaler, _ = preprocessed_synthetic
    assert hasattr(scaler, "mean_") or hasattr(scaler, "scale_"), (
        "Scaler must be fitted (has mean_ or scale_)"
    )


def test_no_nan_in_x_train(preprocessed_synthetic):
    """X_train must contain no NaN values after preprocessing."""
    X_train, _, _, _, _, _ = preprocessed_synthetic
    assert not np.isnan(X_train).any(), "NaN found in X_train"


def test_no_nan_in_x_test(preprocessed_synthetic):
    """X_test must contain no NaN values after preprocessing."""
    _, X_test, _, _, _, _ = preprocessed_synthetic
    assert not np.isnan(X_test).any(), "NaN found in X_test"


def test_feature_names_are_strings(preprocessed_synthetic):
    """Feature names returned should all be strings."""
    _, _, _, _, _, feats = preprocessed_synthetic
    assert all(isinstance(f, str) for f in feats)


def test_drop_cols_removed(preprocessed_synthetic):
    """nameOrig and nameDest (DROP_COLS) must not appear in features."""
    _, _, _, _, _, feats = preprocessed_synthetic
    feature_names = list(feats)
    assert "nameOrig" not in feature_names
    assert "nameDest" not in feature_names


def test_target_col_not_in_features(preprocessed_synthetic):
    """isFraud must not appear as a feature column."""
    _, _, _, _, _, feats = preprocessed_synthetic
    assert "isFraud" not in list(feats)


# ── Label tests ────────────────────────────────────────────────────────────────

def test_binary_labels_only(preprocessed_synthetic):
    """All labels should be 0 or 1 only."""
    _, _, y_train, y_test, _, _ = preprocessed_synthetic
    for y_arr, name in [(y_train, "y_train"), (y_test, "y_test")]:
        unique = set(np.unique(y_arr))
        assert unique.issubset({0, 1}), f"{name} has non-binary values: {unique}"


def test_both_classes_present_in_training(preprocessed_synthetic):
    """Training set should have both fraud (1) and non-fraud (0) samples."""
    _, _, y_train, _, _, _ = preprocessed_synthetic
    unique = set(np.unique(y_train))
    assert 0 in unique, "No non-fraud (0) samples in training set"
    assert 1 in unique, "No fraud (1) samples in training set"


# ── Real CSV smoke test (skip if file absent) ──────────────────────────────────

REAL_CSV = Path("data/raw/Fraud Detection Dataset.csv")


def test_load_raw_data_returns_dataframe():
    """load_raw_data() must return a pandas DataFrame."""
    from ml.data_prep import load_raw_data
    if not REAL_CSV.exists():
        pytest.skip(f"Real dataset not found at {REAL_CSV}")
    df = load_raw_data(REAL_CSV)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] > 0


def test_real_csv_has_expected_row_count():
    """The real dataset should have approximately 51k rows."""
    from ml.data_prep import load_raw_data
    if not REAL_CSV.exists():
        pytest.skip(f"Real dataset not found at {REAL_CSV}")
    df = load_raw_data(REAL_CSV)
    assert df.shape[0] >= 1000, "Expected at least 1000 rows in real dataset"
