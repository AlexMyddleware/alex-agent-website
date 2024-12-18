import sys
import tkinter as tk
from gui.app import ProductivityApp
from models.browser_monitor import FirefoxMonitor

if __name__ == "__main__":
    # Check if running in unblock mode
    if len(sys.argv) > 1 and sys.argv[1] == "unblock":
        print("Unblocking all sites...")
        monitor = FirefoxMonitor()
        success = monitor.unblock_sites()
        if success:
            print("Sites unblocked successfully!")
        else:
            print("Failed to unblock sites. Please check the error messages above.")
        input("Press Enter to exit...")
    else:
        # Normal app startup
        root = tk.Tk()
        app = ProductivityApp(root)
        root.mainloop()
