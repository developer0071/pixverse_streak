import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def dismiss_overlays(page):
    """Try to close cookie banners, ad overlays, and popups before interacting."""
    overlay_selectors = [
        'button:has-text("Accept")',
        'button:has-text("Принять")',
        'button:has-text("OK")',
        'button:has-text("Закрыть")',
        'button:has-text("Close")',
        '[class*="cookie"] button',
        '[class*="consent"] button',
        '[class*="modal__close"]',
        '[class*="popup__close"]',
        '[aria-label="Close"]',
        '[aria-label="Закрыть"]',
        '.close',
    ]
    for sel in overlay_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.click(timeout=3000)
                print(f"Dismissed overlay: {sel}")
                time.sleep(0.5)
        except Exception:
            continue


def safe_click(page, locator):
    """Try normal click first; fall back to force-click if blocked by an overlay."""
    try:
        locator.click(timeout=15000)
    except PlaywrightTimeoutError:
        print("Normal click timed out — trying force click...")
        locator.click(force=True, timeout=15000)


def run_streak():
    username = os.getenv("USER_ID")
    password = os.getenv("USER_PASS")

    if not username or not password:
        raise ValueError("USER_ID and USER_PASS environment variables must be set.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()

        try:
            print("Opening animesss.tv...")
            page.goto("https://animesss.tv/", wait_until="domcontentloaded", timeout=60000)

            # networkidle can hang forever on ad-heavy sites — cap it
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except PlaywrightTimeoutError:
                print("networkidle timed out — continuing anyway.")

            # Dismiss any cookie/ad overlays that might block clicks
            dismiss_overlays(page)

            print("Looking for login button...")
            login_button = None
            login_selectors = [
                'button:has-text("Войти")',
                'a:has-text("Войти")',
                '[class*="login"]:has-text("Войти")',
                'button:has-text("войти")',
                'text=Войти',
            ]
            for sel in login_selectors:
                try:
                    el = page.locator(sel).first
                    el.wait_for(state="visible", timeout=10000)
                    login_button = el
                    print(f"Found login button: {sel}")
                    break
                except PlaywrightTimeoutError:
                    continue

            if login_button is None:
                page.screenshot(path="error_screenshot.png")
                raise RuntimeError("Login button not found with any known selector.")

            print("Clicking login button...")
            safe_click(page, login_button)

            # Wait for the modal/form to appear
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except PlaywrightTimeoutError:
                pass
            time.sleep(1)

            # Dismiss any overlays that appeared after clicking
            dismiss_overlays(page)

            print("Waiting for credential fields...")
            field_selector = (
                'input[placeholder*="логин"], '
                'input[name*="login"], '
                'input[type="text"], '
                'input[name="username"]'
            )
            try:
                page.wait_for_selector(field_selector, timeout=30000)
            except PlaywrightTimeoutError:
                page.screenshot(path="error_screenshot.png")
                raise RuntimeError("Login form fields not found after clicking login button.")

            print("Entering credentials...")
            for sel in ['[placeholder*="логин"]', '[name*="login"]', 'input[name="username"]', 'input[type="text"]']:
                try:
                    field = page.locator(sel).first
                    if field.is_visible():
                        field.fill(username)
                        print(f"Filled username ({sel})")
                        break
                except Exception:
                    continue

            for sel in ['[placeholder*="пароль"]', '[name*="pass"]', 'input[name="password"]', 'input[type="password"]']:
                try:
                    field = page.locator(sel).first
                    if field.is_visible():
                        field.fill(password)
                        print(f"Filled password ({sel})")
                        break
                except Exception:
                    continue

            print("Submitting login form...")
            submit_selectors = [
                'button:has-text("ВОЙТИ НА САЙТ")',
                'button:has-text("Войти на сайт")',
                'button:has-text("Войти")',
                'button[type="submit"]',
                'input[type="submit"]',
            ]
            submitted = False
            for sel in submit_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible():
                        safe_click(page, btn)
                        submitted = True
                        print(f"Submitted via: {sel}")
                        break
                except Exception:
                    continue

            if not submitted:
                page.screenshot(path="error_screenshot.png")
                raise RuntimeError("Could not find or click the submit button.")

            try:
                page.wait_for_load_state("networkidle", timeout=30000)
            except PlaywrightTimeoutError:
                pass

            time.sleep(5)  # Stay a moment so the visit is logged
            print(f"Successfully logged in as {username}. Streak maintained!")

        except Exception as e:
            print(f"Error: {e}")
            try:
                page.screenshot(path="error_screenshot.png")
                print("Screenshot saved.")
            except Exception:
                pass
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    run_streak()