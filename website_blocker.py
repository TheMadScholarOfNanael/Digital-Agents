import time
from datetime import datetime
import os
import sys

# Path to the Windows hosts file
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"

# Get user input for websites and blocking hours
def get_user_settings():
    print("Enter websites to block (comma separated, e.g. facebook.com, youtube.com):")
    sites = input().split(",")
    websites = [site.strip() for site in sites if site.strip()] #takes list of website strings entered by user and strips of leading/trailing 
    #spaces to get clean list of sites to block
    print("Enter blocking start hour (24h format, e.g. 9 for 9am):")
    start_hour = int(input())
    print("Enter blocking end hour (24h format, e.g. 17 for 5pm):")
    end_hour = int(input())
    return websites, start_hour, end_hour

# Check if current time is within blocking hours
def is_block_time(start_hour, end_hour):
    now = datetime.now().hour
    if start_hour < end_hour:
        return start_hour <= now < end_hour #checks if current hour is within blocking period WHEN period does NOT cross midnight (e.g., 9 AM to 5 PM); 
        #returns TRUE if current hour is greater than or equal to start hour AND less than end hour
    else:  # Overnight block (e.g., 22 to 6)
        return now >= start_hour or now < end_hour #determines if current hour falls within overnight blocking period (e.g., 10 PM to 6 AM)

# Block websites by adding to hosts file
def block_websites(websites):
    with open(HOSTS_PATH, 'r+') as file:
        content = file.read()
        for site in websites:
            entry = f"{REDIRECT_IP} {site}\n"
            if entry not in content:
                file.write(entry)

# Unblock websites by removing from hosts file
def unblock_websites(websites):
    with open(HOSTS_PATH, 'r+') as file: #opens hosts file in read/write mode; with statement ensures file is properly closed 
        #after operations
        lines = file.readlines()
        file.seek(0) #moves file pointer to the beginning of the HOSTS file; when you start writing lines back to the file, 
        #it will overwrite from the start, not the end; important for correctly updating the hosts file when unblocking websites
        for line in lines:
            if not any(site in line for site in websites): #checks if NONE of websites to unblock are present in current line of HOSTS file 
                file.write(line)
        file.truncate()

def main():
    # Check for admin privileges on Windows to modify HOSTS file; gets user input for websites and hours to block; prints summary of
    # of blocking schedule; runs infinite loop to block/unblock websites during specified hours; handles script interruption 
    # by unblocking all sites before exiting 
    if sys.platform == 'win32':
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Please run this script as administrator.")
            sys.exit(1)
    else:
        if not hasattr(os, 'geteuid') or os.geteuid() != 0:
            print("Please run this script as administrator (root).")
            sys.exit(1)
    websites, start_hour, end_hour = get_user_settings()
    print(f"Blocking {websites} from {start_hour}:00 to {end_hour}:00 each day.")
    try:
        while True:
            if is_block_time(start_hour, end_hour):
                block_websites(websites)
                print("Websites are blocked.")
            else:
                unblock_websites(websites)
                print("Websites are unblocked.")
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nExiting and unblocking all sites...")
        unblock_websites(websites)
        print("All sites unblocked.")

if __name__ == "__main__":
    main()
