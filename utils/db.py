import sqlite3
from pathlib import Path
from typing import Callable, Any, Iterable


DB_PATH = Path(__file__).parent.parent / "cogniscan.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('clinician', 'patient')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            prediction TEXT,
            confidence REAL,
            probabilities TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    try:
        cur.execute("ALTER TABLE users ADD COLUMN patient_id TEXT")
    except sqlite3.OperationalError:
        pass
    for col in ["probabilities", "patient_id", "patient_summary", "doctor_note"]:
        try:
            cur.execute(f"ALTER TABLE scans ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass
    # Backfill patient_id for existing patient users
    cur.execute("UPDATE users SET patient_id = 'P-' || id WHERE role = 'patient' AND (patient_id IS NULL OR patient_id = '')")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS follow_up_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_user_id INTEGER NOT NULL,
            preferred_date TEXT,
            preferred_time TEXT,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_user_id) REFERENCES users (id)
        )
        """
    )
    conn.commit()
    conn.close()


def query_one(sql: str, params: Iterable[Any] | None = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, tuple(params or []))
    row = cur.fetchone()
    conn.close()
    return row


def query_many(sql: str, params: Iterable[Any] | None = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, tuple(params or []))
    rows = cur.fetchall()
    conn.close()
    return rows


def execute(sql: str, params: Iterable[Any] | None = None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, tuple(params or []))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id
