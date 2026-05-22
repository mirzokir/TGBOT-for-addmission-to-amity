"""
bot.py — Amity University Tashkent Registration Bot
Entry point: python bot.py

АРХИТЕКТУРА РОУТЕРОВ (порядок важен):
  dp
  ├── admin_router   (handlers/admin.py)        — /admin и adm_* callbacks
  ├── reg_router     (handlers/registration.py) — FSM регистрации
  └── core_router    (этот файл)                — /start /cancel /help + fallback
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID
from database import init_db
from states import Reg
from locales import t
from keyboards import lang_keyboard, remove_kb
from handlers.registration import router as reg_router
from handlers.admin import router as admin_router
import settings as bot_settings
from sheets import ensure_header

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════
#  Core router — регистрируется ПОСЛЕДНИМ
# ══════════════════════════════════════════════════════════
core_router = Router()


@core_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Reg.language)
    await message.answer(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=lang_keyboard(),
    )


@core_router.message(Command("restart"))
async def cmd_restart(message: Message, state: FSMContext) -> None:
    await cmd_start(message, state)


@core_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current is None:
        await message.answer(
            "ℹ️ Нет активной регистрации.\nНачать: /start",
            reply_markup=remove_kb(),
        )
        return
    lang_data = await state.get_data()
    lang = lang_data.get("lang", "uz")
    await state.clear()
    await message.answer(t(lang, "cancelled"), reply_markup=remove_kb())


@core_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "ℹ️ <b>Amity University Bot</b>\n\n"
        "/start   — Ro'yxatdan o'tish / Регистрация\n"
        "/restart — Qayta boshlash / Перезапустить\n"
        "/cancel  — Bekor qilish / Отменить\n"
        "/help    — Yordam / Помощь\n"
        "/admin   — Панель администратора",
        parse_mode="HTML",
    )


# ─────────────────────────────────────────────
#  Fallback — НЕ перехватывает команды (/)
#  Срабатывает только на обычный текст без FSM-состояния
# ─────────────────────────────────────────────
@core_router.message(StateFilter(None), ~F.text.startswith("/"))
async def fallback(message: Message) -> None:
    await message.answer(
        "👋 Ro'yxatdan o'tish uchun /start\n"
        "Для регистрации нажмите /start\n"
        "To register press /start",
    )


# ══════════════════════════════════════════════════════════
#  Bot & dispatcher
#  ПОРЯДОК include_router критически важен:
#  admin → reg → core (core последним, иначе fallback глушит /admin)
# ══════════════════════════════════════════════════════════
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())
dp.include_router(admin_router)   # 1. admin — /admin и adm_* callbacks
dp.include_router(reg_router)     # 2. reg   — FSM регистрации
dp.include_router(core_router)    # 3. core  — /start /cancel /help + fallback


# ══════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════

async def main() -> None:
    bot_settings.init_settings()
    log.info("Settings loaded ✅")

    await init_db()
    log.info("Database initialised ✅")

    try:
        ensure_header()
        log.info("Google Sheets ready ✅")
    except Exception as e:
        log.warning("Google Sheets not available: %s", e)

    # Печатаем ADMIN_ID в лог чтобы легко сверить с реальным ID
    log.info("ADMIN_ID configured as: %s", ADMIN_ID)
    log.info("Bot is starting…")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
