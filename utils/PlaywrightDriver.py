from playwright.sync_api import sync_playwright
import json

class PlaywrightDriver:
    def __init__(self, cookies_file=None):
        self.cookies_file = cookies_file
        self.playwright = None
        self.browser = None


    def initialize_driver(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',  # Disable the AutomationControlled flag
                '--no-sandbox',                                   # Useful for some environments
                '--disable-infobars',                             # Removes "Chrome is being controlled by automated software"
                '--disable-dev-shm-usage',                        # Prevents shared memory issues
                '--disable-extensions',                           # Disables all extensions
                '--disable-gpu',                                  # Disables GPU hardware acceleration
            ]
        )
        context = self.browser.new_context()

        if self.cookies_file:
            with open(self.cookies_file, 'r') as file:
                cookies = json.load(file)
                context.add_cookies(cookies)

        return context

    def close(self, context):
        context.close()
        self.browser.close()
        self.playwright.stop()

