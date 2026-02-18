"""Capture screenshots of the running app for the pitch deck."""
import os
from playwright.sync_api import sync_playwright

FRONTEND_URL = "http://localhost:5175"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS = [
    {"name": "dashboard_overview", "path": "/", "wait": 3000, "desc": "Dashboard - Visão Geral"},
    {"name": "dashboard_ml_prediction", "path": "/", "wait": 3000, "click_tab": "ML Predição", "desc": "Dashboard - ML Prediction Tab"},
    {"name": "athletes", "path": "/athletes", "wait": 2000, "desc": "Athletes List"},
    {"name": "load_monitoring", "path": "/load-monitoring", "wait": 3000, "desc": "Load Monitoring"},
    {"name": "game_analysis", "path": "/game-analysis", "wait": 2000, "desc": "Game Analysis"},
    {"name": "wellness", "path": "/wellness-test", "wait": 2000, "desc": "Wellness Test"},
]

def main():
    os.makedirs(os.path.join(OUTPUT_DIR, "screenshots"), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,  # Retina quality
        )
        page = context.new_page()

        for s in SCREENSHOTS:
            print(f"  Capturing: {s['desc']}...")
            page.goto(f"{FRONTEND_URL}{s['path']}")
            page.wait_for_timeout(s["wait"])

            # Click a tab if specified
            if "click_tab" in s:
                try:
                    tab = page.locator(f"button:has-text('{s['click_tab']}')").first
                    tab.click()
                    page.wait_for_timeout(1500)
                except Exception as e:
                    print(f"    Warning: Could not click tab '{s['click_tab']}': {e}")

            filepath = os.path.join(OUTPUT_DIR, "screenshots", f"{s['name']}.png")
            page.screenshot(path=filepath, full_page=False)
            print(f"    Saved: {filepath}")

        browser.close()
    print(f"\nDone! {len(SCREENSHOTS)} screenshots saved to {os.path.join(OUTPUT_DIR, 'screenshots')}")

if __name__ == "__main__":
    main()
