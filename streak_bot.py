import os
import time
import random
from playwright.sync_api import sync_playwright

def run_streak():
    username = os.getenv("USER_ID")
    password = os.getenv("USER_PASS")

    with sync_playwright() as p:
        # Using slow_mo helps bypass simple bot detection
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("Opening animesss.tv...")
        page.goto("https://animesss.tv/", wait_until="networkidle")

        print("Opening login modal...")
        page.get_by_role("button", name="Войти").first.click()        
        time.sleep(1)

        print("Entering credentials...")
        page.get_by_placeholder("Khurshid").fill(username)
        page.get_by_placeholder("••••••••••••").fill(password)

        # 3. Click the "ВОЙТИ НА САЙТ" button
        print("Submitting login...")
        page.get_by_role("button", name="ВОЙТИ НА САЙТ").click()

        # 4. Verification and Streak Saving
        # Most anime sites save the streak just by being logged in on the home page.
        page.wait_for_load_state("networkidle")
        time.sleep(5) # Stay for 5 seconds to ensure the 'visit' is logged
        
        print(f"Successfully logged in as {username}. Streak maintained!")
        
        browser.close()

if __name__ == "__main__":
    run_streak()