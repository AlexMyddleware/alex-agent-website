import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from datetime import datetime

class StatsView:
    def __init__(self, parent, session_tracker):
        self.parent = parent
        self.tracker = session_tracker
        self.stats_frame = ttk.Frame(parent)
        self.stats_frame.grid(row=1, column=0, columnspan=3, pady=10)
        self.current_figure = None
        
    def show_stats(self):
        # Clear previous figure if it exists
        if self.current_figure:
            plt.close(self.current_figure)
            
        conn = sqlite3.connect(self.tracker.db.db_path)
        c = conn.cursor()
        
        # Get individual sessions for the last 7 days
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
        
        if not results:
            print("No completed sessions found yet")
            return
            
        # Process the data
        sessions_by_date = {}
        for date, start_time, duration in results:
            if date not in sessions_by_date:
                sessions_by_date[date] = []
            start_hour = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M')
            sessions_by_date[date].append((start_hour, duration))

        # Create matplotlib figure
        self.current_figure = plt.figure(figsize=(10, 6))
        ax = self.current_figure.add_subplot(111)
        
        # Plot each session as a separate bar
        x_positions = []
        heights = []
        x_labels = []
        
        for i, (date, sessions) in enumerate(sessions_by_date.items()):
            for j, (start_time, duration) in enumerate(sessions):
                x_positions.append(i + j * 0.2)  # Offset each session within the day
                heights.append(duration)
                x_labels.append(f"{date}\n{start_time}")
        
        bars = ax.bar(x_positions, heights, width=0.15)
        
        # Customize the plot
        ax.set_title('Individual Sessions by Day')
        ax.set_xlabel('Date and Start Time')
        ax.set_ylabel('Duration (minutes)')
        
        # Rotate x-axis labels for better readability
        plt.xticks(x_positions, x_labels, rotation=45, ha='right')
        
        # Add duration labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}m',
                   ha='center', va='bottom')
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Clear previous widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(self.current_figure, master=self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0)
        
        conn.close()
        
    def cleanup(self):
        if self.current_figure:
            plt.close(self.current_figure)
