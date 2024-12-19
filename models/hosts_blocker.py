import time
from datetime import datetime
import platform
import sys
import argparse

# Determine the hosts file location based on the operating system
def get_hosts_path():
    if platform.system() == "Windows":
        return r"C:\Windows\System32\drivers\etc\hosts"
    else:  # Linux and MacOS
        return "/etc/hosts"

class WebsiteBlocker:
    def __init__(self):
        self.hosts_path = get_hosts_path()
        self.redirect = "127.0.0.1"
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
        ]

    def block_websites(self):
        try:
            with open(self.hosts_path, 'r+') as hosts_file:
                content = hosts_file.read()
                for site in self.blocked_sites:
                    if site not in content:
                        hosts_file.write(f"{self.redirect} {site}\n")
            print("Websites blocked successfully")
        except PermissionError:
            print("Error: Please run the script with administrator/root privileges")
            sys.exit(1)

    def unblock_websites(self):
        try:
            with open(self.hosts_path, 'r+') as hosts_file:
                lines = hosts_file.readlines()
                hosts_file.seek(0)
                for line in lines:
                    if not any(site in line for site in self.blocked_sites):
                        hosts_file.write(line)
                hosts_file.truncate()
            print("Websites unblocked successfully")
        except PermissionError:
            print("Error: Please run the script with administrator/root privileges")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Website Blocker')
    parser.add_argument('action', choices=['block', 'unblock', 'status'],
                       help='Action to perform: block, unblock, or check status')
    
    args = parser.parse_args()
    blocker = WebsiteBlocker()
    
    if args.action == 'block':
        blocker.block_websites()
    elif args.action == 'unblock':
        blocker.unblock_websites()
    elif args.action == 'status':
        # Add a new method to check if sites are currently blocked
        with open(blocker.hosts_path, 'r') as hosts_file:
            content = hosts_file.read()
            is_blocked = any(site in content for site in blocker.blocked_sites)
            print(f"Websites are currently {'blocked' if is_blocked else 'unblocked'}")
