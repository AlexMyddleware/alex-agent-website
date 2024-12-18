import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ActivityTracker:
    def __init__(self):
        self.db_path = 'productivity.db'
        self.setup_database()
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create tables for tracking productive time
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
    
    def start_session(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        current_time = datetime.now()
        c.execute('''
            INSERT INTO productive_sessions (start_time, date)
            VALUES (?, ?)
        ''', (current_time, current_time.date()))
        
        conn.commit()
        conn.close()
        
    def end_session(self):
        conn = sqlite3.connect(self.db_path)
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

class ProductivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity Tracker")
        self.tracker = ActivityTracker()
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add buttons
        ttk.Button(self.main_frame, text="Start Session", 
                  command=self.tracker.start_session).grid(row=0, column=0, pady=5)
        ttk.Button(self.main_frame, text="End Session", 
                  command=self.tracker.end_session).grid(row=0, column=1, pady=5)
        ttk.Button(self.main_frame, text="Show Stats", 
                  command=self.show_stats).grid(row=0, column=2, pady=5)
        
        # Add stats display
        self.stats_frame = ttk.Frame(self.main_frame)
        self.stats_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
    def show_stats(self):
        conn = sqlite3.connect(self.tracker.db_path)
        c = conn.cursor()
        
        # Get last 7 days of data
        c.execute('''
            SELECT date, SUM(duration) 
            FROM productive_sessions 
            WHERE date >= date('now', '-7 days')
                AND duration IS NOT NULL
            GROUP BY date
            ORDER BY date
        ''')
        
        results = c.fetchall()  # Store results in a variable
        
        if not results:  # Check if we have any data
            print("No completed sessions found yet")
            return
        
        # Only unpack if we have results
        dates, durations = zip(*results)
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(dates, durations)
        ax.set_title('Productive Time by Day')
        ax.set_xlabel('Date')
        ax.set_ylabel('Minutes')
        
        # Clear previous graph if it exists
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0)
        
        conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductivityApp(root)
    root.mainloop()
