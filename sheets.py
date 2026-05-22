"""
sheets.py — Google Sheets integration for Amity University bot.

Setup:
1. Create a Google Service Account (console.cloud.google.com)
2. Enable Google Sheets API
3. Download credentials JSON → save as credentials.json next to bot.py
4. Create a Google Sheet, share it with the service account email (Editor)
5. Set GOOGLE_SHEET_ID in .env

The sheet has one header row and one row per registration.
Columns: see COLUMNS list below.
"""

import json
import logging
import os
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

log = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
WORKSHEET_NAME = os.getenv("GOOGLE_WORKSHEET_NAME", "Registrations")

# Column order (must match _row_from_data)
COLUMNS = [
    "№",
    "Дата регистрации",
    "Telegram ID",
    "Username",
    "Язык",
    "Имя и фамилия",
    "Телефон",
    "Возраст",
    "Образование",
    "Направление",
    "Тип паспорта",
    "Данные паспорта",
    "Сертификат",
    "Балл / уровень",
    "ID / файл сертификата",
    "Дата экзамена",
    "Время для связи",
    "Email",
    "Способ оплаты",
    "Статус оплаты",
    "Чек (file_id)",
    "Статус заявки",
    "Примечание",
]

_client: gspread.Client | None = None
_sheet: gspread.Worksheet | None = None


def _is_configured() -> bool:
    """Return True only if both credentials file and sheet ID are present."""
    import os
    if not SHEET_ID:
        return False
    if not os.path.exists(CREDENTIALS_FILE):
        return False
    # Quick sanity check — file must be valid JSON
    try:
        import json as _json
        with open(CREDENTIALS_FILE, encoding="utf-8") as f:
            data = _json.load(f)
        return "client_email" in data
    except Exception:
        return False


def _get_client() -> gspread.Client:
    global _client
    if _client is None:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client


def _get_sheet() -> gspread.Worksheet:
    global _sheet
    if _sheet is None:
        client = _get_client()
        spreadsheet = client.open_by_key(SHEET_ID)
        try:
            _sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            _sheet = spreadsheet.add_worksheet(
                title=WORKSHEET_NAME, rows=1000, cols=len(COLUMNS)
            )
            # Write header
            _sheet.append_row(COLUMNS, value_input_option="USER_ENTERED")
            # Style header row
            try:
                _sheet.format("A1:W1", {
                    "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8},
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                })
            except Exception:
                pass
    return _sheet


def _cert_details(cert_data_str: str | None) -> tuple[str, str, str]:
    """Returns (type_label, score_or_level, id_or_file)."""
    if not cert_data_str:
        return ("Нет", "", "")
    try:
        c = json.loads(cert_data_str)
        ctype = c.get("type", "")
        if ctype == "ielts":
            return ("IELTS", str(c.get("score", "")),
                    c.get("id", "") or c.get("file_id", ""))
        if ctype == "cefr":
            return ("CEFR", str(c.get("level", "")),
                    c.get("id", "") or c.get("file_id", ""))
        if ctype == "other":
            return (str(c.get("name", "Other")), str(c.get("score", "")),
                    c.get("id", "") or c.get("file_id", ""))
    except Exception:
        pass
    return ("—", "", "")


def _row_from_data(reg_id: int, data: dict, user_id: int, username: str | None) -> list:
    """Build a single sheet row from registration data."""
    cert_type, cert_score, cert_ref = _cert_details(data.get("cert_data"))
    uname = f"@{username}" if username else ""
    pm = data.get("payment_method", "")
    payment_display = {"payme": "Payme", "onsite": "На месте"}.get(pm, pm)
    receipt = data.get("payment_receipt_file_id", "")
    payment_status = "Оплачено (чек загружен)" if receipt else ("Ожидает" if pm == "payme" else "На месте")
    passport_type = data.get("passport_type", "")
    passport_data = data.get("passport_data", "")
    passport_type_display = {"photo": "Фото", "number": "Номер"}.get(passport_type, passport_type)

    return [
        reg_id,
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        user_id,
        uname,
        (data.get("lang") or "").upper(),
        data.get("full_name", ""),
        data.get("phone", ""),
        data.get("age", ""),
        data.get("education", ""),
        data.get("direction", ""),
        passport_type_display,
        str(passport_data) if passport_type == "number" else "(file_id в БД)",
        cert_type,
        cert_score,
        str(cert_ref)[:100] if cert_ref else "",
        data.get("exam_date", ""),
        data.get("contact_time", ""),
        data.get("email", ""),
        payment_display,
        payment_status,
        str(receipt)[:100] if receipt else "",
        "Новая",       # default application status
        "",            # notes — filled by admin
    ]


async def append_registration(reg_id: int, data: dict,
                               user_id: int, username: str | None) -> bool:
    """Append one registration row. Returns True on success."""
    if not _is_configured():
        log.debug("Sheets: not configured — skipping export for reg #%s", reg_id)
        return False
    try:
        row = _row_from_data(reg_id, data, user_id, username)
        sheet = _get_sheet()
        sheet.append_row(row, value_input_option="USER_ENTERED")
        log.info("Sheets: appended row for reg #%s", reg_id)
        return True
    except Exception as e:
        log.error("Sheets append failed for reg #%s: %s", reg_id, e)
        return False


async def update_application_status(phone: str, status: str, note: str = "") -> bool:
    """
    Find a row by phone number and update its status + note columns.
    Returns True if row was found and updated.
    """
    if not _is_configured():
        return False
    try:
        sheet = _get_sheet()
        # Phone is column G (index 7, 1-based)
        cell = sheet.find(phone, in_column=7)
        if cell is None:
            return False
        row_num = cell.row
        # Status = column V (22), Note = column W (23)
        if status:
            sheet.update_cell(row_num, 22, status)
        if note:
            sheet.update_cell(row_num, 23, note)
        return True
    except Exception as e:
        log.error("Sheets status update failed: %s", e)
        return False


def ensure_header() -> None:
    """Ensure the header row exists. Call at startup."""
    if not _is_configured():
        log.info("Sheets: credentials not configured — skipping (set GOOGLE_SHEET_ID and credentials.json to enable)")
        return
    try:
        sheet = _get_sheet()
        first = sheet.row_values(1)
        if first != COLUMNS:
            sheet.insert_row(COLUMNS, index=1, value_input_option="USER_ENTERED")
            log.info("Sheets: header row written")
    except Exception as e:
        log.warning("Sheets header check failed: %s", e)