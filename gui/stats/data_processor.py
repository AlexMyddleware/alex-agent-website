import sqlite3
from datetime import datetime

class SessionDataProcessor:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def get_session_data(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 
                date,
                start_time,
                duration
            FROM productive_sessions 
            WHERE date >= date('now', '-7 days')
                AND duration IS NOT NULL
            ORDER BY date, start_time
        ''')
        
        results = c.fetchall()
        conn.close()
        
        if not results:
            return None
            
        # Process the data
        sessions_by_date = {}
        for date, start_time, duration in results:
            if date not in sessions_by_date:
                sessions_by_date[date] = []
            start_hour = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M')
            sessions_by_date[date].append((start_hour, duration))
            
        return sessions_by_date 