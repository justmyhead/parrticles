import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "data", "parrticles.db"))


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                url         TEXT NOT NULL,
                title       TEXT NOT NULL,
                description TEXT NOT NULL,
                sent_at     TEXT NOT NULL,
                feedback    TEXT
            )
        """)
        conn.commit()


def record_sent(url: str, title: str, description: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO sites (url, title, description, sent_at) VALUES (?, ?, ?, ?)",
            (url, title, description, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return cur.lastrowid


def record_feedback(site_id: int, feedback: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE sites SET feedback = ? WHERE id = ?", (feedback, site_id))
        conn.commit()


def get_all_urls() -> list[str]:
    with sqlite3.connect(DB_PATH) as conn:
        return [r[0] for r in conn.execute("SELECT url FROM sites").fetchall()]


def get_liked_sites() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT url, title, description FROM sites WHERE feedback = 'yes'"
        ).fetchall()
        return [dict(r) for r in rows]


def get_disliked_sites() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT url, title, description FROM sites WHERE feedback = 'no'"
        ).fetchall()
        return [dict(r) for r in rows]


def get_history() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM sites ORDER BY sent_at DESC").fetchall()
        return [dict(r) for r in rows]
