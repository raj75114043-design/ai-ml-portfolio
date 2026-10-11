import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "operations.db"

SEED = [
    ("SITE-101", "DOWN", "North", 3),
    ("SITE-102", "UP", "South", 0),
    ("SITE-103", "DEGRADED", "East", 1),
    ("SITE-104", "UP", "West", 0),
]


def connect(read_only: bool = True) -> sqlite3.Connection:
    if not DB_PATH.exists():
        init()
    uri = f"file:{DB_PATH}?mode=ro" if read_only else f"file:{DB_PATH}"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS sites (site_id TEXT PRIMARY KEY, status TEXT, region TEXT, open_incidents INTEGER)")
    conn.executemany("INSERT OR REPLACE INTO sites VALUES (?, ?, ?, ?)", SEED)
    conn.commit()
    conn.close()
