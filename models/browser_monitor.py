import sqlite3
import os
from datetime import datetime
import platform
from .hosts_blocker import WebsiteBlocker
from .config.blocked_sites import BLOCKED_SITES
from .firefox_blocker import FirefoxBlocker

class FirefoxMonitor:
    def __init__(self):
        self.firefox_path = self._get_firefox_profile_path()
        self.hosts_blocker = WebsiteBlocker()
        self.blocked_sites = BLOCKED_SITES
        self.firefox_blocker = FirefoxBlocker(self.firefox_path, self.blocked_sites)
        
        print(f"Firefox profile path: {self.firefox_path}")
        
    def _get_firefox_profile_path(self):
        if platform.system() == "Windows":
            path = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")
        else:  # macOS and Linux
            path = os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
            
        # Get the default profile (usually ends with .default-release)
        try:
            profiles = os.listdir(path)
            default_profile = next(p for p in profiles if p.endswith('default-release'))
            return os.path.join(path, default_profile, 'places.sqlite')
        except (FileNotFoundError, StopIteration):
            print("Firefox profile not found")
            return None
            
    def check_blocked_access(self, start_time):
        print(f"Checking for blocked access since: {start_time}")
        
        if not self.firefox_path or not os.path.exists(self.firefox_path):
            print("Firefox profile not found or inaccessible")
            return []
            
        attempts = []
        try:
            # Create a copy of places.sqlite as it might be locked by Firefox
            temp_db = self.firefox_path + '-temp'
            print(f"Creating temp database at: {temp_db}")
            
            with open(self.firefox_path, 'rb') as f_in:
                with open(temp_db, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            conn = sqlite3.connect(temp_db)
            c = conn.cursor()
            
            # Query recent history
            query = '''
                SELECT url, visit_date/1000000 
                FROM moz_places mp
                JOIN moz_historyvisits mh ON mp.id = mh.place_id
                WHERE visit_date/1000000 >= ?
                ORDER BY visit_date DESC
            '''
            print(f"Executing query with timestamp: {start_time.timestamp()}")
            
            c.execute(query, (start_time.timestamp(),))
            
            all_visits = c.fetchall()
            print(f"Found {len(all_visits)} total visits")
            
            for url, timestamp in all_visits:
                print(f"Checking URL: {url}")
                if any(site.lower() in url.lower() for site in self.blocked_sites):
                    visit_time = datetime.fromtimestamp(timestamp)
                    attempts.append((url, visit_time))
                    print(f"Found blocked attempt: {url} at {visit_time}")
                    
            conn.close()
            os.remove(temp_db)
            
        except Exception as e:
            print(f"Error monitoring Firefox: {e}")
            import traceback
            traceback.print_exc()
            
        print(f"Found {len(attempts)} blocked attempts")
        return attempts 

    def block_sites(self):
        """Block sites in both Firefox and hosts file"""
        firefox_success = False
        try:
            # Try Firefox blocking first
            firefox_success = self.firefox_blocker.block_sites()
        except Exception as e:
            print(f"Firefox blocking failed: {e}")

        if not firefox_success:
            print("Falling back to hosts-based blocking...")
            try:
                self.hosts_blocker.block_websites()
                return True
            except Exception as e:
                print(f"Hosts blocking failed: {e}")
                return False
        return True

    def unblock_sites(self):
        """Unblock sites from both Firefox and hosts file"""
        # Always try to unblock both methods
        firefox_success = self.firefox_blocker.unblock_sites()
        hosts_success = False
        
        try:
            self.hosts_blocker.unblock_websites()
            hosts_success = True
        except Exception as e:
            print(f"Hosts unblocking failed: {e}")

        return firefox_success or hosts_success

    def check_blocking_status(self, urls=None):
        return self.firefox_blocker.check_blocking_status(urls)