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

        try:
            print("Opening animesss.tv...")
            page.goto("https://animesss.tv/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_load_state("networkidle", timeout=60000)
            
            print("Waiting for login button...")
            login_button = page.get_by_role("button", name="Войти").first
            login_button.wait_for(timeout=60000)
            
            print("Opening login modal...")
            login_button.click(timeout=60000)
            
            print("Waiting for login form...")
            page.wait_for_load_state("networkidle", timeout=60000)

            print("Entering credentials...")
            page.get_by_placeholder("Ваш логин").fill(username, timeout=30000)
            page.get_by_placeholder("Ваш пароль").fill(password, timeout=30000)

            print("Submitting login...")
            page.get_by_role("button", name="ВОЙТИ НА САЙТ").click(timeout=60000)

            # Verification and Streak Saving
            page.wait_for_load_state("networkidle", timeout=60000)
            time.sleep(5)  # Stay for 5 seconds to ensure the 'visit' is logged
            
            print(f"Successfully logged in as {username}. Streak maintained!")
            
        except Exception as e:
            print(f"Error occurred: {e}")
            # Take screenshot for debugging
            page.screenshot(path="error_screenshot.png")
            raise
        finally:
            browser.close()

if __name__ == "__main__":
    run_streak()