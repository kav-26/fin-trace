"""
Fin-Trace: SQLite persistence for investigation history.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "fin_trace.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the investigations table if it doesn't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            company TEXT,
            confidence INTEGER,
            conclusion TEXT,
            full_result TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_investigation(question: str, company: str, result: dict) -> int:
    """Save a completed investigation. Returns the new row's ID."""
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO investigations (question, company, confidence, conclusion, full_result, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            question,
            company,
            result["report"].get("confidence"),
            result["report"].get("conclusion"),
            json.dumps(result),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def list_investigations(limit: int = 50) -> list[dict]:
    """Return recent investigations, most recent first, without the full result payload."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, question, company, confidence, conclusion, created_at
        FROM investigations
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_investigation(investigation_id: int) -> dict | None:
    """Return the full stored result for one investigation by ID."""
    conn = get_connection()
    row = conn.execute(
        "SELECT full_result FROM investigations WHERE id = ?",
        (investigation_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return json.loads(row["full_result"])