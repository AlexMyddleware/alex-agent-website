import tkinter as tk
from tkinter import ttk, messagebox
from .stats_view import StatsView
from .timer_view import TimerView
from models.session import SessionTracker
from datetime import datetime
from models.browser_monitor import FirefoxMonitor

class ProductivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity Tracker")
        self.tracker = SessionTracker()
        self.monitor = FirefoxMonitor()
        
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_gui(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add status text widget
        self.status_text = tk.Text(self.main_frame, height=10, width=50)
        self.status_text.grid(row=1, column=0, columnspan=6, pady=10)
        
        self.timer_view = TimerView(self.main_frame)
        self.stats_view = StatsView(self.main_frame, self.tracker)
        
        # Add buttons
        ttk.Button(self.main_frame, text="Start Session", 
                  command=self.start_session).grid(row=0, column=0, pady=5)
        ttk.Button(self.main_frame, text="End Session", 
                  command=self.end_session).grid(row=0, column=1, pady=5)
        ttk.Button(self.main_frame, text="Show Stats",
                  command=self.show_stats).grid(row=0, column=2, pady=5)
        ttk.Button(self.main_frame, text="Check Blocking Status",
                  command=self.show_blocking_status).grid(row=0, column=3, pady=5)

        # Add new buttons for hosts-based blocking
        self.hosts_block_button = tk.Button(
            self.main_frame,
            text="Block Sites (Hosts)",
            command=self.block_sites_hosts
        )
        self.hosts_block_button.grid(row=0, column=4, pady=5)

        self.hosts_unblock_button = tk.Button(
            self.main_frame,
            text="Unblock Sites (Hosts)",
            command=self.unblock_sites_hosts
        )
        self.hosts_unblock_button.grid(row=0, column=5, pady=5)

        # Initial status update
        self.update_status()

    def start_session(self):
        self.tracker.start_session()
        self.timer_view.start_time = datetime.now()
        self.timer_view.timer_running = True
        self.timer_view.update_timer()

    def end_session(self):
        attempts = self.tracker.end_session()  # Capture the return value
        self.timer_view.timer_running = False
        self.timer_view.timer_label.config(text="No active session")
        
        # Show attempts in a popup if any were detected
        if attempts:
            attempt_text = "Blocked site access attempts:\n\n"
            for url, time in attempts:
                attempt_text += f"• {url} at {time.strftime('%H:%M:%S')}\n"
            messagebox.showwarning("Access Attempts Detected", attempt_text)

    def show_stats(self):
        self.stats_view.show_stats()

    def show_blocking_status(self):
        status_window = tk.Toplevel(self.root)
        status_window.title("Website Blocking Status")
        status_window.geometry("500x600")
        
        # Add a text widget to show the report
        text_widget = tk.Text(status_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(status_window, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Get and insert the status report
        status_report = self.monitor.check_blocking_status()
        text_widget.insert(tk.END, status_report)
        text_widget.configure(state='disabled')  # Make it read-only

    def show_message(self, title, message):
        """Show a popup message dialog"""
        messagebox.showinfo(title, message)

    def block_sites_hosts(self):
        """Explicitly use hosts-based blocking"""
        try:
            self.monitor.hosts_blocker.block_websites()
            messagebox.showinfo("Success", "Sites blocked using hosts file")
            self.update_status()
        except PermissionError:
            messagebox.showerror(
                "Administrator Rights Required", 
                "Please run the application as administrator to modify the hosts file."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to block sites: {str(e)}")

    def unblock_sites_hosts(self):
        """Explicitly use hosts-based unblocking"""
        try:
            self.monitor.hosts_blocker.unblock_websites()
            messagebox.showinfo("Success", "Sites unblocked from hosts file")
            self.update_status()
        except PermissionError:
            messagebox.showerror(
                "Administrator Rights Required", 
                "Please run the application as administrator to modify the hosts file."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to unblock sites: {str(e)}")

    def update_status(self):
        # Update to check both Firefox and hosts status
        firefox_status = self.monitor.check_blocking_status()
        
        # Check hosts status
        with open(self.monitor.hosts_blocker.hosts_path, 'r') as hosts_file:
            content = hosts_file.read()
            hosts_blocked = any(site in content for site in self.monitor.hosts_blocker.blocked_sites)
        
        status_text = (
            f"Firefox Blocking:\n{firefox_status}\n\n"
            f"Hosts File Blocking: {'🚫 Active' if hosts_blocked else '✅ Inactive'}"
        )
        self.status_text.delete('1.0', tk.END)
        self.status_text.insert('1.0', status_text)

    def on_closing(self):
        self.stats_view.cleanup()
        self.root.destroy()
