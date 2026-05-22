import json
import aiosqlite
from config import DB_PATH


# ─────────────────────────────────────────────
#  Schema
# ─────────────────────────────────────────────
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS registrations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    username      TEXT,
    lang          TEXT,
    full_name     TEXT,
    phone         TEXT UNIQUE,
    age           INTEGER,
    education     TEXT,
    direction     TEXT,
    passport_type TEXT,          -- 'photo' | 'number'
    passport_data TEXT,          -- file_id | JSON list of file_ids | passport number
    cert_type     TEXT,          -- 'ielts' | 'cefr' | 'other' | 'none'
    cert_data     TEXT,          -- JSON blob with cert details
    exam_date        TEXT,
    contact_time     TEXT,
    email            TEXT,
    payment_method   TEXT,       -- 'payme' | 'onsite'
    payment_receipt_file_id TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


async def _apply_pragmas(db: aiosqlite.Connection) -> None:
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA synchronous=NORMAL")
    await db.execute("PRAGMA busy_timeout=5000")


async def _migrate_registrations_columns(db: aiosqlite.Connection) -> None:
    cursor = await db.execute("PRAGMA table_info(registrations)")
    rows = await cursor.fetchall()
    colnames = {r[1] for r in rows}
    if "email" not in colnames:
        await db.execute("ALTER TABLE registrations ADD COLUMN email TEXT")
    if "payment_method" not in colnames:
        await db.execute("ALTER TABLE registrations ADD COLUMN payment_method TEXT")
    if "payment_receipt_file_id" not in colnames:
        await db.execute("ALTER TABLE registrations ADD COLUMN payment_receipt_file_id TEXT")


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
        await _apply_pragmas(db)
        await db.execute(CREATE_TABLE)
        await _migrate_registrations_columns(db)
        await db.commit()


# ─────────────────────────────────────────────
#  Queries
# ─────────────────────────────────────────────
async def phone_exists(phone: str) -> bool:
    """Return True if this phone number already has a registration."""
    async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
        await _apply_pragmas(db)
        cursor = await db.execute(
            "SELECT 1 FROM registrations WHERE phone = ?", (phone,)
        )
        row = await cursor.fetchone()
        return row is not None


async def save_registration(data: dict) -> int:
    """Insert a new registration row and return the new id."""
    cert_data = data.get("cert_data")
    if isinstance(cert_data, dict):
        cert_data = json.dumps(cert_data, ensure_ascii=False)

    async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
        await _apply_pragmas(db)
        cursor = await db.execute(
            """
            INSERT INTO registrations
                (user_id, username, lang, full_name, phone, age,
                 education, direction, passport_type, passport_data,
                 cert_type, cert_data, exam_date, contact_time,
                 email, payment_method, payment_receipt_file_id)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("user_id"),
                data.get("username"),
                data.get("lang"),
                data.get("full_name"),
                data.get("phone"),
                data.get("age"),
                data.get("education"),
                data.get("direction"),
                data.get("passport_type"),
                data.get("passport_data"),
                data.get("cert_type"),
                cert_data,
                data.get("exam_date"),
                data.get("contact_time"),
                data.get("email"),
                data.get("payment_method"),
                data.get("payment_receipt_file_id"),
            ),
        )
        await db.commit()
        return cursor.lastrowid or 0


async def get_all_registrations() -> list[dict]:
    """Fetch all rows (admin utility)."""
    async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
        await _apply_pragmas(db)
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM registrations ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
