import sqlite3
from datetime import datetime

class JarvisMemory:
    def __init__(self, db_path="jarvis_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    message TEXT,
                    timestamp TIMESTAMP
                )
            ''')
            conn.commit()

    def save_fact(self, content, category="general"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO facts (content, category, created_at) VALUES (?, ?, ?)",
                (content, category, datetime.now())
            )
            conn.commit()
        return "Fato memorizado, Senhor."

    def get_relevant_facts(self, query):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM facts WHERE content LIKE ?", (f'%{query}%',))
            results = cursor.fetchall()
            return [r[0] for r in results]

    def add_to_history(self, role, message):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO history (role, message, timestamp) VALUES (?, ?, ?)",
                (role, message, datetime.now())
            )
            conn.commit()

    def get_recent_context(self, limit=5):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, message FROM history ORDER BY id DESC LIMIT ?", (limit,)
            )
            context = cursor.fetchall()
            return "\n".join([f"{r[0]}: {r[1]}" for r in reversed(context)])