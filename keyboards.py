from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from locales import t
import settings as bot_settings


# ─────────────────────────────────────────────
#  Language selection (inline)
# ─────────────────────────────────────────────
def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇿 O'zbek",   callback_data="lang_uz"),
        InlineKeyboardButton(text="🇷🇺 Русский",  callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English",  callback_data="lang_en"),
    ]])


# ─────────────────────────────────────────────
#  Reply keyboards
# ─────────────────────────────────────────────
def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def back_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "back_btn"))]],
        resize_keyboard=True,
    )


def phone_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "phone_btn"), request_contact=True)],
            [KeyboardButton(text=t(lang, "back_btn"))],
        ],
        resize_keyboard=True,
    )


def options_kb(options: list[str], lang: str, with_back: bool = True) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=opt)] for opt in options]
    if with_back:
        rows.append([KeyboardButton(text=t(lang, "back_btn"))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def passport_photo_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "passport_photo_done_btn"))],
            [KeyboardButton(text=t(lang, "back_btn"))],
        ],
        resize_keyboard=True,
    )


# ─────────────────────────────────────────────
#  Exam date (inline) — shows only nearest upcoming date
# ─────────────────────────────────────────────
def exam_dates_kb(lang: str) -> InlineKeyboardMarkup:
    next_date = bot_settings.get_next_exam_date()
    if next_date:
        buttons = [[InlineKeyboardButton(
            text=f"📅 {next_date}",
            callback_data=f"exam_{next_date}"
        )]]
    else:
        # Fallback: show all dates from locales if settings empty
        raw_dates: list[str] = t(lang, "exam_dates_raw")
        buttons = [
            [InlineKeyboardButton(text=f"📅 {d}", callback_data=f"exam_{d}")]
            for d in raw_dates
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─────────────────────────────────────────────
#  Summary (inline)
# ─────────────────────────────────────────────
def summary_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "summary_confirm"), callback_data="sum_confirm")],
        [InlineKeyboardButton(text=t(lang, "summary_edit"),    callback_data="sum_edit")],
    ])


# ─────────────────────────────────────────────
#  Edit field chooser (inline)
# ─────────────────────────────────────────────
EDIT_FIELDS = [
    ("summary_field_name",      "ef_name"),
    ("summary_field_phone",     "ef_phone"),
    ("summary_field_age",       "ef_age"),
    ("summary_field_education", "ef_education"),
    ("summary_field_direction", "ef_direction"),
    ("summary_field_passport",  "ef_passport"),
    ("summary_field_cert",      "ef_cert"),
    ("summary_field_exam_date", "ef_exam_date"),
    ("summary_field_contact",   "ef_contact"),
    ("summary_field_email",     "ef_email"),
    ("summary_field_payment",   "ef_payment"),
]


def edit_fields_kb(lang: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=t(lang, key), callback_data=cb)]
        for key, cb in EDIT_FIELDS
    ]
    buttons.append([
        InlineKeyboardButton(text=t(lang, "edit_back_to_summary"), callback_data="ef_back")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
