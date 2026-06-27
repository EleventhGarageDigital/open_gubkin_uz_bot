import logging
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from config import GOOGLE_SHEET_NAME, GOOGLE_CREDENTIALS_FILE

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    "Дата записи в системе",
    "ФИО",
    "Направление",
    "Категория",
    "Дата визита",
    "Время визита",
    "Telegram ID",
    "Telegram username",
]

_client = None
_sheet = None


def _get_client():
    global _client
    if _client is None:
        creds = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        _client = gspread.authorize(creds)
    return _client


def _get_sheet():
    """
    Получает (или создаёт) первый лист таблицы и гарантирует,
    что в первой строке есть заголовки.
    """
    global _sheet
    if _sheet is None:
        client = _get_client()
        spreadsheet = client.open(GOOGLE_SHEET_NAME)
        _sheet = spreadsheet.sheet1

        first_row = _sheet.row_values(1)
        if first_row != HEADERS:
            _sheet.clear()
            _sheet.append_row(HEADERS)
    return _sheet


def add_registration(
    full_name: str,
    direction_title: str,
    category: str,
    visit_date: str,
    visit_time: str,
    telegram_id: int,
    telegram_username: str | None,
) -> None:
    """Добавляет новую строку с записью абитуриента в Google Sheets."""
    sheet = _get_sheet()
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        full_name,
        direction_title,
        category,
        visit_date,
        visit_time,
        str(telegram_id),
        f"@{telegram_username}" if telegram_username else "—",
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")
    logger.info("Запись добавлена в Google Sheets: %s", full_name)
