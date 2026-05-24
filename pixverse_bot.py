import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def get_accounts():
    """Dynamically fetches all accounts from environment variables."""
    accounts = []
    
    base_id = os.getenv("USER_ID")
    base_pass = os.getenv("USER_PASS")
    if base_id and base_pass:
        accounts.append((base_id, base_pass))
        
    i = 2
    while True:
        uid = os.getenv(f"USER_ID{i}")
        upass = os.getenv(f"USER_PASS{i}")
        if uid and upass:
            accounts.append((uid, upass))
            i += 1
        else:
            break 
            
    return accounts

def run_streak():
    accounts = get_accounts()
    target_url = "https://app.pixverse.ai/"

    if not accounts:
        raise ValueError("CRITICAL: No valid USER_ID and USER_PASS environment variables found.")

    print(f"[*] Loaded {len(accounts)} account(s) for the daily streak.")

    with sync_playwright() as p:
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

        for idx, (username, password) in enumerate(accounts):
            print(f"\n[--- Processing Account {idx + 1}/{len(accounts)}: {username} ---]")
            
            try:
                print(f"[*] Navigating to {target_url}...")
                page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except PlaywrightTimeoutError:
                    pass

                print("[*] Locating and clicking the 'Login' button...")
                login_trigger = page.locator('button:has-text("Login"), a:has-text("Login")').first
                
                try:
                    login_trigger.wait_for(state="visible", timeout=15000)
                    login_trigger.click(timeout=10000)
                except PlaywrightTimeoutError:
                    login_trigger.click(force=True)

                print("[*] Injecting secrets into the DOM...")
                
                email_input = page.get_by_placeholder("Email or Username").first
                password_input = page.get_by_placeholder("Password").first
                
                email_input.wait_for(state="visible", timeout=20000)
                
                email_input.click()
                email_input.fill(username)
                
                password_input.click()
                password_input.fill(password)

                print("[*] Submitting authentication payload...")
                submit_btn = page.locator('button:has-text("Login"), button[type="submit"]').last
                submit_btn.click(timeout=15000)

                try:
                    page.wait_for_load_state("networkidle", timeout=20000)
                except PlaywrightTimeoutError:
                    pass
                print("[*] Holding session open for 15 seconds to finalize streak registration...")
                page.wait_for_timeout(15000) 
                print(f"[✓] Streak successfully maintained for {username}.")

                if idx < len(accounts) - 1:
                    print(f"[*] Preparing for next account. Initiating logout...")
                    try:
                        avatar = page.locator('img[alt="User avatar"]').first
                        
                        print("[*] Hovering over profile avatar...")
                        avatar.hover(timeout=10000)
                        
                        logout_option = page.get_by_text("Logout", exact=True).last
                        logout_option.wait_for(state="visible", timeout=10000)
                        
                        print("[*] Clicking 'Logout'...")
                        logout_option.click(timeout=10000)
                        
                        page.wait_for_timeout(5000)
                        print("[✓] Logged out successfully.")
                        
                    except PlaywrightTimeoutError:
                        print("[!] UI Hover failed. Executing failsafe: clearing cookies.")
                        context.clear_cookies()
                        page.goto("about:blank") 

            except Exception as e:
                print(f"[✗] Workflow Terminated for {username} with Error: {e}")
                try:
                    page.screenshot(path=f"error_{username}.png", full_page=True)
                    print(f"[i] Diagnostic screenshot saved as error_{username}.png")
                except Exception:
                    pass

        print("\n[*] All accounts processed. Closing browser.")
        context.close()
        browser.close()

if __name__ == "__main__":
    run_streak()