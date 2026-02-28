import sqlite3
import os
from pathlib import Path
from utils.auth_utils import get_password_hash

from config.settings import settings

def init_user_db(db_path: str = None):
    if db_path is None:
        db_path = settings.db_path
    
    # Ensure directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating 'app_users' table...")
    print("Creating 'app_users' table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'guest',
        email TEXT, -- Added for password reset
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 1.5 Check for email column migration (for existing DBs)
    try:
        cursor.execute("PRAGMA table_info(app_users)")
        columns = [info[1] for info in cursor.fetchall()]
        if "email" not in columns:
            print("Migrating: Adding 'email' column to app_users...")
            cursor.execute("ALTER TABLE app_users ADD COLUMN email TEXT")
            conn.commit()
    except Exception as e:
        print(f"Migration check failed: {e}")
        
    # Create unique index on email
    try:
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON app_users(email)")
    except Exception as e:
        print(f"Index creation failed: {e}")
    
    print("Creating 'app_roles' table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        permissions TEXT NOT NULL, -- JSON array of page names
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Initial seed for roles
    roles_to_seed = [
        ("guest", '["1_📁_Data_Hub", "2_🧠_SQL_RAG_Assistant", "3_🕸️_Graph_RAG_Assistant", "4_🎥_Multimodal_RAG_Assistant", "5_📈_Trends_and_Insights"]'),
        ("data_scientist", '["1_📁_Data_Hub", "2_🧠_SQL_RAG_Assistant", "3_🕸️_Graph_RAG_Assistant", "4_🎥_Multimodal_RAG_Assistant", "5_📈_Trends_and_Insights", "6_🔄_ML_Workflow", "9_🧠_LLM_Fine_Tuning"]'),
        ("admin", '["1_📁_Data_Hub", "2_🧠_SQL_RAG_Assistant", "3_🕸️_Graph_RAG_Assistant", "4_🎥_Multimodal_RAG_Assistant", "5_📈_Trends_and_Insights", "6_🔄_ML_Workflow", "9_🧠_LLM_Fine_Tuning", "10_🔌_API_Interaction", "11_🛡️_Admin_Console"]')
    ]
    
    for r_name, r_perms in roles_to_seed:
        cursor.execute("SELECT id FROM app_roles WHERE name = ?", (r_name,))
        if not cursor.fetchone():
            print(f"Seeding role: {r_name}...")
            cursor.execute("INSERT INTO app_roles (name, permissions) VALUES (?, ?)", (r_name, r_perms))
    
    print("Creating 'api_keys' table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        key TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create default admin if not exists
    cursor.execute("SELECT id FROM app_users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        print("Creating default admin user...")
        hashed_pw = get_password_hash("admin123")
        cursor.execute(
            "INSERT INTO app_users (username, hashed_password, role) VALUES (?, ?, ?)",
            ("admin", hashed_pw, "admin")
        )
    
    # Create default guest if not exists
    cursor.execute("SELECT id FROM app_users WHERE username = ?", ("guest",))
    if not cursor.fetchone():
        print("Creating default guest user...")
        hashed_pw = get_password_hash("guest123")
        cursor.execute(
            "INSERT INTO app_users (username, hashed_password, role) VALUES (?, ?, ?)",
            ("guest", hashed_pw, "guest")
        )
        
    conn.commit()
    conn.close()
    print("User database initialization complete.")

if __name__ == "__main__":
    init_user_db()
