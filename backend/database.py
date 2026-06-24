import sqlite3
import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger("ocr_service.database")

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str):
    """Initializes the database and creates required tables if they don't exist."""
    logger.info(f"Initializing database at: {db_path}")
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Create the prescriptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            image_name TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            structured_json TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def save_prescription(db_path: str, prescription_id: str, session_id: str, uploaded_by: str, image_name: str, raw_text: str, structured_data: dict, confidence: float) -> bool:
    """Saves a prescription record to the database."""
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        structured_json_str = json.dumps(structured_data)
        created_at_str = datetime.now(timezone.utc).isoformat()
        
        cursor.execute(
            """
            INSERT INTO prescriptions (id, session_id, uploaded_by, image_name, raw_text, structured_json, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (prescription_id, session_id, uploaded_by, image_name, raw_text, structured_json_str, confidence, created_at_str)
        )
        conn.commit()
        conn.close()
        logger.info(f"Successfully saved prescription {prescription_id} to database.")
        return True
    except Exception as e:
        logger.error(f"Failed to save prescription to database: {e}")
        return False

def get_prescription(db_path: str, prescription_id: str) -> dict:
    """Retrieves a prescription record by its unique ID."""
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM prescriptions WHERE id = ?", (prescription_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Parse row into a dictionary and decode structured_json
            res = dict(row)
            try:
                res["structured_data"] = json.loads(res["structured_json"])
            except Exception:
                res["structured_data"] = {}
            # Remove raw json string from response mapping to clean output
            res.pop("structured_json", None)
            return res
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve prescription {prescription_id} from database: {e}")
        return None
