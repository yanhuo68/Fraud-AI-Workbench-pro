# rag_sql/pkfk_detector.py
from __future__ import annotations
import pandas as pd
from typing import Dict, List, Tuple
from typing import Dict, List, Tuple

# -------------------------
# PRIMARY KEY DETECTION
# -------------------------

def detect_primary_key(df: pd.DataFrame) -> str | None:
    """
    Returns the best candidate primary key column for a DataFrame.
    Heuristics:
    - Column name contains 'id'
    - Unique values
    - No nulls
    """

    candidates = []

    for col in df.columns:
        series = df[col]

        # cannot be a PK if nulls exist
        if series.isna().any():
            continue

        # cannot be PK if all values are identical
        if series.nunique() == 1:
            continue

        # uniqueness score
        uniqueness_ratio = series.nunique() / len(series)

        # name score
        name_score = 1 if "id" in col.lower() else 0

        score = uniqueness_ratio + name_score

        candidates.append((col, score))

    if not candidates:
        return None

    # pick highest score
    candidates.sort(key=lambda x: x[1], reverse=True)
    col, score = candidates[0]

    # sanity check: must be unique
    if df[col].nunique() == len(df[col]):
        return col

    return None


# -------------------------
# FOREIGN KEY DETECTION
# -------------------------

def detect_foreign_keys(
    tables: Dict[str, pd.DataFrame],
    primary_keys: Dict[str, str | None],
    min_overlap_ratio: float = 0.1,
) -> List[Tuple[str, str, str, str]]:
    """
    Detect foreign key relationships between multiple tables.

    Returns a list of tuples:
        (table_A, column_A, table_B, pk_B)
    meaning:
        table_A.column_A references table_B.pk_B
    """

    relationships = []

    for table_A, dfA in tables.items():
        for table_B, dfB in tables.items():
            if table_A == table_B:
                continue

            pk_B = primary_keys.get(table_B)
            if pk_B is None:
                continue

            pk_values = set(dfB[pk_B].dropna().unique())

            # try matching columns in table A against pk in table B
            for colA in dfA.columns:
                seriesA = dfA[colA].dropna()

                # skip impossible matches
                if seriesA.dtype != dfB[pk_B].dtype:
                    continue

                # compute overlap score
                overlap = seriesA.isin(pk_values).mean()

                if overlap >= min_overlap_ratio:
                    relationships.append((table_A, colA, table_B, pk_B))

    return relationships
