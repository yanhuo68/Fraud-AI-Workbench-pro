import sqlite3
from config.settings import settings
from pathlib import Path

db_path = settings.db_path
print(f"Checking DB at: {db_path}")

try:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"Tables found: {tables}")
        
        for t in tables:
            print(f"\n--- Checking Table: {t} ---")
            cursor.execute(f"PRAGMA foreign_key_list('{t}')")
            fks = cursor.fetchall()
            print(f"Raw PRAGMA foreign_key_list output for '{t}':")
            if not fks:
                print("  (No Foreign Keys)")
            for row in fks:
                # Print row with indices to debug
                print(f"  Row: {row}")
                print(f"    Index 2 (Target Table): {row[2]}")
                print(f"    Index 3 (From Col): {row[3]}")
                print(f"    Index 4 (To Col): {row[4]}")
except Exception as e:
    print(f"Error: {e}")
