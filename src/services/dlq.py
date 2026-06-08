import sqlite3
import os
import json
import logging

logger = logging.getLogger(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'failed_leads.db')

def init_dlq_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS dlq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_data TEXT,
            error_reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def send_to_dlq(lead_data: dict, error_reason: str):
    logger.warning(f"Sending lead to DLQ due to: {error_reason}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO dlq (lead_data, error_reason) VALUES (?, ?)', 
              (json.dumps(lead_data), error_reason))
    conn.commit()
    conn.close()
