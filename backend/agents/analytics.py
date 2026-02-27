import sqlite3
import os
import datetime

ANALYTICS_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "analytics.db")

def init_analytics_db():
    conn = sqlite3.connect(ANALYTICS_DB_PATH)
    cursor = conn.cursor()
    
    # Table for search logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        intent TEXT,
        found_locally BOOLEAN,
        redirected_to_competitor BOOLEAN
    )
    ''')
    
    # Table for device health
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        device_id TEXT PRIMARY KEY,
        status TEXT,
        last_seen DATETIME,
        battery_level INTEGER
    )
    ''')
    
    conn.commit()
    conn.close()

def log_search(query: str, intent: str, found_locally: bool, redirected: bool):
    conn = sqlite3.connect(ANALYTICS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO search_logs (query, intent, found_locally, redirected_to_competitor) VALUES (?, ?, ?, ?)",
        (query, intent, found_locally, redirected)
    )
    conn.commit()
    conn.close()

def update_device_status(device_id: str, status: str, battery: int):
    conn = sqlite3.connect(ANALYTICS_DB_PATH)
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO devices (device_id, status, last_seen, battery_level) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(device_id) DO UPDATE SET status=excluded.status, last_seen=excluded.last_seen, battery_level=excluded.battery_level",
        (device_id, status, now, battery)
    )
    conn.commit()
    conn.close()

init_analytics_db()
