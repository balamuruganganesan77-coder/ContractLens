"""
SQLite database storage and persistence layer for ContractLens
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "contractlens.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize all SQLite tables for application persistence."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Contracts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            status TEXT DEFAULT 'Analyzed',
            effective_date TEXT DEFAULT 'Not found in contract',
            expiration_date TEXT DEFAULT 'Not found in contract',
            obligation_count INTEGER DEFAULT 0,
            risk_count INTEGER DEFAULT 0,
            summary_json TEXT DEFAULT '{}'
        )
    """)

    # 2. Extracted Fields Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id TEXT NOT NULL,
            field_name TEXT NOT NULL,
            value TEXT NOT NULL,
            source_page INTEGER DEFAULT 1,
            source_clause TEXT DEFAULT '',
            confidence REAL DEFAULT 0.9,
            FOREIGN KEY (contract_id) REFERENCES contracts (id) ON DELETE CASCADE
        )
    """)

    # 3. Obligations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obligations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id TEXT NOT NULL,
            party_responsible TEXT NOT NULL,
            obligation_text TEXT NOT NULL,
            deadline TEXT DEFAULT 'Not specified',
            deadline_type TEXT DEFAULT 'Fixed Date',
            frequency TEXT DEFAULT 'One-time',
            source_page INTEGER DEFAULT 1,
            clause_text TEXT DEFAULT '',
            status TEXT DEFAULT 'Upcoming',
            FOREIGN KEY (contract_id) REFERENCES contracts (id) ON DELETE CASCADE
        )
    """)

    # 4. Risks Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id TEXT NOT NULL,
            risk_title TEXT NOT NULL,
            severity TEXT NOT NULL,
            reason TEXT NOT NULL,
            source_page INTEGER DEFAULT 1,
            clause_text TEXT DEFAULT '',
            action_recommended TEXT NOT NULL,
            FOREIGN KEY (contract_id) REFERENCES contracts (id) ON DELETE CASCADE
        )
    """)

    # 5. Timeline Events Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id TEXT NOT NULL,
            event_title TEXT NOT NULL,
            party TEXT DEFAULT 'General',
            date_str TEXT NOT NULL,
            event_type TEXT NOT NULL,
            source_page INTEGER DEFAULT 1,
            alert_level TEXT DEFAULT 'Upcoming',
            FOREIGN KEY (contract_id) REFERENCES contracts (id) ON DELETE CASCADE
        )
    """)

    # 6. Chat History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            citations_json TEXT DEFAULT '[]',
            timestamp TEXT NOT NULL
        )
    """)

    # 7. Version Comparisons Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contract_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            v1_filename TEXT NOT NULL,
            v2_filename TEXT NOT NULL,
            compared_at TEXT NOT NULL,
            diff_summary_json TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_contract(contract_id: str, filename: str, status: str = "Analyzed",
                  effective_date: str = "Not found in contract",
                  expiration_date: str = "Not found in contract",
                  obligation_count: int = 0, risk_count: int = 0,
                  summary_json: str = "{}"):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT OR REPLACE INTO contracts 
        (id, filename, upload_date, status, effective_date, expiration_date, obligation_count, risk_count, summary_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (contract_id, filename, now, status, effective_date, expiration_date, obligation_count, risk_count, summary_json))
    conn.commit()
    conn.close()


def save_extracted_fields(contract_id: str, fields: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM extracted_fields WHERE contract_id = ?", (contract_id,))
    for f in fields:
        cursor.execute("""
            INSERT INTO extracted_fields (contract_id, field_name, value, source_page, source_clause, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (contract_id, f.get('field_name', ''), f.get('value', ''), f.get('source_page', 1), f.get('source_clause', ''), f.get('confidence', 0.9)))
    conn.commit()
    conn.close()


def save_obligations(contract_id: str, obligations: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM obligations WHERE contract_id = ?", (contract_id,))
    for ob in obligations:
        cursor.execute("""
            INSERT INTO obligations (contract_id, party_responsible, obligation_text, deadline, deadline_type, frequency, source_page, clause_text, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contract_id,
            ob.get('party_responsible', 'Unknown'),
            ob.get('obligation_text', ''),
            ob.get('deadline', 'Not specified'),
            ob.get('deadline_type', 'Fixed Date'),
            ob.get('frequency', 'One-time'),
            ob.get('source_page', 1),
            ob.get('clause_text', ''),
            ob.get('status', 'Upcoming')
        ))
    conn.commit()
    conn.close()


def update_obligation_status(obligation_id: int, new_status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE obligations SET status = ? WHERE id = ?", (new_status, obligation_id))
    conn.commit()
    conn.close()


def save_risks(contract_id: str, risks: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM risks WHERE contract_id = ?", (contract_id,))
    for r in risks:
        cursor.execute("""
            INSERT INTO risks (contract_id, risk_title, severity, reason, source_page, clause_text, action_recommended)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            contract_id,
            r.get('risk_title', 'Risk Item'),
            r.get('severity', 'Medium'),
            r.get('reason', ''),
            r.get('source_page', 1),
            r.get('clause_text', ''),
            r.get('action_recommended', 'Human Review Recommended')
        ))
    conn.commit()
    conn.close()


def save_timeline_events(contract_id: str, events: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM timeline_events WHERE contract_id = ?", (contract_id,))
    for ev in events:
        cursor.execute("""
            INSERT INTO timeline_events (contract_id, event_title, party, date_str, event_type, source_page, alert_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            contract_id,
            ev.get('event_title', 'Contract Event'),
            ev.get('party', 'General'),
            ev.get('date_str', 'N/A'),
            ev.get('event_type', 'Milestone'),
            ev.get('source_page', 1),
            ev.get('alert_level', 'Upcoming')
        ))
    conn.commit()
    conn.close()


def save_chat_message(contract_id: str, role: str, message: str, citations: List[Dict[str, Any]] = None):
    conn = get_connection()
    cursor = conn.cursor()
    citations_json = json.dumps(citations or [])
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO chat_history (contract_id, role, message, citations_json, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (contract_id, role, message, citations_json, now))
    conn.commit()
    conn.close()


def get_chat_history(contract_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, message, citations_json, timestamp FROM chat_history WHERE contract_id = ? ORDER BY id ASC", (contract_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            'role': r['role'],
            'message': r['message'],
            'citations': json.loads(r['citations_json'] or '[]'),
            'timestamp': r['timestamp']
        })
    return result


def get_all_contracts() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contracts ORDER BY upload_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_contract(contract_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_contract_obligations(contract_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM obligations WHERE contract_id = ?", (contract_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_obligations() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, c.filename FROM obligations o 
        JOIN contracts c ON o.contract_id = c.id
        ORDER BY o.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_contract_risks(contract_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM risks WHERE contract_id = ?", (contract_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_contract_timeline(contract_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM timeline_events WHERE contract_id = ?", (contract_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_contract_fields(contract_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM extracted_fields WHERE contract_id = ?", (contract_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_contract(contract_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
    cursor.execute("DELETE FROM extracted_fields WHERE contract_id = ?", (contract_id,))
    cursor.execute("DELETE FROM obligations WHERE contract_id = ?", (contract_id,))
    cursor.execute("DELETE FROM risks WHERE contract_id = ?", (contract_id,))
    cursor.execute("DELETE FROM timeline_events WHERE contract_id = ?", (contract_id,))
    cursor.execute("DELETE FROM chat_history WHERE contract_id = ?", (contract_id,))
    conn.commit()
    conn.close()
