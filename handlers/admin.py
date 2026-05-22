"""
handlers/admin.py — Admin control panel via Telegram.

ВАЖНО: этот файл должен лежать в папке handlers/
Путь: handlers/admin.py

Доступ только для ADMIN_ID из .env
Открытие панели: /admin
"""

import logging
import os
from datetime import datetime
from collections import Counter

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from config import ADMIN_ID
import settings
from database import get_all_registrations

log = logging.getLogger(__name__)
router = Router()


# ══════════════════════════════════════════════════════════
#  FSM для multi-step ввода в админке
# ══════════════════════════════════════════════════════════

class AdminState(StatesGroup):
    waiting_add_date     = State()
    waiting_amount       = State()
    waiting_directions   = State()
    waiting_status_phone = State()
    waiting_status_value = State()
    waiting_qr_photo     = State()


# ══════════════════════════════════════════════════════════
#  Guard — только ADMIN_ID
# ══════════════════════════════════════════════════════════

async def _check_admin(message: Message) -> bool:
    return message.from_user is not None and message.from_user.id == ADMIN_ID


async def _check_admin_cb(callback: CallbackQuery) -> bool:
    if callback.from_user is None or callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Доступ запрещён", show_alert=True)
        return False
    return True


# ══════════════════════════════════════════════════════════
#  Inline keyboards
# ══════════════════════════════════════════════════════════

def _main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Даты экзаменов", callback_data="adm_dates"),
            InlineKeyboardButton(text="📊 Статистика",     callback_data="adm_stats"),
        ],
        [
            InlineKeyboardButton(text="📚 Направления",   callback_data="adm_dirs"),
            InlineKeyboardButton(text="💰 Сумма оплаты",  callback_data="adm_amount"),
        ],
        [
            InlineKeyboardButton(text="📋 Заявки",        callback_data="adm_list_0"),
            InlineKeyboardButton(text="🔄 Статус заявки", callback_data="adm_setstatus"),
        ],
        [
            InlineKeyboardButton(text="📷 Обновить QR",   callback_data="adm_qr"),
            InlineKeyboardButton(text="⚙️ Настройки",     callback_data="adm_cfg"),
        ],
    ])


def _dates_kb(dates: list[str], next_d: str | None) -> InlineKeyboardMarkup:
    rows = []
    for d in dates:
        mark = " ✅" if d == next_d else ""
        rows.append([
            InlineKeyboardButton(text=f"📅 {d}{mark}", callback_data="noop"),
            InlineKeyboardButton(text="🗑",            callback_data=f"adm_dd_{d}"),
        ])
    rows.append([InlineKeyboardButton(text="➕ Добавить дату", callback_data="adm_adddate")])
    rows.append([InlineKeyboardButton(text="◀️ Назад",         callback_data="adm_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _back_kb(target: str = "adm_main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=target)]
    ])


def _cfg_kb() -> InlineKeyboardMarkup:
    reg_open    = settings.is_registration_open()
    toggle_text = "🔒 Закрыть регистрацию" if reg_open else "✅ Открыть регистрацию"
    toggle_cb   = "adm_close" if reg_open else "adm_open"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=toggle_text,              callback_data=toggle_cb)],
        [InlineKeyboardButton(text="📷 Обновить QR-код",     callback_data="adm_qr")],
        [InlineKeyboardButton(text="💰 Изменить сумму",      callback_data="adm_amount")],
        [InlineKeyboardButton(text="📚 Изменить направления",callback_data="adm_dirs")],
        [InlineKeyboardButton(text="◀️ Назад",               callback_data="adm_main")],
    ])


def _dirs_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить список", callback_data="adm_setdirs")],
        [InlineKeyboardButton(text="◀️ Назад",           callback_data="adm_main")],
    ])


def _list_nav_kb(page: int, total: int, per_page: int = 5) -> InlineKeyboardMarkup:
    pages = max(1, (total + per_page - 1) // per_page)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"adm_list_{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"adm_list_{page+1}"))
    rows = [nav] if nav else []
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="adm_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _statuses_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Новая",            callback_data="adm_st_Новая")],
        [InlineKeyboardButton(text="🔍 На рассмотрении",  callback_data="adm_st_На рассмотрении")],
        [InlineKeyboardButton(text="✅ Одобрено",          callback_data="adm_st_Одобрено")],
        [InlineKeyboardButton(text="💳 Оплачено",          callback_data="adm_st_Оплачено")],
        [InlineKeyboardButton(text="❌ Отклонено",         callback_data="adm_st_Отклонено")],
        [InlineKeyboardButton(text="◀️ Назад",            callback_data="adm_main")],
    ])


# ══════════════════════════════════════════════════════════
#  Helper
# ══════════════════════════════════════════════════════════

def _reg_line(r: dict) -> str:
    pm      = r.get("payment_method", "")
    receipt = "✅" if r.get("payment_receipt_file_id") else "❌"
    pay_lbl = {"payme": f"Payme {receipt}", "onsite": "На месте"}.get(pm, pm or "—")
    return (
        f"👤 <b>{r.get('full_name','—')}</b>\n"
        f"📱 {r.get('phone','—')}  |  🎓 {r.get('direction','—')}\n"
        f"📅 {r.get('exam_date','—')}  |  💳 {pay_lbl}\n"
        f"📧 {r.get('email','—')}"
    )


async def _send_main_menu(target: Message | CallbackQuery, edit: bool = False) -> None:
    next_date = settings.get_next_exam_date() or "не задана"
    reg_open  = "✅ Открыта" if settings.is_registration_open() else "🔒 Закрыта"
    amount    = settings.get_payment_amount_display()
    text = (
        f"🛠 <b>Панель администратора</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📅 Ближайший экзамен: <b>{next_date}</b>\n"
        f"💰 Сумма оплаты: <b>{amount}</b>\n"
        f"🚦 Регистрация: <b>{reg_open}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"Выберите раздел:"
    )
    kb = _main_menu_kb()
    if isinstance(target, CallbackQuery):
        if edit:
            await target.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        else:
            await target.message.answer(text, parse_mode="HTML", reply_markup=kb)
    else:
        await target.answer(text, parse_mode="HTML", reply_markup=kb)


# ══════════════════════════════════════════════════════════
#  /admin — entry point
# ══════════════════════════════════════════════════════════

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    if not await _check_admin(message):
        return
    await state.clear()
    await _send_main_menu(message)


# ══════════════════════════════════════════════════════════
#  Главное меню (callback)
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_main")
async def cb_main(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    await state.clear()
    await _send_main_menu(callback, edit=True)


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()


# ══════════════════════════════════════════════════════════
#  Раздел: Даты экзаменов
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_dates")
async def cb_dates(callback: CallbackQuery) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    dates  = settings.get_all_exam_dates()
    next_d = settings.get_next_exam_date()
    body   = (
        "\n".join(f"• {d}" + (" ← ближайшая" if d == next_d else "") for d in dates)
        if dates else "Даты не заданы"
    )
    await callback.message.edit_text(
        f"📅 <b>Даты экзаменов</b>\n\n{body}\n\n"
        f"✅ — эта дата показывается пользователям\n"
        f"🗑 — удалить дату",
        parse_mode="HTML",
        reply_markup=_dates_kb(dates, next_d),
    )


@router.callback_query(F.data.startswith("adm_dd_"))
async def cb_delete_date(callback: CallbackQuery) -> None:
    if not await _check_admin_cb(callback):
        return
    ds      = callback.data[7:]
    removed = await settings.remove_exam_date(ds)
    await callback.answer(f"✅ Удалено: {ds}" if removed else "❌ Не найдено")
    dates  = settings.get_all_exam_dates()
    next_d = settings.get_next_exam_date()
    body   = (
        "\n".join(f"• {d}" + (" ← ближайшая" if d == next_d else "") for d in dates)
        if dates else "Даты не заданы"
    )
    await callback.message.edit_text(
        f"📅 <b>Даты экзаменов</b>\n\n{body}\n\n"
        f"✅ — эта дата показывается пользователям",
        parse_mode="HTML",
        reply_markup=_dates_kb(dates, next_d),
    )


@router.callback_query(F.data == "adm_adddate")
async def cb_adddate_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    await state.set_state(AdminState.waiting_add_date)
    await callback.message.edit_text(
        "📅 <b>Добавить дату экзамена</b>\n\n"
        "Введите дату в формате <code>DD.MM.YYYY</code>\n"
        "Пример: <code>20.08.2026</code>",
        parse_mode="HTML",
        reply_markup=_back_kb("adm_dates"),
    )


@router.message(AdminState.waiting_add_date)
async def msg_adddate(message: Message, state: FSMContext) -> None:
    if not await _check_admin(message):
        return
    ds = (message.text or "").strip()
    try:
        datetime.strptime(ds, "%d.%m.%Y")
    except ValueError:
        await message.answer(
            f"❌ Неверный формат: <code>{ds}</code>\n"
            f"Введите как <code>DD.MM.YYYY</code>",
            parse_mode="HTML",
        )
        return
    await settings.add_exam_date(ds)
    await state.clear()
    dates  = settings.get_all_exam_dates()
    next_d = settings.get_next_exam_date()
    body   = "\n".join(f"• {d}" + (" ← ближайшая" if d == next_d else "") for d in dates)
    await message.answer(
        f"✅ Дата <b>{ds}</b> добавлена!\n\n"
        f"📅 <b>Текущие даты:</b>\n{body}",
        parse_mode="HTML",
        reply_markup=_dates_kb(dates, next_d),
    )


# ══════════════════════════════════════════════════════════
#  Раздел: Статистика
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_stats")
async def cb_stats(callback: CallbackQuery) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer("⏳ Загружаю...")
    try:
        regs    = await get_all_registrations()
        total   = len(regs)
        payme   = sum(1 for r in regs if r.get("payment_method") == "payme")
        onsite  = sum(1 for r in regs if r.get("payment_method") == "onsite")
        receipt = sum(1 for r in regs if r.get("payment_receipt_file_id"))

        dirs  = Counter(r.get("direction", "—") for r in regs)
        dates = Counter(r.get("exam_date", "—") for r in regs)

        dir_lines  = "\n".join(f"  • {d}: <b>{c}</b>" for d, c in dirs.most_common(10))  or "  —"
        date_lines = "\n".join(f"  • {d}: <b>{c}</b>" for d, c in sorted(dates.items())) or "  —"

        sheet_id   = os.getenv("GOOGLE_SHEET_ID", "")
        sheets_btn = []
        if sheet_id:
            sheets_btn = [[InlineKeyboardButton(
                text="📊 Открыть Google Sheets",
                url=f"https://docs.google.com/spreadsheets/d/{sheet_id}",
            )]]

        kb = InlineKeyboardMarkup(inline_keyboard=sheets_btn + [
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_main")]
        ])

        await callback.message.edit_text(
            f"📊 <b>Статистика регистраций</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Всего заявок: <b>{total}</b>\n"
            f"💳 Payme: <b>{payme}</b>  |  чек загружен: <b>{receipt}</b>\n"
            f"🏢 На месте: <b>{onsite}</b>\n\n"
            f"<b>По направлениям:</b>\n{dir_lines}\n\n"
            f"<b>По датам экзамена:</b>\n{date_lines}",
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка: {e}", reply_markup=_back_kb("adm_main")
        )


# ══════════════════════════════════════════════════════════
#  Раздел: Список заявок (постраничный)
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("adm_list_"))
async def cb_list(callback: CallbackQuery) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    try:
        page = int(callback.data.split("_")[-1])
    except ValueError:
        page = 0

    per_page = 5
    regs     = await get_all_registrations()
    total    = len(regs)

    if total == 0:
        await callback.message.edit_text(
            "📋 Заявок пока нет.", reply_markup=_back_kb("adm_main")
        )
        return

    start = page * per_page
    end   = min(start + per_page, total)
    chunk = regs[start:end]

    lines = [f"📋 <b>Заявки {start+1}–{end} из {total}</b>\n"]
    for i, r in enumerate(chunk, start=start + 1):
        lines.append(f"<b>#{i}</b>  {_reg_line(r)}\n")

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=_list_nav_kb(page, total, per_page),
    )


# ══════════════════════════════════════════════════════════
#  Раздел: Обновить статус заявки
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_setstatus")
async def cb_setstatus_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    await state.set_state(AdminState.waiting_status_phone)
    await callback.message.edit_text(
        "🔄 <b>Обновить статус заявки</b>\n\n"
        "Введите номер телефона абитуриента:\n"
        "<code>+998901234567</code>",
        parse_mode="HTML",
        reply_markup=_back_kb("adm_main"),
    )


@router.message(AdminState.waiting_status_phone)
async def msg_status_phone(message: Message, state: FSMContext) -> None:
    if not await _check_admin(message):
        return
    phone = (message.text or "").strip()
    if not phone.startswith("+998"):
        await message.answer(
            "❌ Номер должен начинаться с <code>+998</code>\n"
            "Пример: <code>+998901234567</code>",
            parse_mode="HTML",
        )
        return

    regs  = await get_all_registrations()
    found = [r for r in regs if r.get("phone") == phone]
    if not found:
        await message.answer(
            f"❌ Абитуриент с номером <b>{phone}</b> не найден в базе данных.",
            parse_mode="HTML",
            reply_markup=_back_kb("adm_main"),
        )
        await state.clear()
        return

    r = found[0]
    await state.update_data(status_phone=phone)
    await state.set_state(AdminState.waiting_status_value)
    await message.answer(
        f"👤 Найден: <b>{r.get('full_name','—')}</b>\n"
        f"📱 {phone}\n"
        f"📅 Экзамен: {r.get('exam_date','—')}\n"
        f"🎓 Направление: {r.get('direction','—')}\n\n"
        f"Выберите новый статус:",
        parse_mode="HTML",
        reply_markup=_statuses_kb(),
    )


@router.callback_query(F.data.startswith("adm_st_"), AdminState.waiting_status_value)
async def cb_set_status_value(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _check_admin_cb(callback):
        return
    status = callback.data[7:]
    data   = await state.get_data()
    phone  = data.get("status_phone", "")
    await state.clear()

    sheets_note = ""
    try:
        from sheets import update_application_status, _is_configured
        if _is_configured():
            ok = await update_application_status(phone, status)
            sheets_note = "\n📊 Google Sheets обновлён ✅" if ok else "\n⚠️ Sheets не найдено"
        else:
            sheets_note = "\n⚠️ Google Sheets не настроен"
    except Exception as e:
        sheets_note = f"\n⚠️ Sheets ошибка: {e}"

    await callback.answer(f"✅ {status}")
    await callback.message.edit_text(
        f"✅ Статус заявки <b>{phone}</b>\n"
        f"Новый статус: <b>{status}</b>"
        f"{sheets_note}",
        parse_mode="HTML",
        reply_markup=_back_kb("adm_main"),
    )


# ══════════════════════════════════════════════════════════
#  Раздел: Направления обучения
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_dirs")
async def cb_dirs(callback: CallbackQuery) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    dirs  = settings.get_directions()
    lines = "\n".join(f"  {i+1}. {d}" for i, d in enumerate(dirs))
    await callback.message.edit_text(
        f"📚 <b>Направления обучения ({len(dirs)}):</b>\n\n{lines}",
        parse_mode="HTML",
        reply_markup=_dirs_kb(),
    )


@router.callback_query(F.data == "adm_setdirs")
async def cb_setdirs_start(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    await state.set_state(AdminState.waiting_directions)
    await callback.message.edit_text(
        "📚 <b>Изменить направления</b>\n\n"
        "Отправьте список — каждое направление с новой строки:\n\n"
        "<code>IT\n"
        "Business Administration\n"
        "Economics\n"
        "Tourism</code>",
        parse_mode="HTML",
        reply_markup=_back_kb("adm_dirs"),
    )


@router.message(AdminState.waiting_directions)
async def msg_directions(message: Message, state: FSMContext) -> None:
    if not await _check_admin(message):
        return
    lines = [ln.strip() for ln in (message.text or "").splitlines() if ln.strip()]
    if not lines:
        await message.answer("❌ Список пуст. Отправьте направления, каждое с новой строки.")
        return
    await settings.set_directions(lines)
    await state.clear()
    formatted = "\n".join(f"  {i+1}. {d}" for i, d in enumerate(lines))
    await message.answer(
        f"✅ Направления обновлены ({len(lines)} шт.):\n\n{formatted}",
        parse_mode="HTML",
        reply_markup=_back_kb("adm_main"),
    )


# ══════════════════════════════════════════════════════════
#  Раздел: Сумма оплаты
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_amount")
async def cb_amount(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    await state.set_state(AdminState.waiting_amount)
    current = settings.get_payment_amount_display()
    await callback.message.edit_text(
        f"💰 <b>Изменить сумму оплаты</b>\n\n"
        f"Текущая сумма: <b>{current}</b>\n\n"
        f"Введите новую сумму в сумах (только цифры):\n"
        f"Пример: <code>250000</code>",
        parse_mode="HTML",
        reply_markup=_back_kb("adm_main"),
    )


@router.message(AdminState.waiting_amount)
async def msg_amount(message: Message, state: FSMContext) -> None:
    if not await _check_admin(message):
        return
    raw = (message.text or "").strip().replace(" ", "").replace(",", "")
    try:
        amount = int(raw)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            "❌ Введите целое положительное число.\nПример: <code>250000</code>",
            parse_mode="HTML",
        )
        return
    await settings.set_payment_amount(amount)
    await state.clear()
    await message.answer(
        f"✅ Сумма оплаты обновлена: <b>{settings.get_payment_amount_display()}</b>",
        parse_mode="HTML",
        reply_markup=_back_kb("adm_main"),
    )


# ══════════════════════════════════════════════════════════
#  Раздел: QR-код
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_qr")
async def cb_qr(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    await state.set_state(AdminState.waiting_qr_photo)
    current = settings.get_payme_qr_path()
    await callback.message.edit_text(
        f"📷 <b>Обновить QR-код для Payme</b>\n\n"
        f"Текущий файл: <code>{current}</code>\n\n"
        f"Отправьте новое фото QR-кода в этот чат\n"
        f"(именно фото, не документ):",
        parse_mode="HTML",
        reply_markup=_back_kb("adm_cfg"),
    )


@router.message(AdminState.waiting_qr_photo)
async def msg_qr_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    if not await _check_admin(message):
        return
    if not message.photo:
        await message.answer(
            "❌ Отправьте фото QR-кода (не документ, а именно фото)."
        )
        return
    photo     = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    dest      = "qrcode.png"
    await bot.download_file(file_info.file_path, destination=dest)
    await settings.set_payme_qr_path(dest)
    await state.clear()
    await message.answer(
        f"✅ QR-код обновлён!\n"
        f"Сохранён как <code>{dest}</code>\n\n"
        f"Пользователи увидят новый QR при оплате через Payme.",
        parse_mode="HTML",
        reply_markup=_back_kb("adm_main"),
    )


# ══════════════════════════════════════════════════════════
#  Раздел: Настройки
# ══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_cfg")
async def cb_cfg(callback: CallbackQuery) -> None:
    if not await _check_admin_cb(callback):
        return
    await callback.answer()
    reg_open = settings.is_registration_open()
    status   = "✅ Открыта" if reg_open else "🔒 Закрыта"
    amount   = settings.get_payment_amount_display()
    qr       = settings.get_payme_qr_path()
    dirs_cnt = len(settings.get_directions())
    await callback.message.edit_text(
        f"⚙️ <b>Настройки бота</b>\n\n"
        f"🚦 Регистрация: <b>{status}</b>\n"
        f"💰 Сумма оплаты: <b>{amount}</b>\n"
        f"📚 Направлений: <b>{dirs_cnt}</b>\n"
        f"📷 QR-файл: <code>{qr}</code>",
        parse_mode="HTML",
        reply_markup=_cfg_kb(),
    )


@router.callback_query(F.data == "adm_open")
async def cb_open(callback: CallbackQuery) -> None:
    if not await _check_admin_cb(callback):
        return
    await settings.set_registration_open(True)
    await callback.answer("✅ Регистрация открыта!")
    await cb_cfg(callback)


@router.callback_query(F.data == "adm_close")
async def cb_close(callback: CallbackQuery) -> None:
    if not await _check_admin_cb(callback):
        return
    await settings.set_registration_open(False)
    await callback.answer("🔒 Регистрация закрыта!")
    await cb_cfg(callback)


# ══════════════════════════════════════════════════════════
#  Быстрые текстовые команды
# ══════════════════════════════════════════════════════════

@router.message(Command("admin_stats"))
async def cmd_stats(message: Message) -> None:
    if not await _check_admin(message):
        return
    regs    = await get_all_registrations()
    total   = len(regs)
    payme   = sum(1 for r in regs if r.get("payment_method") == "payme")
    onsite  = sum(1 for r in regs if r.get("payment_method") == "onsite")
    receipt = sum(1 for r in regs if r.get("payment_receipt_file_id"))
    dirs    = Counter(r.get("direction", "—") for r in regs)
    dates   = Counter(r.get("exam_date", "—") for r in regs)
    await message.answer(
        f"📊 Всего: <b>{total}</b> | Payme: <b>{payme}</b> (чек: {receipt}) | На месте: <b>{onsite}</b>\n\n"
        + "\n".join(f"• {d}: {c}" for d, c in dirs.most_common(10))
        + "\n\n"
        + "\n".join(f"• {d}: {c}" for d, c in sorted(dates.items())),
        parse_mode="HTML",
    )


@router.message(Command("admin_open"))
async def cmd_open(message: Message) -> None:
    if not await _check_admin(message):
        return
    await settings.set_registration_open(True)
    await message.answer("✅ Регистрация <b>открыта</b>.", parse_mode="HTML")


@router.message(Command("admin_close"))
async def cmd_close(message: Message) -> None:
    if not await _check_admin(message):
        return
    await settings.set_registration_open(False)
    await message.answer("🔒 Регистрация <b>закрыта</b>.", parse_mode="HTML")


@router.message(Command("admin_adddate"))
async def cmd_adddate(message: Message) -> None:
    if not await _check_admin(message):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /admin_adddate DD.MM.YYYY")
        return
    ds = parts[1].strip()
    try:
        datetime.strptime(ds, "%d.%m.%Y")
    except ValueError:
        await message.answer(f"❌ Неверный формат: <code>{ds}</code>", parse_mode="HTML")
        return
    await settings.add_exam_date(ds)
    await message.answer(
        f"✅ Добавлено: <b>{ds}</b>. Ближайшая: <b>{settings.get_next_exam_date()}</b>",
        parse_mode="HTML",
    )


@router.message(Command("admin_deldate"))
async def cmd_deldate(message: Message) -> None:
    if not await _check_admin(message):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /admin_deldate DD.MM.YYYY")
        return
    ds = parts[1].strip()
    if await settings.remove_exam_date(ds):
        next_d = settings.get_next_exam_date() or "нет"
        await message.answer(
            f"✅ Удалено: <b>{ds}</b>. Ближайшая: <b>{next_d}</b>",
            parse_mode="HTML",
        )
    else:
        await message.answer(f"❌ Дата <b>{ds}</b> не найдена.", parse_mode="HTML")