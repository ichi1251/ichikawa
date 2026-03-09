"""
TikTok Live Center scraper.

Navigates to the Live Center analytics page and extracts per-session metrics.
"""

import re
import logging
from datetime import date, datetime
from typing import Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeout

from auth import load_cookies
from config import TIKTOK_LIVE_CENTER_URL, COOKIES_FILE

logger = logging.getLogger(__name__)

LIVE_CENTER_ANALYSIS_URL = "https://www.tiktok.com/tiktok-live-studio/web/#/analysis"


def _text(page: Page, selector: str, timeout: int = 5000) -> str:
    """Return stripped inner text of first matching element, or empty string."""
    try:
        el = page.locator(selector).first
        el.wait_for(timeout=timeout)
        return el.inner_text().strip()
    except PlaywrightTimeout:
        return ""


def _parse_number(value: str) -> str:
    """Remove commas and non-numeric chars, return as string for Sheets."""
    cleaned = re.sub(r"[^\d.]", "", value.replace(",", ""))
    return cleaned if cleaned else "0"


def _parse_percent(value: str) -> str:
    """Return numeric portion of a percentage string."""
    m = re.search(r"[\d.]+", value)
    return m.group() if m else "0"


def _build_context_with_cookies(playwright) -> tuple:
    """Launch browser and inject saved cookies."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    )
    cookies = load_cookies(COOKIES_FILE)
    if cookies:
        context.add_cookies(cookies)
    else:
        raise RuntimeError(
            f"Cookie file '{COOKIES_FILE}' not found. Run `python auth.py` first."
        )
    return browser, context


def scrape_latest_session() -> Optional[dict]:
    """
    Scrape the most recent LIVE session from TikTok Live Center.
    Returns a dict with all metrics, or None on failure.
    """
    with sync_playwright() as p:
        browser, context = _build_context_with_cookies(p)
        page = context.new_page()

        try:
            logger.info("Navigating to TikTok Live Center...")
            page.goto(LIVE_CENTER_ANALYSIS_URL, wait_until="networkidle", timeout=30000)

            # Handle potential redirect to login
            if "login" in page.url.lower():
                raise RuntimeError("Session expired. Run `python auth.py` to re-authenticate.")

            # Wait for the session list table to load
            page.wait_for_selector("table tbody tr", timeout=20000)

            # Click the first (latest) row to open details
            first_row = page.locator("table tbody tr").first
            row_cells = first_row.locator("td")

            live_title = row_cells.nth(0).inner_text().strip()
            live_date_raw = row_cells.nth(1).inner_text().strip()
            live_duration = row_cells.nth(2).inner_text().strip()
            total_views_row = _parse_number(row_cells.nth(3).inner_text().strip())
            new_followers_row = _parse_number(row_cells.nth(4).inner_text().strip())
            diamonds_row = _parse_number(row_cells.nth(5).inner_text().strip())

            first_row.click()
            page.wait_for_selector("[class*='metrics'], [class*='insight'], [class*='detail']", timeout=15000)

            data = _extract_detail_metrics(page)
            data.update({
                "日付": live_date_raw,
                "LIVE名": live_title,
                "LIVE時間": live_duration,
                "新規フォロワー": new_followers_row,
            })

            # Fallback for diamonds from row if detail not found
            if data.get("ダイヤモンド", "0") == "0" and diamonds_row != "0":
                data["ダイヤモンド"] = diamonds_row

            logger.info("Scraping complete: %s", data)
            return data

        except Exception as e:
            logger.error("Scraping failed: %s", e)
            # Save screenshot for debugging
            try:
                page.screenshot(path="debug_screenshot.png")
                logger.info("Debug screenshot saved to debug_screenshot.png")
            except Exception:
                pass
            raise
        finally:
            browser.close()


def _extract_detail_metrics(page: Page) -> dict:
    """
    Extract all metric cards from the detail panel.
    TikTok's class names are obfuscated; we match by Japanese label text.
    """
    data: dict = {}

    # Build a map: label_text -> sibling_value_text
    # Each metric card typically has a label span and a value span side by side
    cards = page.locator("[class*='metric'], [class*='item'], [class*='stat'], [class*='data']").all()

    # Fallback: scrape all text pairs on the page
    # Strategy: find all elements that contain Japanese metric labels
    label_map = {
        "視聴数": "視聴数",
        "ユニーク視聴者数": "ユニーク視聴者数",
        "アクティブな視聴者": "アクティブな視聴者",
        "最高同時視聴者数": "最高同時視聴者数",
        "平均視聴時間": "平均視聴時間",
        "コメント": "コメント",
        "いいね": "いいね",
        "シェア": "シェア",
        "ギフト贈呈者": "ギフト贈呈者",
        "LIVEのおすすめ": "LIVEのおすすめ(%)",
        "あなたの投稿": "あなたの投稿(%)",
        "フォロー中フィード": "フォロー中フィード(%)",
        "その他": "その他(%)",
        "推定額": "推定額(USD)",
        "ダイヤモンド": "ダイヤモンド",
        "このLIVEの%": "このLIVEの%",
    }

    # Use page.evaluate to extract label/value pairs from the DOM
    pairs = page.evaluate("""
        () => {
            const results = [];
            // Look for elements containing metric text alongside a number
            const allEls = document.querySelectorAll('*');
            for (const el of allEls) {
                const children = [...el.children];
                if (children.length >= 2) {
                    const texts = children.map(c => c.innerText ? c.innerText.trim() : '');
                    if (texts[0] && texts[1] && /^[\\d,.\u5206%]+$/.test(texts[1].replace(/\\s/,''))) {
                        results.push([texts[0], texts[1]]);
                    }
                }
            }
            return results;
        }
    """)

    # Parse the extracted pairs
    follower_section = False
    seen_avg = False

    for label, value in pairs:
        col = label_map.get(label)
        if col:
            clean = _parse_number(value) if "%" not in value else _parse_percent(value)
            if label == "平均視聴時間" and not seen_avg:
                data["平均視聴時間"] = value.strip()
                seen_avg = True
            elif label == "平均視聴時間" and seen_avg:
                data["フォロワー_平均視聴時間"] = value.strip()
            elif label == "ユニーク視聴者数" and "フォロワー_ユニーク視聴者数" not in data and "視聴数" in data:
                data["フォロワー_ユニーク視聴者数"] = clean
            elif label == "コメント" and "フォロワー_コメント投稿者" not in data and "コメント" in data:
                data["フォロワー_コメント投稿者"] = clean
            elif label == "ギフト贈呈者" and "フォロワー_ギフト贈呈者" not in data and "ギフト贈呈者" in data:
                data["フォロワー_ギフト贈呈者"] = clean
            elif label == "シェア" and "シェア_トラフィック(%)" in data:
                pass  # already set
            elif label == "シェア" and "エンゲージメント" in data:
                data["シェア_トラフィック(%)"] = _parse_percent(value)
            else:
                if col not in data:
                    data[col] = clean

    return data


def scrape_sessions_by_date(target_date: date) -> list[dict]:
    """
    Scrape all LIVE sessions matching target_date.
    Returns a list of session dicts (may be empty if no LIVE on that date).
    """
    with sync_playwright() as p:
        browser, context = _build_context_with_cookies(p)
        page = context.new_page()

        try:
            page.goto(LIVE_CENTER_ANALYSIS_URL, wait_until="networkidle", timeout=30000)
            if "login" in page.url.lower():
                raise RuntimeError("Session expired. Run `python auth.py` to re-authenticate.")

            page.wait_for_selector("table tbody tr", timeout=20000)
            rows = page.locator("table tbody tr").all()

            sessions = []
            for row in rows:
                cells = row.locator("td")
                date_text = cells.nth(1).inner_text().strip()
                # Match date portion (e.g. "2026年3月9日")
                m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_text)
                if m:
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    row_date = date(y, mo, d)
                    if row_date == target_date:
                        live_title = cells.nth(0).inner_text().strip()
                        live_duration = cells.nth(2).inner_text().strip()
                        new_followers = _parse_number(cells.nth(4).inner_text().strip())

                        row.click()
                        page.wait_for_timeout(2000)

                        detail = _extract_detail_metrics(page)
                        detail.update({
                            "日付": date_text,
                            "LIVE名": live_title,
                            "LIVE時間": live_duration,
                            "新規フォロワー": new_followers,
                        })
                        sessions.append(detail)

                        # Navigate back to list
                        page.go_back()
                        page.wait_for_selector("table tbody tr", timeout=15000)
                        rows = page.locator("table tbody tr").all()

            return sessions

        finally:
            browser.close()
