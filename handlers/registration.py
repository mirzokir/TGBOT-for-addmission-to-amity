"""
handlers/registration.py
Full registration FSM for Amity University bot.
"""

import json
import html
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from states import Reg
from locales import t
from validators import (
    validate_full_name, validate_phone, validate_age, validate_email,
    validate_passport_number,
    validate_ielts_score, validate_ielts_id,
    validate_cefr_id,
    validate_other_cert_name, validate_other_cert_score, validate_other_id,
    validate_photo_size,
)
from keyboards import (
    lang_keyboard, phone_kb, back_kb, options_kb, remove_kb,
    exam_dates_kb, summary_kb, edit_fields_kb, passport_photo_kb,
)
from database import phone_exists, save_registration
from config import ADMIN_ID, PAYME_QR_PATH
import settings as bot_settings
from sheets import append_registration

log = logging.getLogger(__name__)
router = Router()


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════

async def get_lang(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("lang", "uz")


def _ht(s: object) -> str:
    """Escape user-controlled strings for Telegram HTML."""
    return html.escape(str(s) if s is not None else "", quote=False)


def _passport_file_ids(passport_data: str | None) -> list[str]:
    if not passport_data:
        return []
    raw = str(passport_data).strip()
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(x) for x in parsed if x]
        except json.JSONDecodeError:
            return []
    return [raw]


def _passport_summary_html(passport_type: str, passport_data: str | None, lang: str) -> str:
    if passport_type != "photo":
        return f"{_ht(t(lang, 'passport_type_number'))} {_ht(passport_data)}"
    ids = _passport_file_ids(passport_data)
    n = len(ids)
    if n <= 1:
        return _ht(t(lang, "passport_type_photo"))
    return _ht(t(lang, "passport_type_photo_multi").format(n=n))


def is_back(text: str | None, lang: str) -> bool:
    if not text:
        return False
    return text.strip() == t(lang, "back_btn")


def _parse_lang_from_text(raw: str) -> str | None:
    """Map free-text / short codes to lang code, or None."""
    s = raw.strip().lower().replace("ё", "е")
    if not s:
        return None
    if s in {"uz", "1"} or "o'zbek" in s or "ozbek" in s or "ўзбек" in s or "узбек" in s:
        return "uz"
    if s in {"ru", "2"} or "рус" in s:
        return "ru"
    if s in {"en", "3"} or "english" in s or "англ" in s or "ingliz" in s:
        return "en"
    return None


def _payment_options(lang: str) -> list[str]:
    raw = t(lang, "payment_options")
    return list(raw) if isinstance(raw, list) else []


def _direction_options() -> list[str]:
    """Get directions from runtime settings (admin-editable)."""
    return bot_settings.get_directions()


def _payment_code_from_choice(text: str, lang: str) -> str | None:
    opts = _payment_options(lang)
    if text not in opts:
        return None
    return ("payme", "onsite")[opts.index(text)]


def _payment_summary_label(data: dict, lang: str) -> str:
    pm = data.get("payment_method")
    if pm == "payme":
        return t(lang, "summary_payment_payme_short")
    if pm == "onsite":
        return t(lang, "summary_payment_onsite_short")
    return "—"


async def _after_payment_choice(message: Message, state: FSMContext, lang: str, code: str) -> None:
    await state.update_data(payment_method=code, payment_receipt_file_id=None)
    if code == "payme":
        # Ask user: QR code or manual?
        await state.set_state(Reg.payment_qr_choice)
        await message.answer(
            t(lang, "payment_qr_choice_ask"),
            parse_mode="HTML",
            reply_markup=options_kb(t(lang, "payment_qr_options"), lang),
        )
        return
    await show_summary(message, state, lang)


async def _send_payme_qr(message: Message, lang: str) -> None:
    """Send QR code photo + instruction text."""
    qr_path = bot_settings.get_payme_qr_path()
    try:
        qr_file = FSInputFile(qr_path)
        await message.answer_photo(
            qr_file,
            caption=t(lang, "payment_payme_qr_text"),
            parse_mode="HTML",
        )
    except Exception:
        # If QR file missing — just send text
        await message.answer(t(lang, "payment_payme_qr_text"), parse_mode="HTML")


# ─────────────────────────────────────────────
#  Build summary text
# ─────────────────────────────────────────────
def _cert_label(cert_data_str: str | None, lang: str) -> str:
    if not cert_data_str:
        return t(lang, "no_cert")
    try:
        c = json.loads(cert_data_str)
        ctype = c.get("type", "")
        if ctype == "ielts":
            score = c.get("score", "?")
            extra = "📷" if c.get("send_type") == "photo" else f"🆔 {c.get('id','')}"
            return f"IELTS {score} ({extra})"
        if ctype == "cefr":
            level = c.get("level", "?")
            extra = "📷" if c.get("send_type") == "photo" else f"🆔 {c.get('id','')}"
            return f"CEFR {level} ({extra})"
        if ctype == "other":
            name  = c.get("name", "?")
            score = c.get("score", "?")
            return f"{name}: {score}"
    except Exception:
        pass
    return "—"


async def build_summary(data: dict, lang: str) -> str:
    passport_type = data.get("passport_type", "")
    passport_data = data.get("passport_data", "")
    passport_str = _passport_summary_html(str(passport_type), str(passport_data) if passport_data else None, lang)

    cert_str = _ht(_cert_label(data.get("cert_data"), lang))

    lines = [
        t(lang, "summary_title"),
        "",
        f"{t(lang, 'summary_field_name')}: <b>{_ht(data.get('full_name', '—'))}</b>",
        f"{t(lang, 'summary_field_phone')}: <b>{_ht(data.get('phone', '—'))}</b>",
        f"{t(lang, 'summary_field_age')}: <b>{_ht(data.get('age', '—'))}</b>",
        f"{t(lang, 'summary_field_education')}: <b>{_ht(data.get('education', '—'))}</b>",
        f"{t(lang, 'summary_field_direction')}: <b>{_ht(data.get('direction', '—'))}</b>",
        f"{t(lang, 'summary_field_passport')}: <b>{passport_str}</b>",
        f"{t(lang, 'summary_field_cert')}: <b>{cert_str}</b>",
        f"{t(lang, 'summary_field_exam_date')}: <b>{_ht(data.get('exam_date', '—'))}</b>",
        f"{t(lang, 'summary_field_contact')}: <b>{_ht(data.get('contact_time', '—'))}</b>",
        f"{t(lang, 'summary_field_email')}: <b>{_ht(data.get('email', '—'))}</b>",
        f"{t(lang, 'summary_field_payment')}: <b>{_ht(_payment_summary_label(data, lang))}</b>",
    ]
    if data.get("payment_method") == "payme" and data.get("payment_receipt_file_id"):
        lines.append(
            f"{t(lang, 'summary_field_payment_receipt')}: "
            f"<b>{_ht(t(lang, 'summary_payment_receipt_ok'))}</b>"
        )
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  Show summary (from Message)
# ─────────────────────────────────────────────
async def show_summary(message: Message, state: FSMContext, lang: str) -> None:
    await state.set_state(Reg.summary)
    data = await state.get_data()
    text = await build_summary(data, lang)
    await message.answer(text, parse_mode="HTML", reply_markup=remove_kb())
    await message.answer("👇", reply_markup=summary_kb(lang))


# ─────────────────────────────────────────────
#  Admin notification
# ─────────────────────────────────────────────
async def notify_admin(bot: Bot, data: dict, reg_id: int,
                       user_id: int, username: str | None) -> None:
    lang = data.get("lang", "uz")
    passport_type = data.get("passport_type", "")
    passport_data = data.get("passport_data", "")

    if passport_type == "photo":
        ids = _passport_file_ids(str(passport_data) if passport_data else "")
        passport_str = _ht(t(lang, "passport_type_photo_multi").format(n=len(ids))) if len(ids) > 1 else _ht(t(lang, "passport_type_photo"))
    else:
        passport_str = f"{_ht(t(lang, 'passport_type_number'))} {_ht(passport_data)}"

    cert_str = _ht(_cert_label(data.get("cert_data"), lang))
    uname = f"@{username}" if username else "N/A"

    text = (
        f"🆕 <b>Yangi ro'yxatdan o'tish #{reg_id}</b>\n\n"
        f"👤 Ism: <b>{_ht(data.get('full_name'))}</b>\n"
        f"📱 Tel: <b>{_ht(data.get('phone'))}</b>\n"
        f"🎂 Yosh: <b>{_ht(data.get('age'))}</b>\n"
        f"🎓 Ta'lim: <b>{_ht(data.get('education'))}</b>\n"
        f"📚 Yo'nalish: <b>{_ht(data.get('direction'))}</b>\n"
        f"🪪 Pasport: <b>{passport_str}</b>\n"
        f"📜 Sertifikat: <b>{cert_str}</b>\n"
        f"📅 Imtihon: <b>{_ht(data.get('exam_date'))}</b>\n"
        f"⏰ Vaqt: <b>{_ht(data.get('contact_time'))}</b>\n"
        f"📧 Email: <b>{_ht(data.get('email'))}</b>\n"
        f"💳 To'lov: <b>{_ht(_payment_summary_label(data, lang))}</b>\n"
        f"🌐 Til: <b>{_ht(lang.upper())}</b>\n"
        f"👤 Telegram: {_ht(uname)}\n"
        f"🆔 User ID: <code>{user_id}</code>"
    )
    await bot.send_message(ADMIN_ID, text, parse_mode="HTML")

    if passport_type == "photo" and passport_data:
        ids = _passport_file_ids(str(passport_data))
        for i, fid in enumerate(ids, start=1):
            try:
                cap = f"🪪 Pasport rasmi ({i}/{len(ids)})"
                await bot.send_photo(ADMIN_ID, fid, caption=cap)
            except Exception as e:
                log.warning("Could not send passport photo %s to admin: %s", i, e)

    cert_raw = data.get("cert_data")
    if cert_raw:
        try:
            cert = json.loads(cert_raw)
            if cert.get("send_type") == "photo" and cert.get("file_id"):
                await bot.send_photo(
                    ADMIN_ID, cert["file_id"],
                    caption=f"📜 Sertifikat rasmi ({cert.get('type','').upper()})"
                )
        except Exception as e:
            log.warning("Could not send cert photo to admin: %s", e)

    if data.get("payment_method") == "payme" and data.get("payment_receipt_file_id"):
        try:
            await bot.send_photo(
                ADMIN_ID,
                data["payment_receipt_file_id"],
                caption="🧾 Payme to'lovi cheki",
            )
        except Exception as e:
            log.warning("Could not send payment receipt to admin: %s", e)


# ══════════════════════════════════════════════════════════
#  STEP 1 — LANGUAGE
# ══════════════════════════════════════════════════════════

@router.message(Reg.language)
async def msg_language(message: Message, state: FSMContext) -> None:
    """If user sends text on /start instead of inline buttons, respond (otherwise Telegram looks stuck)."""
    if message.text:
        lang_code = _parse_lang_from_text(message.text)
        if lang_code:
            await state.update_data(lang=lang_code, is_editing=False)
            await state.set_state(Reg.full_name)
            await message.answer(t(lang_code, "welcome"), parse_mode="HTML")
            await message.answer(
                t(lang_code, "full_name_ask"),
                parse_mode="HTML",
                reply_markup=back_kb(lang_code),
            )
            return
    await message.answer(
        t("uz", "choose_language"),
        reply_markup=lang_keyboard(),
    )


@router.callback_query(StateFilter(Reg.language), F.data.startswith("lang_"))
async def cb_language(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    lang = callback.data.split("_", 1)[1]          # "uz" | "ru" | "en"

    if not bot_settings.is_registration_open():
        await callback.message.edit_text(
            "⛔ Регистрация временно закрыта. Пожалуйста, попробуйте позже.\n"
            "Ro'yxatdan o'tish vaqtincha yopilgan. Keyinroq urinib ko'ring.\n"
            "Registration is temporarily closed. Please try again later."
        )
        await state.clear()
        return

    await state.update_data(lang=lang, is_editing=False)
    await state.set_state(Reg.full_name)

    await callback.message.edit_text(t(lang, "welcome"), parse_mode="HTML")
    await callback.message.answer(
        t(lang, "full_name_ask"),
        parse_mode="HTML",
        reply_markup=back_kb(lang),
    )


# ══════════════════════════════════════════════════════════
#  STEP 2 — FULL NAME
# ══════════════════════════════════════════════════════════

@router.message(Reg.full_name)
async def msg_full_name(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if message.text is None or not message.text.strip():
        await message.answer(t(lang, "text_reply_expected"))
        return

    if is_back(message.text, lang):
        # Back → language selection
        await state.set_state(Reg.language)
        await message.answer(
            t(lang, "choose_language"),
            reply_markup=lang_keyboard(),
        )
        return

    if not validate_full_name(message.text or ""):
        await message.answer(t(lang, "full_name_error"))
        return

    await state.update_data(full_name=(message.text or "").strip())
    await state.set_state(Reg.phone)
    await message.answer(t(lang, "phone_ask"), parse_mode="HTML", reply_markup=phone_kb(lang))


# ══════════════════════════════════════════════════════════
#  STEP 3 — PHONE
# ══════════════════════════════════════════════════════════

async def _process_phone(message: Message, state: FSMContext, lang: str, phone: str) -> None:
    if not validate_phone(phone):
        await message.answer(t(lang, "phone_error"))
        return

    if await phone_exists(phone):
        await message.answer(t(lang, "phone_duplicate"), parse_mode="HTML")
        return

    await state.update_data(phone=phone)
    await state.set_state(Reg.age)
    await message.answer(t(lang, "age_ask"), parse_mode="HTML", reply_markup=back_kb(lang))


@router.message(Reg.phone, F.content_type == ContentType.CONTACT)
async def msg_phone_contact(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    phone = message.contact.phone_number  # type: ignore[union-attr]
    if not phone.startswith("+"):
        phone = "+" + phone
    await _process_phone(message, state, lang, phone)


@router.message(Reg.phone, F.text)
async def msg_phone_text(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if is_back(message.text, lang):
        await state.set_state(Reg.full_name)
        await message.answer(
            t(lang, "full_name_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )
        return

    await _process_phone(message, state, lang, (message.text or "").strip())


@router.message(Reg.phone)
async def msg_phone_other(message: Message, state: FSMContext) -> None:
    """Contact and text are handled by dedicated handlers; guide other content types."""
    lang = await get_lang(state)
    await message.answer(t(lang, "text_reply_expected"))


# ══════════════════════════════════════════════════════════
#  STEP 4 — AGE
# ══════════════════════════════════════════════════════════

@router.message(Reg.age)
async def msg_age(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if message.text is None or not message.text.strip():
        await message.answer(t(lang, "text_reply_expected"))
        return

    if is_back(message.text, lang):
        await state.set_state(Reg.phone)
        await message.answer(t(lang, "phone_ask"), parse_mode="HTML", reply_markup=phone_kb(lang))
        return

    valid, age = validate_age(message.text or "")
    if not valid:
        await message.answer(t(lang, "age_error"))
        return

    await state.update_data(age=age)
    await state.set_state(Reg.education)
    await message.answer(
        t(lang, "education_ask"), parse_mode="HTML",
        reply_markup=options_kb(t(lang, "education_options"), lang),
    )


# ══════════════════════════════════════════════════════════
#  STEP 5 — EDUCATION
# ══════════════════════════════════════════════════════════

@router.message(Reg.education)
async def msg_education(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if message.text is None or not message.text.strip():
        await message.answer(t(lang, "text_reply_expected"))
        return

    if is_back(message.text, lang):
        await state.set_state(Reg.age)
        await message.answer(t(lang, "age_ask"), parse_mode="HTML", reply_markup=back_kb(lang))
        return

    opts = t(lang, "education_options")
    if message.text not in opts:
        await message.answer(
            t(lang, "education_ask"), parse_mode="HTML",
            reply_markup=options_kb(opts, lang),
        )
        return

    await state.update_data(education=message.text)
    await state.set_state(Reg.direction)
    await message.answer(
        t(lang, "direction_ask"), parse_mode="HTML",
        reply_markup=options_kb(_direction_options(), lang),
    )


# ══════════════════════════════════════════════════════════
#  STEP 6 — DIRECTION
# ══════════════════════════════════════════════════════════

@router.message(Reg.direction)
async def msg_direction(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if message.text is None or not message.text.strip():
        await message.answer(t(lang, "text_reply_expected"))
        return

    if is_back(message.text, lang):
        await state.set_state(Reg.education)
        await message.answer(
            t(lang, "education_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "education_options"), lang),
        )
        return

    opts = _direction_options()
    if message.text not in opts:
        await message.answer(
            t(lang, "direction_ask"), parse_mode="HTML",
            reply_markup=options_kb(opts, lang),
        )
        return

    await state.update_data(direction=message.text)
    await state.set_state(Reg.passport_choice)
    await message.answer(
        t(lang, "passport_choice_ask"), parse_mode="HTML",
        reply_markup=options_kb(t(lang, "passport_choice_options"), lang),
    )


# ══════════════════════════════════════════════════════════
#  STEP 7 — PASSPORT CHOICE
# ══════════════════════════════════════════════════════════

@router.message(Reg.passport_choice)
async def msg_passport_choice(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    data = await state.get_data()
    editing = data.get("is_editing", False)

    if is_back(message.text, lang):
        if editing:
            # Return to edit field chooser
            await state.set_state(Reg.edit_choice)
            await message.answer(
                t(lang, "edit_choose_field"), parse_mode="HTML",
                reply_markup=edit_fields_kb(lang),
            )
        else:
            await state.set_state(Reg.direction)
            await message.answer(
                t(lang, "direction_ask"), parse_mode="HTML",
                reply_markup=options_kb(_direction_options(), lang),
            )
        return

    opts = t(lang, "passport_choice_options")
    if message.text not in opts:
        await message.answer(
            t(lang, "passport_choice_ask"), parse_mode="HTML",
            reply_markup=options_kb(opts, lang),
        )
        return

    if message.text == opts[0]:  # photo
        await state.update_data(passport_type="photo", passport_photo_ids=[], passport_data="")
        await state.set_state(Reg.passport_photo)
        await message.answer(
            t(lang, "passport_photo_ask"), parse_mode="HTML", reply_markup=passport_photo_kb(lang)
        )
    else:  # number
        await state.update_data(passport_type="number")
        await state.set_state(Reg.passport_number)
        await message.answer(
            t(lang, "passport_number_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )


# ─────────────────────────────────────────────
#  7a — Passport photo
# ─────────────────────────────────────────────

@router.message(Reg.passport_photo)
async def msg_passport_photo(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    done_btn = t(lang, "passport_photo_done_btn")

    if is_back(message.text, lang):
        await state.update_data(passport_photo_ids=[], passport_data="")
        await state.set_state(Reg.passport_choice)
        await message.answer(
            t(lang, "passport_choice_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "passport_choice_options"), lang),
        )
        return

    if message.text and message.text.strip() == done_btn:
        data = await state.get_data()
        raw_ids = data.get("passport_photo_ids") or []
        ids = list(raw_ids) if isinstance(raw_ids, (list, tuple)) else []
        if not ids:
            await message.answer(t(lang, "passport_photo_need_one"))
            return
        await state.update_data(passport_data=json.dumps(ids), passport_photo_ids=[])
        await _after_passport(message, state, lang)
        return

    if not message.photo:
        await message.answer(t(lang, "passport_photo_error"))
        return

    photo = message.photo[-1]
    if not validate_photo_size(photo.file_size):
        await message.answer(t(lang, "passport_photo_error"))
        return

    data = await state.get_data()
    raw_ids = data.get("passport_photo_ids") or []
    ids = list(raw_ids) if isinstance(raw_ids, (list, tuple)) else []
    ids.append(photo.file_id)
    await state.update_data(passport_photo_ids=ids)
    count = len(ids)
    confirm_text = t(lang, "passport_photo_more")
    # Show running count to user so they know photos are accumulating
    await message.answer(
        f"✅ ({count}) {confirm_text}",
        parse_mode="HTML",
        reply_markup=passport_photo_kb(lang),
    )


# ─────────────────────────────────────────────
#  7b — Passport number
# ─────────────────────────────────────────────

@router.message(Reg.passport_number)
async def msg_passport_number(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if is_back(message.text, lang):
        await state.set_state(Reg.passport_choice)
        await message.answer(
            t(lang, "passport_choice_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "passport_choice_options"), lang),
        )
        return

    text = (message.text or "").strip().upper()
    if not validate_passport_number(text):
        await message.answer(t(lang, "passport_number_error"))
        return

    await state.update_data(passport_data=text)
    await _after_passport(message, state, lang)


async def _after_passport(message: Message, state: FSMContext, lang: str) -> None:
    """Route after passport is filled — to cert or back to summary if editing."""
    data = await state.get_data()
    if data.get("is_editing"):
        await state.update_data(is_editing=False)
        await show_summary(message, state, lang)
    else:
        await state.set_state(Reg.cert_type)
        await message.answer(
            t(lang, "cert_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_options"), lang),
        )


# ══════════════════════════════════════════════════════════
#  STEP 8 — CERTIFICATE TYPE
# ══════════════════════════════════════════════════════════

@router.message(Reg.cert_type)
async def msg_cert_type(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    data = await state.get_data()
    editing = data.get("is_editing", False)

    if is_back(message.text, lang):
        if editing:
            await state.set_state(Reg.edit_choice)
            await message.answer(
                t(lang, "edit_choose_field"), parse_mode="HTML",
                reply_markup=edit_fields_kb(lang),
            )
        else:
            # Back to passport step
            passport_type = data.get("passport_type", "number")
            if passport_type == "photo":
                await state.update_data(passport_photo_ids=[], passport_data="")
                await state.set_state(Reg.passport_photo)
                await message.answer(
                    t(lang, "passport_photo_ask"),
                    parse_mode="HTML",
                    reply_markup=passport_photo_kb(lang),
                )
            else:
                await state.set_state(Reg.passport_number)
                await message.answer(
                    t(lang, "passport_number_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
                )
        return

    opts = t(lang, "cert_options")
    if message.text not in opts:
        await message.answer(
            t(lang, "cert_ask"), parse_mode="HTML",
            reply_markup=options_kb(opts, lang),
        )
        return

    # Map display label → internal key
    cert_map = {opts[0]: "ielts", opts[1]: "cefr", opts[2]: "other", opts[3]: "none"}
    cert_type = cert_map[message.text]
    await state.update_data(cert_type=cert_type)

    if cert_type == "ielts":
        await state.set_state(Reg.ielts_score)
        await message.answer(
            t(lang, "ielts_score_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )
    elif cert_type == "cefr":
        await state.set_state(Reg.cefr_level)
        await message.answer(
            t(lang, "cefr_level_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cefr_options"), lang),
        )
    elif cert_type == "other":
        await state.set_state(Reg.other_name)
        await message.answer(
            t(lang, "other_name_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )
    else:  # none
        await state.update_data(cert_data=None)
        await _after_cert(message, state, lang)


# ─────────────────────────────────────────────
#  IELTS sub-flow
# ─────────────────────────────────────────────

@router.message(Reg.ielts_score)
async def msg_ielts_score(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.cert_type)
        await message.answer(
            t(lang, "cert_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_options"), lang),
        )
        return
    valid, score = validate_ielts_score(message.text or "")
    if not valid:
        await message.answer(t(lang, "ielts_score_error"))
        return
    # Format score as "6.0" / "6.5" — never "6" (avoids ambiguity in cert_data JSON)
    score_str = f"{score:.1f}"
    await state.update_data(ielts_score=score_str)
    await state.set_state(Reg.ielts_send_type)
    await message.answer(
        t(lang, "ielts_send_type_ask"), parse_mode="HTML",
        reply_markup=options_kb(t(lang, "cert_send_options"), lang),
    )


@router.message(Reg.ielts_send_type)
async def msg_ielts_send_type(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.ielts_score)
        await message.answer(
            t(lang, "ielts_score_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )
        return
    opts = t(lang, "cert_send_options")
    if message.text not in opts:
        await message.answer(
            t(lang, "ielts_send_type_ask"), parse_mode="HTML",
            reply_markup=options_kb(opts, lang),
        )
        return
    if message.text == opts[0]:
        await state.update_data(ielts_send_type="photo")
        await state.set_state(Reg.ielts_photo)
        await message.answer(t(lang, "ielts_photo_ask"), reply_markup=back_kb(lang))
    else:
        await state.update_data(ielts_send_type="id")
        await state.set_state(Reg.ielts_id)
        await message.answer(
            t(lang, "ielts_id_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )


@router.message(Reg.ielts_photo)
async def msg_ielts_photo(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.ielts_send_type)
        await message.answer(
            t(lang, "ielts_send_type_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_send_options"), lang),
        )
        return
    if not message.photo:
        await message.answer(t(lang, "photo_error"))
        return
    photo = message.photo[-1]
    if not validate_photo_size(photo.file_size):
        await message.answer(t(lang, "photo_error"))
        return
    data = await state.get_data()
    cert_data = json.dumps({"type": "ielts", "score": data.get("ielts_score"),
                             "send_type": "photo", "file_id": photo.file_id})
    await state.update_data(cert_data=cert_data)
    await message.answer(t(lang, "photo_upload_ok"), parse_mode="HTML")
    await _after_cert(message, state, lang)


@router.message(Reg.ielts_id)
async def msg_ielts_id(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.ielts_send_type)
        await message.answer(
            t(lang, "ielts_send_type_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_send_options"), lang),
        )
        return
    text = (message.text or "").strip()
    if not validate_ielts_id(text):
        await message.answer(t(lang, "ielts_id_error"))
        return
    data = await state.get_data()
    cert_data = json.dumps({"type": "ielts", "score": data.get("ielts_score"),
                             "send_type": "id", "id": text})
    await state.update_data(cert_data=cert_data)
    await _after_cert(message, state, lang)


# ─────────────────────────────────────────────
#  CEFR sub-flow
# ─────────────────────────────────────────────

@router.message(Reg.cefr_level)
async def msg_cefr_level(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.cert_type)
        await message.answer(
            t(lang, "cert_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_options"), lang),
        )
        return
    opts = t(lang, "cefr_options")
    if message.text not in opts:
        await message.answer(
            t(lang, "cefr_level_ask"), parse_mode="HTML",
            reply_markup=options_kb(opts, lang),
        )
        return
    await state.update_data(cefr_level=message.text)
    await state.set_state(Reg.cefr_send_type)
    await message.answer(
        t(lang, "cefr_send_type_ask"), parse_mode="HTML",
        reply_markup=options_kb(t(lang, "cert_send_options"), lang),
    )


@router.message(Reg.cefr_send_type)
async def msg_cefr_send_type(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.cefr_level)
        await message.answer(
            t(lang, "cefr_level_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cefr_options"), lang),
        )
        return
    opts = t(lang, "cert_send_options")
    if message.text not in opts:
        await message.answer(
            t(lang, "cefr_send_type_ask"), parse_mode="HTML",
            reply_markup=options_kb(opts, lang),
        )
        return
    if message.text == opts[0]:
        await state.update_data(cefr_send_type="photo")
        await state.set_state(Reg.cefr_photo)
        await message.answer(t(lang, "cefr_photo_ask"), reply_markup=back_kb(lang))
    else:
        await state.update_data(cefr_send_type="id")
        await state.set_state(Reg.cefr_id)
        await message.answer(
            t(lang, "cefr_id_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )


@router.message(Reg.cefr_photo)
async def msg_cefr_photo(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.cefr_send_type)
        await message.answer(
            t(lang, "cefr_send_type_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_send_options"), lang),
        )
        return
    if not message.photo:
        await message.answer(t(lang, "photo_error"))
        return
    photo = message.photo[-1]
    if not validate_photo_size(photo.file_size):
        await message.answer(t(lang, "photo_error"))
        return
    data = await state.get_data()
    cert_data = json.dumps({"type": "cefr", "level": data.get("cefr_level"),
                             "send_type": "photo", "file_id": photo.file_id})
    await state.update_data(cert_data=cert_data)
    await message.answer(t(lang, "photo_upload_ok"), parse_mode="HTML")
    await _after_cert(message, state, lang)


@router.message(Reg.cefr_id)
async def msg_cefr_id(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.cefr_send_type)
        await message.answer(
            t(lang, "cefr_send_type_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_send_options"), lang),
        )
        return
    text = (message.text or "").strip()
    if not validate_cefr_id(text):
        await message.answer(t(lang, "cefr_id_error"))
        return
    data = await state.get_data()
    cert_data = json.dumps({"type": "cefr", "level": data.get("cefr_level"),
                             "send_type": "id", "id": text})
    await state.update_data(cert_data=cert_data)
    await _after_cert(message, state, lang)


# ─────────────────────────────────────────────
#  Other certificate sub-flow
# ─────────────────────────────────────────────

@router.message(Reg.other_name)
async def msg_other_name(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.cert_type)
        await message.answer(
            t(lang, "cert_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_options"), lang),
        )
        return
    text = (message.text or "").strip()
    if not validate_other_cert_name(text):
        await message.answer(t(lang, "other_name_error"))
        return
    await state.update_data(other_name=text)
    await state.set_state(Reg.other_score)
    await message.answer(
        t(lang, "other_score_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
    )


@router.message(Reg.other_score)
async def msg_other_score(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.other_name)
        await message.answer(
            t(lang, "other_name_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )
        return
    text = (message.text or "").strip()
    if not validate_other_cert_score(text):
        await message.answer(t(lang, "other_score_error"))
        return
    await state.update_data(other_score=text)
    await state.set_state(Reg.other_send_type)
    await message.answer(
        t(lang, "other_send_type_ask"), parse_mode="HTML",
        reply_markup=options_kb(t(lang, "cert_send_options"), lang),
    )


@router.message(Reg.other_send_type)
async def msg_other_send_type(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.other_score)
        await message.answer(
            t(lang, "other_score_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )
        return
    opts = t(lang, "cert_send_options")
    if message.text not in opts:
        await message.answer(
            t(lang, "other_send_type_ask"), parse_mode="HTML",
            reply_markup=options_kb(opts, lang),
        )
        return
    if message.text == opts[0]:
        await state.update_data(other_send_type="photo")
        await state.set_state(Reg.other_photo)
        await message.answer(t(lang, "other_photo_ask"), reply_markup=back_kb(lang))
    else:
        await state.update_data(other_send_type="id")
        await state.set_state(Reg.other_id)
        await message.answer(
            t(lang, "other_id_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )


@router.message(Reg.other_photo)
async def msg_other_photo(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.other_send_type)
        await message.answer(
            t(lang, "other_send_type_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_send_options"), lang),
        )
        return
    if not message.photo:
        await message.answer(t(lang, "photo_error"))
        return
    photo = message.photo[-1]
    if not validate_photo_size(photo.file_size):
        await message.answer(t(lang, "photo_error"))
        return
    data = await state.get_data()
    cert_data = json.dumps({"type": "other", "name": data.get("other_name"),
                             "score": data.get("other_score"),
                             "send_type": "photo", "file_id": photo.file_id})
    await state.update_data(cert_data=cert_data)
    await message.answer(t(lang, "photo_upload_ok"), parse_mode="HTML")
    await _after_cert(message, state, lang)


@router.message(Reg.other_id)
async def msg_other_id(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    if is_back(message.text, lang):
        await state.set_state(Reg.other_send_type)
        await message.answer(
            t(lang, "other_send_type_ask"), parse_mode="HTML",
            reply_markup=options_kb(t(lang, "cert_send_options"), lang),
        )
        return
    text = (message.text or "").strip()
    if not validate_other_id(text):
        await message.answer(t(lang, "other_id_error"))
        return
    data = await state.get_data()
    cert_data = json.dumps({"type": "other", "name": data.get("other_name"),
                             "score": data.get("other_score"),
                             "send_type": "id", "id": text})
    await state.update_data(cert_data=cert_data)
    await _after_cert(message, state, lang)


async def _after_cert(message: Message, state: FSMContext, lang: str) -> None:
    """Route after cert block — to exam date or back to summary if editing."""
    data = await state.get_data()
    if data.get("is_editing"):
        await state.update_data(is_editing=False)
        await show_summary(message, state, lang)
    else:
        await state.set_state(Reg.exam_date)
        await message.answer(
            t(lang, "exam_date_ask"), parse_mode="HTML", reply_markup=remove_kb()
        )
        await message.answer("👇", reply_markup=exam_dates_kb(lang))


# ══════════════════════════════════════════════════════════
#  STEP 9 — EXAM DATE (inline keyboard)
# ══════════════════════════════════════════════════════════

@router.callback_query(
    StateFilter(Reg.exam_date, Reg.edit_value),
    F.data.startswith("exam_"),
)
async def cb_exam_date(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    lang = await get_lang(state)
    date = callback.data[5:]                  # "13.05.2026"

    await state.update_data(exam_date=date)
    await callback.message.edit_text(f"📅 {date} ✅")

    current_state = await state.get_state()

    if current_state == Reg.edit_value.state:
        await state.update_data(is_editing=False)
        await show_summary(callback.message, state, lang)
    else:
        await state.set_state(Reg.contact_time)
        await callback.message.answer(
            t(lang, "contact_time_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )


# ══════════════════════════════════════════════════════════
#  STEP 10 — CONTACT TIME
# ══════════════════════════════════════════════════════════

@router.message(Reg.contact_time)
async def msg_contact_time(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if message.text is not None and is_back(message.text, lang):
        await state.set_state(Reg.exam_date)
        await message.answer(
            t(lang, "exam_date_ask"), parse_mode="HTML", reply_markup=remove_kb()
        )
        await message.answer("👇", reply_markup=exam_dates_kb(lang))
        return

    text = (message.text or "").strip()
    if message.text is None:
        await message.answer(t(lang, "text_reply_expected"))
        return
    if not text:
        await message.answer(t(lang, "contact_time_error"))
        return

    await state.update_data(contact_time=text)
    await state.set_state(Reg.email)
    await message.answer(t(lang, "email_ask"), parse_mode="HTML", reply_markup=back_kb(lang))


# ══════════════════════════════════════════════════════════
#  STEP 10b — EMAIL
# ══════════════════════════════════════════════════════════

@router.message(Reg.email)
async def msg_email(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if message.text is not None and is_back(message.text, lang):
        await state.set_state(Reg.contact_time)
        await message.answer(
            t(lang, "contact_time_ask"), parse_mode="HTML", reply_markup=back_kb(lang)
        )
        return

    text = (message.text or "").strip()
    if not message.text or not text:
        await message.answer(t(lang, "text_reply_expected"))
        return
    if not validate_email(text):
        await message.answer(t(lang, "email_error"))
        return

    await state.update_data(email=text.lower())
    await state.set_state(Reg.payment)
    await message.answer(
        t(lang, "payment_ask"),
        parse_mode="HTML",
        reply_markup=options_kb(_payment_options(lang), lang),
    )


# ══════════════════════════════════════════════════════════
#  STEP 10c — PAYMENT METHOD
# ══════════════════════════════════════════════════════════

@router.message(Reg.payment)
async def msg_payment(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if is_back(message.text, lang):
        await state.set_state(Reg.email)
        await message.answer(t(lang, "email_ask"), parse_mode="HTML", reply_markup=back_kb(lang))
        return

    text = (message.text or "").strip()
    code = _payment_code_from_choice(text, lang)
    if not code:
        await message.answer(
            t(lang, "payment_error"),
            parse_mode="HTML",
            reply_markup=options_kb(_payment_options(lang), lang),
        )
        return

    await _after_payment_choice(message, state, lang, code)


# ══════════════════════════════════════════════════════════
#  STEP 10d — PAYME RECEIPT PHOTO
# ══════════════════════════════════════════════════════════

@router.message(Reg.payment_receipt)
async def msg_payment_receipt(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if message.text is not None and is_back(message.text, lang):
        # Back to the QR/manual choice step
        await state.set_state(Reg.payment_qr_choice)
        await state.update_data(payment_receipt_file_id=None)
        await message.answer(
            t(lang, "payment_qr_choice_ask"),
            parse_mode="HTML",
            reply_markup=options_kb(t(lang, "payment_qr_options"), lang),
        )
        return

    if not message.photo:
        await message.answer(
            t(lang, "payment_receipt_error"),
            parse_mode="HTML",
            reply_markup=back_kb(lang),
        )
        return

    photo = message.photo[-1]
    if not validate_photo_size(photo.file_size):
        await message.answer(
            t(lang, "payment_receipt_error"),
            parse_mode="HTML",
            reply_markup=back_kb(lang),
        )
        return

    await state.update_data(payment_receipt_file_id=photo.file_id)
    await show_summary(message, state, lang)


# ══════════════════════════════════════════════════════════
#  STEP 10e — PAYME QR CHOICE (QR or manual)
# ══════════════════════════════════════════════════════════

@router.message(Reg.payment_qr_choice)
async def msg_payment_qr_choice(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)

    if is_back(message.text, lang):
        await state.set_state(Reg.payment)
        await state.update_data(payment_receipt_file_id=None)
        await message.answer(
            t(lang, "payment_ask"),
            parse_mode="HTML",
            reply_markup=options_kb(_payment_options(lang), lang),
        )
        return

    opts = t(lang, "payment_qr_options")
    if message.text not in opts:
        await message.answer(
            t(lang, "payment_qr_error"),
            parse_mode="HTML",
            reply_markup=options_kb(opts, lang),
        )
        return

    if message.text == opts[0]:
        # QR code variant
        await _send_payme_qr(message, lang)
    else:
        # Manual variant
        await message.answer(
            t(lang, "payment_payme_manual"),
            parse_mode="HTML",
            reply_markup=remove_kb(),
        )

    # After instruction — ask for receipt
    await state.set_state(Reg.payment_receipt)
    await message.answer(
        t(lang, "payment_receipt_ask"),
        parse_mode="HTML",
        reply_markup=back_kb(lang),
    )


# ══════════════════════════════════════════════════════════
#  STEP 11 — SUMMARY
# ══════════════════════════════════════════════════════════

@router.callback_query(Reg.summary, F.data == "sum_confirm")
async def cb_summary_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await callback.answer()
    lang = await get_lang(state)
    data = await state.get_data()

    db_data = {
        **data,
        "user_id":  callback.from_user.id,
        "username": callback.from_user.username,
    }
    reg_id = await save_registration(db_data)

    try:
        await notify_admin(
            bot, data, reg_id,
            callback.from_user.id, callback.from_user.username,
        )
    except Exception as e:
        log.error("Admin notification failed: %s", e)

    # Google Sheets export (non-blocking — errors don't affect user)
    try:
        await append_registration(
            reg_id, data,
            callback.from_user.id, callback.from_user.username,
        )
    except Exception as e:
        log.error("Google Sheets export failed: %s", e)

    await state.clear()
    await callback.message.edit_text("✅")
    await callback.message.answer(t(lang, "success"), parse_mode="HTML", reply_markup=remove_kb())


@router.callback_query(Reg.summary, F.data == "sum_edit")
async def cb_summary_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    lang = await get_lang(state)
    await state.set_state(Reg.edit_choice)
    await callback.message.edit_text(
        t(lang, "edit_choose_field"), parse_mode="HTML",
        reply_markup=edit_fields_kb(lang),
    )


# ══════════════════════════════════════════════════════════
#  EDIT FLOW
# ══════════════════════════════════════════════════════════

@router.callback_query(Reg.edit_choice, F.data.startswith("ef_"))
async def cb_edit_choice(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    lang = await get_lang(state)
    field = callback.data[3:]           # "name" | "phone" | "age" | ...

    if field == "back":
        # Back to summary
        await state.set_state(Reg.summary)
        data = await state.get_data()
        text = await build_summary(data, lang)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=summary_kb(lang))
        return

    await state.update_data(is_editing=True)

    # Fields that need their own multi-step sub-flow
    if field == "passport":
        await state.set_state(Reg.passport_choice)
        await callback.message.edit_text(t(lang, "passport_choice_ask"), parse_mode="HTML")
        await callback.message.answer(
            "👇",
            reply_markup=options_kb(t(lang, "passport_choice_options"), lang),
        )
        return

    if field == "cert":
        await state.set_state(Reg.cert_type)
        await callback.message.edit_text(t(lang, "cert_ask"), parse_mode="HTML")
        await callback.message.answer(
            "👇",
            reply_markup=options_kb(t(lang, "cert_options"), lang),
        )
        return

    if field == "exam_date":
        await state.set_state(Reg.edit_value)
        await callback.message.edit_text(t(lang, "exam_date_ask"), parse_mode="HTML")
        await callback.message.answer("👇", reply_markup=exam_dates_kb(lang))
        return

    # Simple text fields → go to edit_value state
    await state.set_state(Reg.edit_value)
    await state.update_data(editing_field=field)

    prompts = {
        "name":      (t(lang, "full_name_ask"),      back_kb(lang)),
        "phone":     (t(lang, "phone_ask"),           phone_kb(lang)),
        "age":       (t(lang, "age_ask"),             back_kb(lang)),
        "education": (t(lang, "education_ask"),       options_kb(t(lang, "education_options"), lang)),
        "direction": (t(lang, "direction_ask"),       options_kb(_direction_options(), lang)),
        "contact":   (t(lang, "contact_time_ask"),   back_kb(lang)),
        "email":     (t(lang, "email_ask"),           back_kb(lang)),
        "payment":   (t(lang, "payment_ask"),         options_kb(_payment_options(lang), lang)),
    }
    prompt_text, kb = prompts.get(field, ("?", back_kb(lang)))
    await callback.message.edit_text(prompt_text, parse_mode="HTML")
    await callback.message.answer("👇", reply_markup=kb)


@router.message(Reg.edit_value)
async def msg_edit_value(message: Message, state: FSMContext) -> None:
    lang = await get_lang(state)
    data = await state.get_data()
    field = data.get("editing_field", "")

    if is_back(message.text, lang):
        await state.set_state(Reg.edit_choice)
        await state.update_data(is_editing=False)
        await message.answer(
            t(lang, "edit_choose_field"), parse_mode="HTML",
            reply_markup=edit_fields_kb(lang),
        )
        return

    if field != "payment" and message.text is None:
        await message.answer(t(lang, "text_reply_expected"))
        return

    text = (message.text or "").strip()

    # ── Validate & save each editable field ──
    if field == "name":
        if not validate_full_name(text):
            await message.answer(t(lang, "full_name_error"))
            return
        await state.update_data(full_name=text)

    elif field == "phone":
        if not validate_phone(text):
            await message.answer(t(lang, "phone_error"))
            return
        old_phone = data.get("phone", "")
        if text != old_phone and await phone_exists(text):
            await message.answer(t(lang, "phone_duplicate"), parse_mode="HTML")
            return
        await state.update_data(phone=text)

    elif field == "age":
        valid, age = validate_age(text)
        if not valid:
            await message.answer(t(lang, "age_error"))
            return
        await state.update_data(age=age)

    elif field == "education":
        opts = t(lang, "education_options")
        if text not in opts:
            await message.answer(
                t(lang, "education_ask"), parse_mode="HTML",
                reply_markup=options_kb(opts, lang),
            )
            return
        await state.update_data(education=text)

    elif field == "direction":
        opts = _direction_options()
        if text not in opts:
            await message.answer(
                t(lang, "direction_ask"), parse_mode="HTML",
                reply_markup=options_kb(opts, lang),
            )
            return
        await state.update_data(direction=text)

    elif field == "contact":
        if not text:
            await message.answer(t(lang, "contact_time_error"))
            return
        await state.update_data(contact_time=text)

    elif field == "email":
        if not validate_email(text):
            await message.answer(t(lang, "email_error"))
            return
        await state.update_data(email=text.lower())

    elif field == "payment":
        code = _payment_code_from_choice(text, lang)
        if not code:
            await message.answer(
                t(lang, "payment_error"),
                parse_mode="HTML",
                reply_markup=options_kb(_payment_options(lang), lang),
            )
            return
        await state.update_data(is_editing=False)
        await _after_payment_choice(message, state, lang, code)
        return

    else:
        # Unknown field — just go back to summary
        pass

    await state.update_data(is_editing=False)
    await show_summary(message, state, lang)
