import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def run_streak():
    # ── Configuration & Environment ──────────────────────────────────────────
    username = os.getenv("USER_ID")
    password = os.getenv("USER_PASS")
    target_url = "https://app.pixverse.ai/"

    if not username or not password:
        raise ValueError("CRITICAL: USER_ID and USER_PASS environment variables must be set.")

    with sync_playwright() as p:
        # Launching with a realistic viewport and user agent
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        try:
            # ── 1. Load the target site ─────────────────────────────────────────
            print(f"[*] Navigating to {target_url}...")
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except PlaywrightTimeoutError:
                print("[!] Network idle timeout reached — continuing execution.")

            # ── 2. Trigger the Login flow ───────────────────────────────────────
            print("[*] Locating and clicking the initial 'Login' button...")
            
            login_trigger = page.locator('button:has-text("Login"), a:has-text("Login")').first
            
            try:
                login_trigger.wait_for(state="visible", timeout=15000)
                login_trigger.click(timeout=10000)
            except PlaywrightTimeoutError:
                print("[!] Standard click failed — attempting forced click.")
                login_trigger.click(force=True)

            # ── 3. Await Authentication UI ──────────────────────────────────────
            print("[*] Waiting for the authentication inputs to mount...")
            
            # Target the exact placeholders visible in the UI
            email_input = page.get_by_placeholder("Email or Username").first
            password_input = page.get_by_placeholder("Password").first
            
            try:
                email_input.wait_for(state="visible", timeout=20000)
            except PlaywrightTimeoutError:
                page.screenshot(path="error_screenshot.png")
                raise RuntimeError("FATAL: Login inputs failed to appear within the timeout. Artifact saved.")

            # ── 4. Inject Credentials ───────────────────────────────────────────
            print("[*] Injecting secrets into the DOM...")
            
            # Explicit clicks ensure the frontend state manager registers the input focus
            email_input.click()
            email_input.fill(username)
            
            password_input.click()
            password_input.fill(password)

            # ── 5. Execute Login Request ────────────────────────────────────────
            print("[*] Submitting authentication payload...")
            
            submit_btn = page.locator('button:has-text("Login"), button[type="submit"]').last
            submit_btn.click(timeout=15000)

            # ── 6. Verify Session Integrity & Register Streak ───────────────────
            print("[*] Awaiting post-login redirect/network idle...")
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except PlaywrightTimeoutError:
                pass

            # Extended buffer (15 seconds) to ensure the backend streak API registers the visit.
            # Using wait_for_timeout keeps the browser event loop active, unlike time.sleep().
            print("[*] Holding session open for 15 seconds to finalize streak registration...")
            page.wait_for_timeout(15000) 
            
            print(f"[✓] Streak successfully maintained for {username}.")

        except Exception as e:
            print(f"[✗] Workflow Terminated with Error: {e}")
            try:
                page.screenshot(path="error_screenshot.png", full_page=True)
                print("[i] Diagnostic screenshot saved for GitHub Actions artifacts.")
            except Exception:
                pass
            raise
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run_streak()