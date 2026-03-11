import sqlite3
import datetime

DB_FILE = 'runs.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            total_tests INTEGER,
            passed INTEGER,
            failed INTEGER,
            avg_latency REAL,
            p95_latency REAL,
            error_rate REAL,
            is_available BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def save_run(stats):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO runs (timestamp, total_tests, passed, failed, avg_latency, p95_latency, error_rate, is_available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.datetime.now().isoformat(),
        stats['total'], stats['passed'], stats['failed'],
        stats['avg_latency'], stats['p95_latency'],
        stats['error_rate'], stats['is_available']
    ))
    conn.commit()
    conn.close()

def get_runs(limit=15):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM runs ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
