"""
Google Sheets integration.

Uses OAuth2 (credentials.json) to write TikTok LIVE data
to the configured spreadsheet.
"""

import logging
from typing import Optional
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

from config import SPREADSHEET_ID, SHEET_NAME, GOOGLE_CREDENTIALS_FILE, HEADERS

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

TOKEN_FILE = "token.pickle"


def _get_client() -> gspread.Client:
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return gspread.authorize(creds)


def _get_or_create_sheet(client: gspread.Client) -> gspread.Worksheet:
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        worksheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=len(HEADERS))
        logger.info("Created new sheet: %s", SHEET_NAME)

    # Ensure headers exist in row 1
    existing = worksheet.row_values(1)
    if existing != HEADERS:
        worksheet.update("A1", [HEADERS])
        logger.info("Headers written to sheet.")

    return worksheet


def session_already_recorded(worksheet: gspread.Worksheet, date_str: str, live_name: str) -> bool:
    """Return True if this session (same date + name) is already in the sheet."""
    records = worksheet.get_all_records()
    for row in records:
        if str(row.get("日付", "")) == date_str and str(row.get("LIVE名", "")) == live_name:
            return True
    return False


def append_session(session: dict) -> None:
    """Append a single session dict as a new row in the spreadsheet."""
    client = _get_client()
    worksheet = _get_or_create_sheet(client)

    date_str = session.get("日付", "")
    live_name = session.get("LIVE名", "")

    if session_already_recorded(worksheet, date_str, live_name):
        logger.info("Session already recorded (%s %s), skipping.", date_str, live_name)
        return

    row = [session.get(col, "") for col in HEADERS]
    worksheet.append_row(row, value_input_option="USER_ENTERED")
    logger.info("Row appended: %s %s", date_str, live_name)


def append_sessions(sessions: list[dict]) -> int:
    """Append multiple session dicts. Returns count of rows actually written."""
    if not sessions:
        return 0

    client = _get_client()
    worksheet = _get_or_create_sheet(client)
    written = 0

    for session in sessions:
        date_str = session.get("日付", "")
        live_name = session.get("LIVE名", "")

        if session_already_recorded(worksheet, date_str, live_name):
            logger.info("Already recorded (%s %s), skipping.", date_str, live_name)
            continue

        row = [session.get(col, "") for col in HEADERS]
        worksheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info("Row appended: %s %s", date_str, live_name)
        written += 1

    return written
