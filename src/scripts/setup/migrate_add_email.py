import sqlite3
import sys
import os

# Add parent directory to path to import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import settings

def migrate_add_email():
    """
    Adds an 'email' column to the 'app_users' table if it doesn't exist.
    """
    db_path = settings.db_path
    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(app_users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "email" not in columns:
            print("Adding 'email' column to 'app_users' table...")
            # SQLite doesn't support adding UNIQUE columns easily without default values or table recreation.
            # We add it as a standard column first. Unique constraint will be enforced via index or app logic.
            cursor.execute("ALTER TABLE app_users ADD COLUMN email TEXT")
            
            # create unique index
            print("Creating unique index on email...")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON app_users(email)")
            
            conn.commit()
            print("Migration successful: 'email' column added with unique index.")
        else:
            print("Migration skipped: 'email' column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_add_email()
