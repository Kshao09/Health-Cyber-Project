
import sqlite3
import os
from datetime import datetime

DB_FILE = "app.db"

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_FILE):
        db = get_db()
        cursor = db.cursor()
        cursor.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        );

        CREATE TABLE records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            original_filename TEXT,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            shared_with_id INTEGER NOT NULL,
            record_id INTEGER NOT NULL,
            FOREIGN KEY(owner_id) REFERENCES users(id),
            FOREIGN KEY(shared_with_id) REFERENCES users(id),
            FOREIGN KEY(record_id) REFERENCES records(id),
            UNIQUE(owner_id, shared_with_id, record_id)
        );

        CREATE TABLE access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            target TEXT,
            timestamp TEXT
        );
        """)
        db.commit()
        db.close()

def log_action(user_id, action, target=None):
    db = get_db()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # local time
    db.execute(
        "INSERT INTO access_logs (user_id, action, target, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, action, target, timestamp)
    )
    db.commit()
    db.close()


