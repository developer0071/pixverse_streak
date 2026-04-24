import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def run_streak():
    username = os.getenv("USER_ID")
    password = os.getenv("USER_PASS")

    if not username or not password:
        raise ValueError("USER_ID and USER_PASS environment variables must be set.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()

        try:
            # ── 1. Load the homepage ──────────────────────────────────────────
            print("Opening animesss.tv...")
            page.goto("https://animesss.tv/", wait_until="domcontentloaded", timeout=60000)
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except PlaywrightTimeoutError:
                print("networkidle timed out — continuing.")

            # ── 2. Dismiss bottom toast banner (if present) ───────────────────
            # The site shows a Telegram promo banner at the bottom with an × button
            try:
                close_btn = page.locator(".notify-bottom .close, .notify .close, .alert .close").first
                if close_btn.is_visible():
                    close_btn.click(timeout=3000)
                    print("Dismissed bottom banner.")
            except Exception:
                pass

            # ── 3. Click the header "ВОЙТИ" button to open the login modal ────
            print("Clicking header ВОЙТИ button...")
            
            header_login = page.get_by_text("ВОЙТИ").filter(visible=True).first
            
            try:
                header_login.wait_for(state="visible", timeout=15000)
                header_login.click(timeout=15000)
            except PlaywrightTimeoutError:
                print("Visible click timed out — force-clicking...")
                header_login.click(force=True)
                
            # ── 4. Wait for the login modal to appear ─────────────────────────
            print("Waiting for login modal...")
            try:
                page.wait_for_selector('input[placeholder="Ваш логин"]', timeout=20000)
            except PlaywrightTimeoutError:
                page.screenshot(path="error_screenshot.png")
                raise RuntimeError("Login modal did not appear. Screenshot saved.")

            # ── 5. Fill credentials ───────────────────────────────────────────
            print("Entering credentials...")
            page.locator('input[placeholder="Ваш логин"]').fill(username)
            page.locator('input[placeholder="Ваш пароль"]').fill(password)

            # ── 6. Submit ─────────────────────────────────────────────────────
            print("Submitting...")
            # The pink submit button inside the modal says "ВОЙТИ НА САЙТ"
            submit = page.locator('button:has-text("ВОЙТИ НА САЙТ")').first
            submit.click(timeout=15000)

            # ── 7. Confirm login ──────────────────────────────────────────────
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except PlaywrightTimeoutError:
                pass

            time.sleep(5)  # Stay on page so the daily visit is registered
            print(f"✓ Logged in as {username}. Streak maintained!")

        except Exception as e:
            print(f"✗ Error: {e}")
            try:
                page.screenshot(path="error_screenshot.png")
                print("Screenshot saved → check Actions artifacts.")
            except Exception:
                pass
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    run_streak()