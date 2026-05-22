from aiogram.fsm.state import State, StatesGroup


class Reg(StatesGroup):
    # Language selection
    language = State()

    # Basic info
    full_name = State()
    phone = State()
    age = State()
    education = State()
    direction = State()

    # Passport block
    passport_choice = State()
    passport_photo = State()
    passport_number = State()

    # Certificate block
    cert_type = State()

    # IELTS
    ielts_score = State()
    ielts_send_type = State()
    ielts_photo = State()
    ielts_id = State()

    # CEFR
    cefr_level = State()
    cefr_send_type = State()
    cefr_photo = State()
    cefr_id = State()

    # Other certificate
    other_name = State()
    other_score = State()
    other_send_type = State()
    other_photo = State()
    other_id = State()

    # Exam & contact
    exam_date = State()
    contact_time = State()
    email = State()
    payment = State()
    payment_qr_choice = State()   # QR or manual PayMe
    payment_receipt = State()

    # Summary & edit
    summary = State()
    edit_choice = State()
    edit_value = State()