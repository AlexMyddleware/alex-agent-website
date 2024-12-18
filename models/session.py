from datetime import datetime
from database.activity_db import ActivityDatabase
from .browser_monitor import FirefoxMonitor
import sqlite3

class SessionTracker:
    def __init__(self):
        self.db = ActivityDatabase()
        self.firefox_monitor = FirefoxMonitor()
        self.session_start_time = None
        
    def start_session(self):
        self.session_start_time = datetime.now()
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO productive_sessions (start_time, date)
            VALUES (?, ?)
        ''', (self.session_start_time, self.session_start_time.date()))
        conn.commit()
        conn.close()
        
    def end_session(self):
        if not self.session_start_time:
            print("No active session to end")  # Debug print
            return []
            
        print(f"Ending session that started at: {self.session_start_time}")  # Debug print
        
        # Check for blocked site attempts
        attempts = self.firefox_monitor.check_blocked_access(self.session_start_time)
        print(f"Found {len(attempts)} attempts during session")  # Debug print
        
        # Regular session end logic
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
        
        self.session_start_time = None
        return attempts
