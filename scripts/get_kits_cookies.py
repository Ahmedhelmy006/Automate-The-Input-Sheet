import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from services.PlaywrightDriver import PlaywrightDriver

def save_cookies(url, save_path):
    # Initialize PlaywrightDriver (no cookies_file provided for a fresh session)
    driver = PlaywrightDriver()
    context = driver.initialize_driver()
    page = context.new_page()

    # Open the website
    page.goto(url)
    print("Please log in manually. Press Enter when done...")
    input()  # Wait for manual login

    # Save cookies
    cookies = context.cookies()
    with open(save_path, 'w') as file:
        json.dump(cookies, file, indent=4)
        print(f"Cookies have been saved to {save_path}")

    # Close the browser
    driver.close(context)

if __name__ == "__main__":
    WEBSITE_URL = "https://app.kit.com/dashboard"  # Replace with the website URL
    COOKIES_FILE = r"D:\Automate the Inputsheet\data\cookies\kits_cookies.json"

    save_cookies(WEBSITE_URL, COOKIES_FILE)
