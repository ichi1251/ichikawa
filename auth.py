"""
TikTok authentication helper.

Run this script once to log in via browser and save cookies:
    python auth.py

Saved cookies are loaded automatically by the scraper on subsequent runs.
"""

import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from config import TIKTOK_LIVE_CENTER_URL, COOKIES_FILE


def save_cookies(cookies: list, path: str = COOKIES_FILE) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    print(f"Cookies saved to {path}")


def load_cookies(path: str = COOKIES_FILE) -> list:
    p = Path(path)
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def login_interactively() -> None:
    """Open a browser for the user to log in, then save cookies."""
    print("ブラウザが開きます。TikTokにログインしてください。")
    print("ログイン完了後、ブラウザを閉じると自動でCookieが保存されます。\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.tiktok.com/login")

        print("ログインが完了したらEnterを押してください...")
        input()

        cookies = context.cookies()
        save_cookies(cookies)
        browser.close()


def is_logged_in(page) -> bool:
    """Check if the current page session is authenticated."""
    return "tiktok.com" in page.url and page.locator("[data-e2e='header-avatar']").count() > 0


if __name__ == "__main__":
    login_interactively()
