import sqlite3
from datetime import datetime

class ActivityDatabase:
    def __init__(self):
        self.db_path = 'productivity.db'
        self.setup_database()
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS productive_sessions (
                id INTEGER PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER,
                date DATE
            )
        ''')
        conn.commit()
        conn.close()
