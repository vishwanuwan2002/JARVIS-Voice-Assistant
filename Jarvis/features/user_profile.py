"""User profile memory system for JARVIS.
Stores user preferences, habits, and personal information to make interactions more personalized.
"""

import os
import sqlite3
import json
from typing import Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'user_profile.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_profile (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def set_preference(key: str, value: Any):
    """Set a user preference."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)',
              (key, json.dumps(value)))
    conn.commit()
    conn.close()

def get_preference(key: str, default=None) -> Any:
    """Get a user preference."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT value FROM user_profile WHERE key=?', (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return default

def get_all_preferences() -> Dict[str, Any]:
    """Get all user preferences."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT key, value FROM user_profile')
    rows = c.fetchall()
    conn.close()
    return {key: json.loads(value) for key, value in rows}

def remember_interaction(command: str, response: str, success: bool = True):
    """Remember successful interactions to learn user patterns."""
    interactions = get_preference('interactions', [])
    interactions.append({
        'command': command,
        'response': response,
        'success': success,
        'timestamp': str(__import__('datetime').datetime.now())
    })
    # Keep only last 100 interactions
    interactions = interactions[-100:]
    set_preference('interactions', interactions)

def learn_favorite_app(app_name: str):
    """Learn user's favorite apps."""
    favorites = get_preference('favorite_apps', [])
    if app_name not in favorites:
        favorites.append(app_name)
        set_preference('favorite_apps', favorites)

def get_favorite_apps() -> list:
    """Get user's favorite apps."""
    return get_preference('favorite_apps', [])

def set_user_name(name: str):
    """Set user's name."""
    set_preference('user_name', name)

def get_user_name() -> str:
    """Get user's name."""
    return get_preference('user_name', 'sir')

def set_location(city: str, country: str = None):
    """Set user's default location."""
    set_preference('location', {'city': city, 'country': country})

def get_location() -> Optional[Dict]:
    """Get user's default location."""
    return get_preference('location')

# Initialize database on import
init_db()