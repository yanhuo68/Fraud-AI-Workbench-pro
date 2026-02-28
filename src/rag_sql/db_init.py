# rag_sql/db_init.py
import sqlite3
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)

from config.settings import settings

DB_PATH = settings.db_path

def create_db_from_csv(csv_path: str | Path, db_path: str | Path = None):
    if db_path is None:
        db_path = DB_PATH
    csv_path = Path(csv_path)
    db_path = Path(db_path)

    logger.info(f"Creating SQLite DB at {db_path} from {csv_path}")
    df = pd.read_csv(csv_path)

    with sqlite3.connect(db_path) as conn:
        df.to_sql("transactions", conn, if_exists="replace", index=False)
    logger.info("SQLite DB created with table 'transactions'")

if __name__ == "__main__":
    create_db_from_csv("data/raw/Fraud Detection Dataset.csv")
