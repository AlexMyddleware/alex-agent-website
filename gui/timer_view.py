import tkinter as tk
from tkinter import ttk
from datetime import datetime

class TimerView:
    def __init__(self, parent):
        self.parent = parent
        self.timer_label = ttk.Label(parent, text="No active session")
        self.timer_label.grid(row=2, column=0, columnspan=3, pady=5)
        self.start_time = None
        self.timer_running = False

    def update_timer(self):
        if self.timer_running and self.start_time:
            elapsed = datetime.now() - self.start_time
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            seconds = int(elapsed.total_seconds() % 60)
            self.timer_label.config(text=f"Session time: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.parent.after(1000, self.update_timer)
