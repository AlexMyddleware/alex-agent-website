import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .stats.data_processor import SessionDataProcessor
from .stats.plot_manager import SessionPlotManager

class StatsView:
    def __init__(self, parent, session_tracker):
        self.parent = parent
        self.stats_frame = ttk.Frame(parent)
        self.stats_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        self.data_processor = SessionDataProcessor(session_tracker.db.db_path)
        self.plot_manager = SessionPlotManager()
        
    def show_stats(self):
        sessions_by_date = self.data_processor.get_session_data()
        
        if not sessions_by_date:
            print("No completed sessions found yet")
            return
            
        figure = self.plot_manager.create_session_plot(sessions_by_date)
        
        # Clear previous widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(figure, master=self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0)
        
    def cleanup(self):
        self.plot_manager.cleanup()
