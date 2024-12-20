import sqlite3
import os
from datetime import datetime
import platform
from .hosts_blocker import WebsiteBlocker
from .config.blocked_sites import BLOCKED_SITES

class FirefoxMonitor:
    def __init__(self):
        self.firefox_path = self._get_firefox_profile_path()
        self.hosts_blocker = WebsiteBlocker()
        self.blocked_sites = BLOCKED_SITES
        
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
            firefox_success = self._block_sites_firefox()
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
        firefox_success = self._unblock_sites_firefox()
        hosts_success = False
        
        try:
            self.hosts_blocker.unblock_websites()
            hosts_success = True
        except Exception as e:
            print(f"Hosts unblocking failed: {e}")

        return firefox_success or hosts_success

    # Rename existing block_sites to _block_sites_firefox
    def _block_sites_firefox(self):
        """Original Firefox-specific blocking implementation"""
        if not self.firefox_path:
            print("Firefox profile not found")
            return False

        try:
            profile_dir = os.path.dirname(self.firefox_path)
            user_prefs_path = os.path.join(profile_dir, "user.js")

            # Create blocking rules
            blocking_rules = []
            for site in self.blocked_sites:
                site = site.replace("www.", "").replace("https://", "").replace("http://", "").strip("/")
                if site:
                    blocking_rules.append(f'user_pref("capability.policy.policynames", "blocksites");')
                    blocking_rules.append(f'user_pref("capability.policy.blocksites.sites", "http://{site} https://{site} http://www.{site} https://www.{site}");')
                    blocking_rules.append(f'user_pref("capability.policy.blocksites.checkloaduri.enabled", "allAccess");')

            # Write to user.js
            with open(user_prefs_path, 'w') as f:
                f.write('\n'.join(blocking_rules))

            print("Sites blocked successfully!")
            return True

        except Exception as e:
            print(f"Error blocking sites: {e}")
            return False

    # Rename existing unblock_sites to _unblock_sites_firefox
    def _unblock_sites_firefox(self):
        """Original Firefox-specific unblocking implementation"""
        if not self.firefox_path:
            print("Firefox profile not found")
            return False

        try:
            profile_dir = os.path.dirname(self.firefox_path)
            user_prefs_path = os.path.join(profile_dir, "user.js")

            # Remove the user.js file if it exists
            if os.path.exists(user_prefs_path):
                os.remove(user_prefs_path)
                print(f"Removed blocking rules from {user_prefs_path}")

            # Also check for prefs.js and remove blocking related entries
            prefs_js_path = os.path.join(profile_dir, "prefs.js")
            if os.path.exists(prefs_js_path):
                with open(prefs_js_path, 'r') as f:
                    lines = f.readlines()
                
                with open(prefs_js_path, 'w') as f:
                    for line in lines:
                        if not any(x in line.lower() for x in ["blocksites", "capability.policy"]):
                            f.write(line)

            print("Sites unblocked successfully!")
            return True

        except Exception as e:
            print(f"Error unblocking sites: {e}")
            return False

    def check_blocking_status(self, urls=None):
        """
        Check if specified URLs or all blocked sites are currently blocked.
        Returns:
            str: Formatted status report
        """
        if urls is None:
            urls = self.blocked_sites

        profile_dir = os.path.dirname(self.firefox_path)
        user_prefs_path = os.path.join(profile_dir, "user.js")
        
        # Check if blocking is actually enabled
        blocking_enabled = os.path.exists(user_prefs_path)
        
        status_report = ["Blocking Status Report:", "-" * 50]
        status_report.append(f"Global Blocking Status: {'🚫 Enabled' if blocking_enabled else '✅ Disabled'}\n")
        
        checked = set()
        for url in urls:
            normalized_url = url.lower().replace('https://', '').replace('http://', '').replace('www.', '').strip('/')
            if normalized_url not in checked:
                checked.add(normalized_url)
                is_blocked = blocking_enabled and url in self.blocked_sites
                status_report.append(f"{url:<30} {'🚫 Blocked' if is_blocked else '✅ Not Blocked'}")
        
        status_report.append("-" * 50)
        return "\n".join(status_report)