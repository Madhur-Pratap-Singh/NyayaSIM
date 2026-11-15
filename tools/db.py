"""
NyayaSim Relational SQLite Audit Logging System
Tracks every simulation run, individual agent prompt & response,
and procedural audit events for examiner inspection and reproducibility.
"""

import os
import sqlite3
import json
import time
from typing import Optional, List, Dict, Any

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
DB_PATH = os.path.join(DB_DIR, "nyayasim_audit.db")


def get_db_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes audit database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        state TEXT NOT NULL,
        is_early_stop INTEGER DEFAULT 0,
        escalation_decision TEXT,
        created_at REAL NOT NULL,
        completed_at REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_steps (
        step_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        agent_name TEXT NOT NULL,
        prompt_text TEXT,
        response_json TEXT,
        status TEXT DEFAULT 'OK',
        created_at REAL NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs (run_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        timestamp REAL NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs (run_id)
    )
    """)

    conn.commit()
    conn.close()


def log_run(run_id: str, case_id: str, state: str, is_early_stop: bool = False, escalation_decision: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = time.time()
    cursor.execute("""
    INSERT OR REPLACE INTO runs (run_id, case_id, state, is_early_stop, escalation_decision, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (run_id, case_id, state, 1 if is_early_stop else 0, escalation_decision, now))
    conn.commit()
    conn.close()


def log_step(run_id: str, agent_name: str, prompt_text: str, response_data: Any, status: str = "OK"):
    conn = get_db_connection()
    cursor = conn.cursor()
    resp_str = json.dumps(response_data, default=str) if not isinstance(response_data, str) else response_data
    cursor.execute("""
    INSERT INTO agent_steps (run_id, agent_name, prompt_text, response_json, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (run_id, agent_name, prompt_text, resp_str, status, time.time()))
    conn.commit()
    conn.close()


def log_event(run_id: str, event_type: str, payload: Any):
    conn = get_db_connection()
    cursor = conn.cursor()
    payload_str = json.dumps(payload, default=str) if not isinstance(payload, str) else payload
    cursor.execute("""
    INSERT INTO audit_log (run_id, event_type, payload_json, timestamp)
    VALUES (?, ?, ?, ?)
    """, (run_id, event_type, payload_str, time.time()))
    conn.commit()
    conn.close()


def get_run_steps(run_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_steps WHERE run_id = ? ORDER BY step_id ASC", (run_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


# Auto-initialize database on import
init_db()
