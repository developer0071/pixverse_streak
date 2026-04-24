import os
import time
import random
from playwright.sync_api import sync_playwright

def run_streak():
    # Fetch credentials from the environment variables set by GitHub
    username = os.getenv("USER_ID")
    password = os.getenv("USER_PASS")

    if not username or not password:
        print("Error: Credentials not found in environment.")
        return

    with sync_playwright() as p:
        # Launch browser - slow_mo adds a 'human' delay between actions
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Navigating to login page...")
        page.goto("https://example.com/login", wait_until="networkidle")

        # Human-like interaction: typing with delays
        page.type('input[name="username"]', username, delay=random.randint(50, 150))
        page.type('input[name="password"]', password, delay=random.randint(50, 150))
        
        # Click login and wait for navigation
        page.click('button[id="login-button"]')
        page.wait_for_load_state("networkidle")

        # Verify login success (check for a logout button or profile link)
        if page.query_selector(".profile-icon"):
            print("Login successful!")
            # Navigate to the specific streak/check-in page if different
            page.goto("https://example.com/daily-checkin")
            time.sleep(random.randint(2, 5)) 
            print("Streak recorded.")
        else:
            print("Login failed. Check credentials or site structure.")

        browser.close()

if __name__ == "__main__":
    run_streak()