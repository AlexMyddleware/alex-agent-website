import tkinter as tk
from tkinter import ttk
from .stats_view import StatsView
from .timer_view import TimerView
from models.session import SessionTracker
from datetime import datetime

class ProductivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity Tracker")
        self.tracker = SessionTracker()
        
        self.setup_gui()
        
    def setup_gui(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.timer_view = TimerView(self.main_frame)
        self.stats_view = StatsView(self.main_frame, self.tracker)
        
        # Add buttons
        ttk.Button(self.main_frame, text="Start Session", 
                  command=self.start_session).grid(row=0, column=0, pady=5)
        ttk.Button(self.main_frame, text="End Session", 
                  command=self.end_session).grid(row=0, column=1, pady=5)
        ttk.Button(self.main_frame, text="Show Stats",
                  command=self.show_stats).grid(row=0, column=2, pady=5)

    def start_session(self):
        self.tracker.start_session()
        self.timer_view.start_time = datetime.now()
        self.timer_view.timer_running = True
        self.timer_view.update_timer()

    def end_session(self):
        self.tracker.end_session()
        self.timer_view.timer_running = False
        self.timer_view.timer_label.config(text="No active session")

    def show_stats(self):
        self.stats_view.show_stats()
