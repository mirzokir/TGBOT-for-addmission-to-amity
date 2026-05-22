import re

MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB


def validate_full_name(text: str) -> bool:
    """At least 2 words, letters only (Latin, Cyrillic, apostrophes)."""
    text = text.strip()
    parts = text.split()
    if len(parts) < 2:
        return False
    return bool(re.match(r"^[A-Za-zА-Яа-яЁёʻʼ'\- ]{3,100}$", text))


def validate_email(text: str) -> bool:
    """Simple email format check."""
    s = text.strip()
    if len(s) > 120:
        return False
    return bool(re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", s))


def validate_phone(text: str) -> bool:
    """Uzbekistan format: +998XXXXXXXXX with valid operator prefix."""
    s = text.strip()
    if not re.match(r"^\+998\d{9}$", s):
        return False
    # Valid Uzbekistan operator codes (2-digit after +998):
    # 90, 91, 93, 94, 95, 97, 98, 99 — mobile
    # 33, 50, 55, 77, 88 — additional mobile
    # 71 — Tashkent landline (sometimes used)
    operator = s[4:6]
    valid_operators = {
        "90", "91", "93", "94", "95", "97", "98", "99",
        "33", "50", "55", "77", "88", "71",
    }
    return operator in valid_operators


def validate_age(text: str) -> tuple[bool, int]:
    """Integer in range [16, 35]. Returns (True, age) or (False, 0)."""
    try:
        age = int(text.strip())
        if 16 <= age <= 35:
            return True, age
        return False, 0
    except ValueError:
        return False, 0


def validate_passport_number(text: str) -> bool:
    """Format: AA1234567 — 2 uppercase letters + 7 digits."""
    return bool(re.match(r"^[A-Z]{2}[0-9]{7}$", text.strip().upper()))


def validate_ielts_score(text: str) -> tuple[bool, float]:
    """
    IELTS score: 0.0 – 9.0, step 0.5.
    Valid: 0.0, 0.5, 1.0, …, 9.0
    """
    try:
        score = float(text.strip().replace(",", "."))
        if not (0.0 <= score <= 9.0):
            return False, 0.0
        # step 0.5 check: score * 2 must be integer
        if abs(round(score * 2) - score * 2) > 1e-9:
            return False, 0.0
        return True, score
    except ValueError:
        return False, 0.0


def validate_ielts_id(text: str) -> bool:
    """Alphanumeric, 6–20 chars."""
    return bool(re.match(r"^[A-Za-z0-9]{6,20}$", text.strip()))


def validate_cefr_id(text: str) -> bool:
    """Alphanumeric, 5–20 chars."""
    return bool(re.match(r"^[A-Za-z0-9]{5,20}$", text.strip()))


def validate_other_cert_name(text: str) -> bool:
    """Minimum 3 chars."""
    return len(text.strip()) >= 3


def validate_other_cert_score(text: str) -> bool:
    """Non-empty."""
    return len(text.strip()) > 0


def validate_other_id(text: str) -> bool:
    """Alphanumeric, 5–25 chars."""
    return bool(re.match(r"^[A-Za-z0-9]{5,25}$", text.strip()))


def validate_photo_size(file_size: int | None) -> bool:
    """True if within 5 MB limit (None = unknown size → allow)."""
    if file_size is None:
        return True
    return file_size <= MAX_PHOTO_BYTES