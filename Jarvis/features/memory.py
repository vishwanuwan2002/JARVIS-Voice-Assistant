"""Conversation memory backed by SQLite.

Stores message history per session and provides retrieval for context windowing.
This is intentionally lightweight and uses only the Python stdlib `sqlite3`.
"""

import os
import sqlite3
from typing import List, Tuple

DB_PATH = os.environ.get('JARVIS_MEMORY_DB', os.path.join(os.path.dirname(__file__), '..', 'memory.db'))


def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = _get_conn()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session TEXT,
        role TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()


def save_message(session: str, role: str, content: str):
    conn = _get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO messages (session, role, content) VALUES (?, ?, ?)', (session, role, content))
    conn.commit()
    conn.close()


def get_recent(session: str, limit: int = 10) -> List[Tuple[str, str, str]]:
    conn = _get_conn()
    c = conn.cursor()
    c.execute('SELECT role, content, created_at FROM messages WHERE session=? ORDER BY id DESC LIMIT ?', (session, limit))
    rows = c.fetchall()
    conn.close()
    # return in chronological order
    return list(reversed(rows))


def clear_session(session: str):
    conn = _get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE session=?', (session,))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    save_message('default', 'user', 'Hello, this is a test')
    save_message('default', 'assistant', 'Hello, I am Kael AI')
    print(get_recent('default', 5))
