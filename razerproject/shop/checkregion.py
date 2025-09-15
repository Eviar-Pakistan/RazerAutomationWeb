import time, json
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs, unquote
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def get_region(email, password):
    global page, browser, playwright
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
    except Exception as e:
        close()
        return {"error": f"Failed to start browser: {str(e)}"}

    try:
        page.goto("https://gold.razer.com")
    except Exception as e:
        close()
        return {"error": f"Failed to load Razer Gold site: {str(e)}"}

    try:
        page.wait_for_selector(".cky-consent-bar", timeout=8000)
        page.click(".cky-btn-accept")
    except:
        close()
        pass  # Cookie banner might not appear, that's okay

    try:
        page.wait_for_selector("a[aria-label='Log in your razer id account']", timeout=10000)
        page.click("a[aria-label='Log in your razer id account']")
    except Exception as e:
        close()
        return {"error": f"Failed to find login button: {str(e)}"}

    try:
        page.wait_for_selector("#input-login-email", timeout=15000)
        page.fill("#input-login-email", email)
        page.click("#input-login-password")
        page.eval_on_selector("#input-login-password", "el => el.removeAttribute('readonly')")
        page.fill("#input-login-password", password)
        page.click("#btn-log-in")
    except Exception as e:
        close()
        return {"error": f"Failed during login: {str(e)}"}

    try:
        for _ in range(60):
            if "gold.razer.com" in page.url:
                break
            time.sleep(0.5)
        final_url = page.url
    except Exception as e:
        close()
        return {"error": f"Login redirect failed: {str(e)}"}

    try:
        parsed = urlparse(final_url)
        region = None
        if parsed.query:
            query_params = parse_qs(parsed.query)
            if "redirect" in query_params:
                redirect_url = unquote(query_params["redirect"][0])
                path_parts = urlparse(redirect_url).path.strip("/").split("/")
                if path_parts:
                    region = path_parts[0]
        else:
            path_parts = parsed.path.strip("/").split("/")
            if path_parts:
                region = path_parts[0]
        if not region:
            return {"error": "Region could not be extracted"}
        return {"region": region}
    except Exception as e:
        close()
        return {"error": f"Failed to extract region: {str(e)}"}
    finally:
        close()

def close():
    global browser, playwright
    if browser:
        browser.close()
    if playwright:
        playwright.stop()

