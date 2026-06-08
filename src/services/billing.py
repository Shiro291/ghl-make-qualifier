import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'billing.db')

def init_billing_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            client_id TEXT PRIMARY KEY,
            requests_used INTEGER DEFAULT 0,
            tier TEXT DEFAULT 'free'
        )
    ''')
    conn.commit()
    conn.close()

def check_and_increment_usage(client_id: str = "default_client") -> bool:
    """
    Returns True if allowed, False if limit exceeded.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT requests_used, tier FROM usage WHERE client_id = ?', (client_id,))
    row = c.fetchone()
    
    if not row:
        c.execute('INSERT INTO usage (client_id, requests_used, tier) VALUES (?, 1, "free")', (client_id,))
        conn.commit()
        conn.close()
        return True
        
    requests_used, tier = row
    
    # Simple tier limits
    limit = 10 if tier == 'free' else 10000
    
    if requests_used >= limit:
        conn.close()
        return False
        
    c.execute('UPDATE usage SET requests_used = requests_used + 1 WHERE client_id = ?', (client_id,))
    conn.commit()
    conn.close()
    return True
