import pyotp
from playwright.sync_api import sync_playwright

page = None
browser = None
playwright = None
stored_email = None
stored_password = None
stored_secret = None


def login(email, password):
    global page, browser, playwright, stored_email, stored_password
    stored_email = email
    stored_password = password

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://razerid.razer.com/account")

    # Accept cookies if needed
    try:
        page.wait_for_selector(".cky-consent-bar", timeout=8000)
        page.click(".cky-btn-accept")
    except:
        pass

    # Fill login form
    page.fill("#input-login-email", email)
    page.click("#input-login-password")
    page.eval_on_selector("#input-login-password", "el => el.removeAttribute('readonly')")
    page.fill("#input-login-password", password)
    page.click("#btn-log-in")
    page.wait_for_load_state("networkidle")

    print("Logged in. Redirecting to dashboard...")

    # Wait for dashboard
    page.wait_for_url("**/dashboard", timeout=20000)

    # Go to account page
    page.goto("https://razerid.razer.com/account")
    page.wait_for_load_state("networkidle")

    # Click on 2FA setup link
    page.wait_for_selector("#section-tfa")
    page.click("#section-tfa")
    print("Clicked 2FA link, waiting for OTP modal...")

    # Wait for OTP modal to appear
    page.wait_for_selector(".wrapper[role=dialog]", timeout=15000)
    print("OTP modal is open, waiting for code from user...")

    return True


def submit_email_otp_and_setup(code):
    global page, stored_secret, stored_email, stored_password
    
    try:
            # Fill OTP digits into modal
            inputs = page.query_selector_all(".input-group-otp input")
            if len(inputs) != 6:
                raise Exception("OTP fields not found")

            for i, digit in enumerate(code.strip()):
                inputs[i].fill(digit)

            # Submit OTP
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")
            print("Email OTP submitted, now at setup page.")

            # ---- Setup Authenticator ----
            page.wait_for_selector(".tfa-item", timeout=15000)
            page.click(".tfa-item")
            print("Selected Authenticator App")

            # Wait until the secret key container is visible
            page.wait_for_selector(".secret-key", state="attached")
            stored_secret = page.text_content(".secret-key").strip()
            print(f"Secret Key captured: {stored_secret}")

            # Click Next button
            page.click("#btn-next")
            print("Clicked Next after getting secret key")

            # Generate OTP with pyotp
            totp = pyotp.TOTP(stored_secret)
            otp_code = totp.now()
            print(f"Generated OTP: {otp_code}")

            # Fill OTP digits into inputs
            page.wait_for_selector(".input-group-otp input", timeout=10000)
            inputs = page.query_selector_all(".input-group-otp input")
            if len(inputs) != 6:
                raise Exception("Authenticator OTP fields not found")

            for i, digit in enumerate(otp_code):
                inputs[i].fill(digit)

            # Click Next after filling OTP
            page.click("#btn-next")
            print("Clicked Next after entering authenticator OTP")

            # Wait and click Finish
            try:
                page.wait_for_selector("#btn-finish", timeout=10000)
                page.click("#btn-finish")
                print("Setup Finished")
            except:
                print("Finish button not found, maybe already completed")

            # Return credentials & secret key
            return {
                "email": stored_email,
                "password": stored_password,
                "secret_key": stored_secret
            }
    finally:
        close()

def close():
    global browser, playwright
    if browser:
        browser.close()
        print("Browser closed.")
    if playwright:
        playwright.stop()
        print("Playwright stopped.")
