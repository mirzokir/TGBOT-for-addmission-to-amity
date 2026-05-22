"""
settings.py — Runtime-editable bot settings.

All mutable config (exam dates, directions, payment amount, QR path, etc.)
lives here instead of in locales or hardcoded values. Admins update them
via Telegram commands; changes persist across restarts via JSON file.
"""

import json
import asyncio
import logging
import os
from copy import deepcopy
from datetime import datetime, date
from pathlib import Path

log = logging.getLogger(__name__)

SETTINGS_FILE = Path(os.getenv("SETTINGS_FILE", "bot_settings.json"))

# ──────────────────────────────────────────────
#  Default (factory) settings
# ──────────────────────────────────────────────
_DEFAULTS: dict = {
    "exam_dates": [
        "13.05.2026",
        "10.06.2026",
        "24.06.2026",
        "15.07.2026",
    ],
    "payment_amount": 200000,          # so'm
    "payment_amount_display": "200 000 so'm",
    "directions": [
        "IT",
        "Artificial Intelligence & Data Science",
        "Cybersecurity & Blockchain",
        "Business Administration",
        "Economics",
        "Tourism",
        "English Language",
    ],
    "payme_qr_path": "qrcode.png",
    # Editable instruction fragments (plain text / HTML)
    "payme_manual_extra": "",   # appended to the manual PayMe instruction
    "registration_open": True,  # False → bot refuses new registrations
}

# In-memory store
_settings: dict = {}
_lock = asyncio.Lock()


# ──────────────────────────────────────────────
#  Load / Save
# ──────────────────────────────────────────────

def _load_from_disk() -> dict:
    if SETTINGS_FILE.exists():
        try:
            raw = SETTINGS_FILE.read_text(encoding="utf-8")
            data = json.loads(raw)
            # Merge with defaults so new keys are always present
            merged = deepcopy(_DEFAULTS)
            merged.update(data)
            return merged
        except Exception as e:
            log.warning("Could not read settings file: %s — using defaults", e)
    return deepcopy(_DEFAULTS)


def _save_to_disk(data: dict) -> None:
    try:
        tmp = SETTINGS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(SETTINGS_FILE)
    except Exception as e:
        log.error("Could not save settings: %s", e)


def init_settings() -> None:
    """Call once at startup (sync)."""
    global _settings
    _settings = _load_from_disk()
    log.info("Settings loaded: %s", SETTINGS_FILE)


# ──────────────────────────────────────────────
#  Public getters  (sync — safe from any context)
# ──────────────────────────────────────────────

def get(key: str, default=None):
    return _settings.get(key, default)


def get_all_exam_dates() -> list[str]:
    return list(_settings.get("exam_dates", []))


def get_next_exam_date() -> str | None:
    """Return the nearest future (or today) exam date, DD.MM.YYYY format."""
    today = date.today()
    upcoming = []
    for ds in _settings.get("exam_dates", []):
        try:
            d = datetime.strptime(ds.strip(), "%d.%m.%Y").date()
            if d >= today:
                upcoming.append((d, ds.strip()))
        except ValueError:
            pass
    if not upcoming:
        return None
    upcoming.sort(key=lambda x: x[0])
    return upcoming[0][1]


def get_directions() -> list[str]:
    return list(_settings.get("directions", _DEFAULTS["directions"]))


def get_payment_amount_display() -> str:
    return _settings.get("payment_amount_display", "200 000 so'm")


def get_payme_qr_path() -> str:
    return _settings.get("payme_qr_path", "qrcode.png")


def is_registration_open() -> bool:
    return bool(_settings.get("registration_open", True))


# ──────────────────────────────────────────────
#  Public setters  (async — acquire lock before writing)
# ──────────────────────────────────────────────

async def set_exam_dates(dates: list[str]) -> None:
    async with _lock:
        _settings["exam_dates"] = dates
        _save_to_disk(_settings)


async def add_exam_date(ds: str) -> None:
    async with _lock:
        if ds not in _settings["exam_dates"]:
            _settings["exam_dates"].append(ds)
            _settings["exam_dates"].sort(
                key=lambda x: datetime.strptime(x, "%d.%m.%Y")
            )
        _save_to_disk(_settings)


async def remove_exam_date(ds: str) -> bool:
    async with _lock:
        if ds in _settings["exam_dates"]:
            _settings["exam_dates"].remove(ds)
            _save_to_disk(_settings)
            return True
        return False


async def set_payment_amount(amount: int) -> None:
    async with _lock:
        _settings["payment_amount"] = amount
        _settings["payment_amount_display"] = f"{amount:,}".replace(",", " ") + " so'm"
        _save_to_disk(_settings)


async def set_directions(dirs: list[str]) -> None:
    async with _lock:
        _settings["directions"] = dirs
        _save_to_disk(_settings)


async def set_payme_qr_path(path: str) -> None:
    async with _lock:
        _settings["payme_qr_path"] = path
        _save_to_disk(_settings)


async def set_registration_open(val: bool) -> None:
    async with _lock:
        _settings["registration_open"] = val
        _save_to_disk(_settings)


async def set_value(key: str, value) -> None:
    """Generic setter for any top-level key."""
    async with _lock:
        _settings[key] = value
        _save_to_disk(_settings)
