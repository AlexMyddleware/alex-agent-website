import os

class FirefoxBlocker:
    def __init__(self, firefox_path, blocked_sites):
        self.firefox_path = firefox_path
        self.blocked_sites = blocked_sites

    def block_sites(self):
        """Firefox-specific blocking implementation"""
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

    def unblock_sites(self):
        """Firefox-specific unblocking implementation"""
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