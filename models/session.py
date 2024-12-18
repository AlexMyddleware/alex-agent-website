from datetime import datetime
from database.activity_db import ActivityDatabase
import sqlite3

class SessionTracker:
    def __init__(self):
        self.db = ActivityDatabase()
        
    def start_session(self):
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        current_time = datetime.now()
        c.execute('''
            INSERT INTO productive_sessions (start_time, date)
            VALUES (?, ?)
        ''', (current_time, current_time.date()))
        conn.commit()
        conn.close()
        
    def end_session(self):
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        current_time = datetime.now()
        c.execute('''
            UPDATE productive_sessions 
            SET end_time = ?, 
                duration = ROUND((julianday(?) - julianday(start_time)) * 24 * 60)
            WHERE end_time IS NULL
        ''', (current_time, current_time))
        conn.commit()
        conn.close()
