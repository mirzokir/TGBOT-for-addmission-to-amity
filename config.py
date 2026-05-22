import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
DB_PATH: str = "registrations.db"

# Path to the PayMe QR code image (place qrcode.png next to bot.py)
PAYME_QR_PATH: str = os.getenv("PAYME_QR_PATH", "qrcode.png")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set in .env file")