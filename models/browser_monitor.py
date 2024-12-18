import sqlite3
import os
from datetime import datetime
import platform

class FirefoxMonitor:
    def __init__(self):
        self.firefox_path = self._get_firefox_profile_path()

        self.blocked_sites = [
            "facebook.com",
            "www.youtube.com",
            "https://www.youtube.com/",
            "https://www.youtube.com",
            "youtube.com",
            "www.instagram.com",
            "instagram.com",
            "www.twitter.com",
            "twitter.com",
            "reddit.com",
            "www.tiktok.com",
            "tiktok.com",
            "www.twitch.tv",
            "twitch.tv",
            "old.reddit.com",
            # Reddit variants
            "www.reddit.com",
            "old.reddit.com",
            "new.reddit.com",
            "np.reddit.com",
            # Add https and http explicitly
            "https://reddit.com",
            "https://www.reddit.com",
            "http://reddit.com",
            "http://www.reddit.com",
            '/r/',
            # Add your other sites with similar variants
            "facebook.com",
            "www.facebook.com",
            "youtube.com",
            "www.youtube.com",
            "4chan.org",
            "www.4chan.org",
            "4chan.net",
            "www.4chan.net",
            "4channel.org",
            "www.4channel.org",
            "sflix.to",
            "www.sflix.to",
            "sflix.to",
            "www.sflix.to",
            "netflix.com",
            "www.netflix.com",
            "netflix.net",
            "www.netflix.net",
            "netflix.net",
            "www.netflix.net",
        ]  # You can modify this list
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