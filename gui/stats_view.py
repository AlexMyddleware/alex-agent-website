import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3

class StatsView:
    def __init__(self, parent, session_tracker):
        self.parent = parent
        self.tracker = session_tracker
        self.stats_frame = ttk.Frame(parent)
        self.stats_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
    def show_stats(self):
        conn = sqlite3.connect(self.tracker.db.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT date, SUM(duration) 
            FROM productive_sessions 
            WHERE date >= date('now', '-7 days')
                AND duration IS NOT NULL
            GROUP BY date
            ORDER BY date
        ''')
        
        results = c.fetchall()
        
        if not results:
            print("No completed sessions found yet")
            return
            
        dates, durations = zip(*results)
        
        # Clear previous graph if it exists
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(dates, durations)
        ax.set_title('Productive Time by Day')
        ax.set_xlabel('Date')
        ax.set_ylabel('Minutes')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0)
        
        conn.close()
