from typing import Any

# ─────────────────────────────────────────────
#  All UI texts in three languages
# ─────────────────────────────────────────────
TEXTS: dict[str, dict[str, Any]] = {

    # ═══════════════════════════════════════════
    #  UZBEK
    # ═══════════════════════════════════════════
    "uz": {
        "choose_language": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "welcome": (
            "Assalomu alaykum! 👋\n\n"
            "Siz <b>Toshkent shahridagi xalqaro Amity universitetining</b> "
            "rasmiy telegram botidasiz.\n\n"
            "Hujjat topshirish uchun quyidagi ma'lumotlarni to'ldiring.\n\n"
            "⚠️ <b>Diqqat!</b> Barcha bosqichlar majburiy to'ldiriladi."
        ),

        # Full name
        "full_name_ask": (
            "👤 <b>Ism va familiyangizni kiriting</b>\n\n"
            "📋 Format: <code>Ism Familiya</code>\n"
            "📌 Misol: <code>Ali Valiyev</code>"
        ),
        "full_name_error": (
            "❌ Noto'g'ri format!\n"
            "• Faqat harflar\n"
            "• Kamida 2 ta so'z\n"
            "📌 Misol: Ali Valiyev"
        ),

        # Phone
        "phone_ask": (
            "📱 <b>Telefon raqamingizni yuboring</b>\n\n"
            "📋 Format: <code>+998901234567</code>\n\n"
            "👇 Pastdagi tugmani bosing yoki qo'lda kiriting:"
        ),
        "phone_btn": "📱 Raqamni ulashish",
        "phone_error": "❌ Noto'g'ri format!\n📌 Misol: +998901234567",
        "phone_duplicate": (
            "❌ <b>Bu telefon raqam allaqachon ro'yxatdan o'tgan!</b>\n\n"
            "Agar xato deb hisoblasangiz, biz bilan bog'laning:\n"
            "📞 +998 71 123-45-67\n"
            "🔄 Boshqa raqam bilan ro'yxatdan o'tish uchun raqam yuboring."
        ),

        # Age
        "age_ask": (
            "🎂 <b>Yoshingizni kiriting</b>\n\n"
            "📋 Format: <code>20</code>\n"
            "⚠️ Yosh oralig'i: 16 – 35"
        ),
        "age_error": "❌ Yosh 16 dan 35 gacha bo'lishi kerak!\n📌 Butun son kiriting. Misol: 20",

        # Education
        "education_ask": "🎓 <b>Ta'lim holatingizni tanlang:</b>",
        "education_options": [
            "🏫 Maktab o'quvchisi",
            "🏛 Litsey / kollej",
            "🎓 Universitet",
            "💼 Ishlayman",
            "📝 Boshqa",
        ],

        # Direction
        "direction_ask": "📚 <b>Qaysi yo'nalishga qiziqasiz?</b>",
        "direction_options": [
            "💻 IT",
            "🤖 Artificial Intelligence & Data Science",
            "🔐 Cybersecurity & Blockchain",
            "💼 Business Administration",
            "📊 Economics",
            "✈️ Tourism",
            "🇬🇧 English Language",
        ],

        # Passport
        "passport_choice_ask": "🪪 <b>Pasport ma'lumotini qanday yuborasiz?</b>",
        "passport_choice_options": ["📷 Rasm yuklash", "🔢 Raqam kiritish"],
        "passport_photo_ask": (
            "📸 <b>Pasport rasmlarini yuboring</b>\n\n"
            "Bir yoki bir nechta rasm yuborishingiz mumkin (har biri jpg/png, max 5 MB).\n"
            "Barcha rasmlarni yuborganingizdan keyin <b>«Tayyor»</b> tugmasini bosing."
        ),
        "passport_photo_done_btn": "✅ Tayyor — barcha rasmlar yuborildi",
        "passport_photo_need_one": "❌ Kamida bitta pasport rasmini yuboring.",
        "passport_photo_more": (
            "✅ Rasm qabul qilindi. Yana rasm yuborishingiz yoki «Tayyor» ni bosing."
        ),
        "passport_photo_error": "❌ Iltimos, rasm yuboring! (jpg/png, max 5MB)",
        "passport_number_ask": (
            "🔢 <b>Pasport seriya va raqamini kiriting</b>\n\n"
            "📋 Format: <code>AA1234567</code>\n"
            "📌 2 ta katta harf + 7 ta raqam"
        ),
        "passport_number_error": "❌ Noto'g'ri format!\n📌 Misol: AA1234567 (2 harf + 7 raqam)",

        # Certificate
        "cert_ask": "📜 <b>Ingliz tili sertifikatingiz bormi?</b>",
        "cert_options": ["📝 IELTS", "🇪🇺 CEFR", "📄 Boshqa sertifikat", "❌ Yo'q"],

        # IELTS
        "ielts_score_ask": (
            "📊 <b>IELTS balingizni kiriting</b>\n\n"
            "📋 Format: <code>6.5</code>\n"
            "⚠️ Diapazon: 0.0 – 9.0 | Qadam: 0.5"
        ),
        "ielts_score_error": (
            "❌ Noto'g'ri ball!\n"
            "• 0.0 dan 9.0 gacha\n"
            "• Qadam: 0.5 (masalan: 6.0, 6.5, 7.0)"
        ),
        "ielts_send_type_ask": "📤 <b>IELTS sertifikatini qanday yuborasiz?</b>",
        "cert_send_options": ["📷 Rasm", "🆔 ID raqam"],
        "ielts_photo_ask": "📸 IELTS sertifikat rasmini yuklang (jpg/png, max 5MB):",
        "ielts_id_ask": (
            "🆔 <b>IELTS Certificate ID kiriting</b>\n\n"
            "📋 Misol: <code>21UZ123456AB</code>\n"
            "⚠️ 6–20 ta belgi, faqat harf va raqamlar"
        ),
        "ielts_id_error": "❌ Noto'g'ri format! 6–20 ta belgi, faqat harf va raqamlar.",

        # CEFR
        "cefr_level_ask": "🎯 <b>CEFR darajangizni tanlang:</b>",
        "cefr_options": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "cefr_send_type_ask": "📤 <b>CEFR sertifikatini qanday yuborasiz?</b>",
        "cefr_photo_ask": "📸 CEFR sertifikat rasmini yuklang (jpg/png, max 5MB):",
        "cefr_id_ask": (
            "🆔 <b>CEFR sertifikat ID raqamini kiriting</b>\n\n"
            "📋 Misol: <code>CEFR123456</code>\n"
            "⚠️ 5–20 ta belgi"
        ),
        "cefr_id_error": "❌ Noto'g'ri format! 5–20 ta belgi, faqat harf va raqamlar.",

        # Other cert
        "other_name_ask": (
            "📝 <b>Qaysi sertifikat ekanini yozing</b>\n\n"
            "📌 Masalan: TOEFL, Duolingo, Cambridge"
        ),
        "other_name_error": "❌ Kamida 3 ta belgi kiriting!",
        "other_score_ask": (
            "📊 <b>Natijangizni kiriting</b>\n\n"
            "📌 Masalan: 95 (TOEFL) yoki 120 (Duolingo)"
        ),
        "other_score_error": "❌ Natija bo'sh bo'lmasin!",
        "other_send_type_ask": "📤 <b>Sertifikatni qanday yuborasiz?</b>",
        "other_photo_ask": "📸 Sertifikat rasmini yuklang (jpg/png, max 5MB):",
        "other_id_ask": (
            "🆔 <b>Sertifikat ID raqamini kiriting</b>\n\n"
            "⚠️ 5–25 ta belgi, harf va raqamlar"
        ),
        "other_id_error": "❌ Noto'g'ri format! 5–25 ta belgi, faqat harf va raqamlar.",

        # Photo generic error
        "photo_error": "❌ Iltimos, rasm yuboring! (jpg/png, max 5MB)",
        "photo_upload_ok": "✅ Rasm muvaffaqiyatli qabul qilindi!",

        # Exam date
        "exam_date_ask": "📅 <b>Imtihon kunini tanlang:</b>",
        "exam_dates_raw": ["13.05.2026", "10.06.2026", "24.06.2026", "15.07.2026"],

        # Contact time
        "contact_time_ask": (
            "⏰ <b>Siz bilan bog'lanish uchun qulay vaqtni yozing</b>\n\n"
            "📌 Masalan: 09:00 – 10:00 oralig'ida (18:00 gacha)"
        ),
        "contact_time_error": "❌ Iltimos, qulay vaqtni kiriting!",

        # Email & payment
        "email_ask": (
            "📧 <b>Elektron pochtangizni kiriting</b>\n\n"
            "📌 Misol: <code>ali@gmail.com</code>"
        ),
        "email_error": "❌ Noto'g'ri email formati!",
        "payment_ask": "💳 <b>To'lov usulini tanlang:</b>",
        "payment_options": [
            "💳 Payme orqali onlayn",
            "🏢 Joyida — naqd yoki boshqa usul",
        ],
        "payment_error": "❌ Iltimos, pastdagi tugmalardan birini tanlang.",

        # PayMe QR choice
        "payment_qr_choice_ask": "💳 <b>To'lov usulini tanlang:</b>",
        "payment_qr_options": ["📷 QR-kod orqali to'lash", "📱 Qo'lda (QR-kodsiz)"],
        "payment_qr_error": "❌ Iltimos, pastdagi tugmalardan birini tanlang.",

        # PayMe via QR
        "payment_payme_qr_text": (
            "Ariza beruvchi \"Payme\" onlayn xizmatidan foydalangan holda onlayn to'lashi mumkin. "
            "\"Payme\" orqali to'lovni amalga oshirish uchun qo'shimcha to'lov olinmaydi.\n\n"
            "🚫 <b>Ro'yxatdan o'tish to'lovlari qaytarilmaydi!</b>\n\n"
            "To'lovdan so'ng chek/kvitansiya rasmini botga yuboring."
        ),

        # PayMe manual instruction
        "payment_payme_manual": (
            "📱 <b>Payme orqali qo'lda to'lash (QR-kodsiz)</b>\n\n"
            "1️⃣ <b>Payme</b> ilovasini oching.\n"
            "2️⃣ Yuqori o'ng burchakdagi <b>🔍 qidiruv</b> belgisiga bosing.\n"
            "3️⃣ Qidiruvga <b>«Amity»</b> deb kiriting.\n"
            "4️⃣ <b>«AMITY UNIVERSITY in TASHKENT»</b> ta'minotchisini tanlang.\n\n"
            "📋 <b>To'lov oynasida quyidagilarni to'ldiring:</b>\n\n"
            "• <b>F.I.Sh</b> — ism va familiyangizni kiriting\n"
            "• <b>Fakultet dasturi nomi</b> — <code>International Foundation Studies</code> tanlang\n"
            "• <b>Shartnoma Raqami</b> — bu maydonni bo'sh qoldiring (kirish imtihoni uchun shartnoma raqami berilmaydi)\n"
            "• <b>Telefon raqami</b> — botda ko'rsatilgan raqamingizni kiriting\n"
            "• <b>Uchun to'lov</b> — <code>Admission 2026</code> tanlang\n"
            "• <b>To'lov summasi</b> — <code>200 000 so'm</code> kiriting\n\n"
            "✅ Ma'lumotlarni to'ldirib to'lovni amalga oshiring.\n"
            "🚫 <b>Ro'yxatdan o'tish to'lovlari qaytarilmaydi!</b>\n\n"
            "To'lovdan so'ng chek/kvitansiya rasmini botga yuboring."
        ),

        "payment_payme_instruction": "",  # legacy — no longer used directly
        "payment_receipt_ask": (
            "🧾 <b>Payme to'lovi cheki yoki kvitansiyasini rasm sifatida yuboring</b>\n\n"
            "📋 Format: jpg / png, max 5 MB\n"
            "⚠️ Bu qadam majburiy."
        ),
        "payment_receipt_error": "❌ Iltimos, chek/kvitansiya rasmini yuboring (jpg/png, max 5 MB).",

        # Summary
        "summary_title": "📋 <b>Ma'lumotlaringizni tekshiring:</b>",
        "summary_field_name": "👤 Ism Familiya",
        "summary_field_phone": "📱 Telefon",
        "summary_field_age": "🎂 Yosh",
        "summary_field_education": "🎓 Ta'lim",
        "summary_field_direction": "📚 Yo'nalish",
        "summary_field_passport": "🪪 Pasport",
        "summary_field_cert": "📜 Sertifikat",
        "summary_field_exam_date": "📅 Imtihon kuni",
        "summary_field_contact": "⏰ Bog'lanish vaqti",
        "summary_field_email": "📧 Email",
        "summary_field_payment": "💳 To'lov",
        "summary_payment_payme_short": "Payme (onlayn)",
        "summary_payment_onsite_short": "Joyida (naqd / boshqa)",
        "summary_field_payment_receipt": "🧾 Payme cheki",
        "summary_payment_receipt_ok": "✅ Yuborildi",
        "summary_confirm": "✅ Ma'lumotlar to'g'ri — Tasdiqlash",
        "summary_edit": "✏️ Ma'lumotni o'zgartirish",
        "edit_choose_field": "✏️ <b>Qaysi maydonni o'zgartirmoqchisiz?</b>",
        "edit_back_to_summary": "⬅️ Summaryga qaytish",

        # Buttons
        "back_btn": "⬅️ Orqaga",
        "cancel_btn": "❌ Bekor qilish",
        "text_reply_expected": "❌ Iltimos, matn xabar yuboring.",

        # Final
        "success": (
            "🎉 <b>Rahmat!</b>\n\n"
            "Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
            "Tez orada siz bilan bog'lanamiz! 📞"
        ),
        "cancelled": (
            "❌ Ro'yxatdan o'tish bekor qilindi.\n"
            "Qayta boshlash uchun /start ni bosing."
        ),
        "already_in_progress": (
            "⚠️ Siz allaqachon ro'yxatdan o'tish jarayonidasiz.\n"
            "Qayta boshlash uchun /restart ni bosing."
        ),

        # Passport type labels (for summary)
        "passport_type_photo": "📷 Rasm yuborildi",
        "passport_type_photo_multi": "📷 {n} ta rasm yuborildi",
        "passport_type_number": "🔢",
        "no_cert": "❌ Yo'q",
    },

    # ═══════════════════════════════════════════
    #  RUSSIAN
    # ═══════════════════════════════════════════
    "ru": {
        "choose_language": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "welcome": (
            "Здравствуйте! 👋\n\n"
            "Вы находитесь в официальном Telegram-боте "
            "<b>Международного Университета Amity в Ташкенте</b>.\n\n"
            "Для подачи документов заполните следующие данные.\n\n"
            "⚠️ <b>Внимание!</b> Все поля обязательны для заполнения."
        ),
        "full_name_ask": (
            "👤 <b>Введите ваше имя и фамилию</b>\n\n"
            "📋 Формат: <code>Имя Фамилия</code>\n"
            "📌 Пример: <code>Али Валиев</code>"
        ),
        "full_name_error": (
            "❌ Неверный формат!\n"
            "• Только буквы\n"
            "• Минимум 2 слова\n"
            "📌 Пример: Али Валиев"
        ),
        "phone_ask": (
            "📱 <b>Отправьте ваш номер телефона</b>\n\n"
            "📋 Формат: <code>+998901234567</code>\n\n"
            "👇 Нажмите кнопку ниже или введите вручную:"
        ),
        "phone_btn": "📱 Поделиться номером",
        "phone_error": "❌ Неверный формат!\n📌 Пример: +998901234567",
        "phone_duplicate": (
            "❌ <b>Этот номер телефона уже зарегистрирован!</b>\n\n"
            "Если считаете это ошибкой, свяжитесь с нами:\n"
            "📞 +998 71 123-45-67\n"
            "🔄 Введите другой номер для регистрации."
        ),
        "age_ask": (
            "🎂 <b>Введите ваш возраст</b>\n\n"
            "📋 Формат: <code>20</code>\n"
            "⚠️ Диапазон: 16 – 35 лет"
        ),
        "age_error": "❌ Возраст должен быть от 16 до 35!\n📌 Введите целое число, например: 20",
        "education_ask": "🎓 <b>Выберите ваш статус образования:</b>",
        "education_options": [
            "🏫 Школьник",
            "🏛 Лицей / колледж",
            "🎓 Университет",
            "💼 Работаю",
            "📝 Другое",
        ],
        "direction_ask": "📚 <b>Какое направление вас интересует?</b>",
        "direction_options": [
            "💻 IT",
            "🤖 Artificial Intelligence & Data Science",
            "🔐 Cybersecurity & Blockchain",
            "💼 Business Administration",
            "📊 Economics",
            "✈️ Tourism",
            "🇬🇧 English Language",
        ],
        "passport_choice_ask": "🪪 <b>Как хотите отправить данные паспорта?</b>",
        "passport_choice_options": ["📷 Загрузить фото", "🔢 Ввести номер"],
        "passport_photo_ask": (
            "📸 <b>Загрузите фото паспорта</b>\n\n"
            "Можно отправить одно или несколько фото (jpg/png, каждое до 5 MB).\n"
            "Когда все фото отправлены, нажмите <b>«Готово»</b>."
        ),
        "passport_photo_done_btn": "✅ Готово — все фото отправлены",
        "passport_photo_need_one": "❌ Отправьте хотя бы одно фото паспорта.",
        "passport_photo_more": (
            "✅ Фото принято. Можете отправить ещё или нажмите «Готово»."
        ),
        "passport_photo_error": "❌ Пожалуйста, отправьте фото! (jpg/png, макс 5MB)",
        "passport_number_ask": (
            "🔢 <b>Введите серию и номер паспорта</b>\n\n"
            "📋 Формат: <code>AA1234567</code>\n"
            "📌 2 заглавные буквы + 7 цифр"
        ),
        "passport_number_error": "❌ Неверный формат!\n📌 Пример: AA1234567 (2 буквы + 7 цифр)",
        "cert_ask": "📜 <b>У вас есть сертификат по английскому языку?</b>",
        "cert_options": ["📝 IELTS", "🇪🇺 CEFR", "📄 Другой сертификат", "❌ Нет"],
        "ielts_score_ask": (
            "📊 <b>Введите ваш балл IELTS</b>\n\n"
            "📋 Формат: <code>6.5</code>\n"
            "⚠️ Диапазон: 0.0 – 9.0 | Шаг: 0.5"
        ),
        "ielts_score_error": (
            "❌ Неверный балл!\n"
            "• От 0.0 до 9.0\n"
            "• Шаг: 0.5 (например: 6.0, 6.5, 7.0)"
        ),
        "ielts_send_type_ask": "📤 <b>Как отправите сертификат IELTS?</b>",
        "cert_send_options": ["📷 Фото", "🆔 ID номер"],
        "ielts_photo_ask": "📸 Загрузите фото сертификата IELTS (jpg/png, макс 5MB):",
        "ielts_id_ask": (
            "🆔 <b>Введите IELTS Certificate ID</b>\n\n"
            "📋 Пример: <code>21UZ123456AB</code>\n"
            "⚠️ 6–20 символов, только буквы и цифры"
        ),
        "ielts_id_error": "❌ Неверный формат! 6–20 символов, только буквы и цифры.",
        "cefr_level_ask": "🎯 <b>Выберите ваш уровень CEFR:</b>",
        "cefr_options": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "cefr_send_type_ask": "📤 <b>Как отправите сертификат CEFR?</b>",
        "cefr_photo_ask": "📸 Загрузите фото сертификата CEFR (jpg/png, макс 5MB):",
        "cefr_id_ask": (
            "🆔 <b>Введите ID сертификата CEFR</b>\n\n"
            "📋 Пример: <code>CEFR123456</code>\n"
            "⚠️ 5–20 символов"
        ),
        "cefr_id_error": "❌ Неверный формат! 5–20 символов, только буквы и цифры.",
        "other_name_ask": (
            "📝 <b>Напишите название сертификата</b>\n\n"
            "📌 Например: TOEFL, Duolingo, Cambridge"
        ),
        "other_name_error": "❌ Введите минимум 3 символа!",
        "other_score_ask": (
            "📊 <b>Введите ваш результат</b>\n\n"
            "📌 Например: 95 (TOEFL) или 120 (Duolingo)"
        ),
        "other_score_error": "❌ Результат не может быть пустым!",
        "other_send_type_ask": "📤 <b>Как отправите сертификат?</b>",
        "other_photo_ask": "📸 Загрузите фото сертификата (jpg/png, макс 5MB):",
        "other_id_ask": (
            "🆔 <b>Введите ID номер сертификата</b>\n\n"
            "⚠️ 5–25 символов, буквы и цифры"
        ),
        "other_id_error": "❌ Неверный формат! 5–25 символов, только буквы и цифры.",
        "photo_error": "❌ Пожалуйста, отправьте фото! (jpg/png, макс 5MB)",
        "photo_upload_ok": "✅ Фото успешно получено!",
        "exam_dates_raw": ["13.05.2026", "10.06.2026", "24.06.2026", "15.07.2026"],
        "contact_time_ask": (
            "⏰ <b>Напишите удобное время для связи</b>\n\n"
            "📌 Например: с 09:00 до 10:00 (до 18:00)"
        ),
        "contact_time_error": "❌ Пожалуйста, укажите удобное время!",

        "email_ask": (
            "📧 <b>Введите вашу электронную почту</b>\n\n"
            "📌 Пример: <code>ali@gmail.com</code>"
        ),
        "email_error": "❌ Неверный формат email!",
        "payment_ask": "💳 <b>Выберите способ оплаты:</b>",
        "payment_options": [
            "💳 Онлайн через Payme",
            "🏢 На месте — наличными или другим способом",
        ],
        "payment_error": "❌ Пожалуйста, выберите один из вариантов ниже.",

        # PayMe QR choice
        "payment_qr_choice_ask": "💳 <b>Выберите способ оплаты через Payme:</b>",
        "payment_qr_options": ["📷 Оплата по QR-коду", "📱 Вручную (без QR-кода)"],
        "payment_qr_error": "❌ Пожалуйста, выберите один из вариантов ниже.",

        # PayMe via QR
        "payment_payme_qr_text": (
            "Абитуриент может оплатить онлайн через сервис \"Payme\". "
            "За оплату через \"Payme\" дополнительная комиссия не взимается.\n\n"
            "🚫 <b>Регистрационный взнос не возвращается!</b>\n\n"
            "После оплаты отправьте фото чека/квитанции в бот."
        ),

        # PayMe manual instruction
        "payment_payme_manual": (
            "📱 <b>Оплата через Payme вручную (без QR-кода)</b>\n\n"
            "1️⃣ Откройте приложение <b>Payme</b>.\n"
            "2️⃣ Нажмите на значок <b>🔍 поиска</b> в правом верхнем углу.\n"
            "3️⃣ В строке поиска введите <b>«Amity»</b>.\n"
            "4️⃣ Выберите поставщика <b>«AMITY UNIVERSITY in TASHKENT»</b>.\n\n"
            "📋 <b>Заполните поля в окне оплаты:</b>\n\n"
            "• <b>F.I.Sh</b> — введите имя и фамилию\n"
            "• <b>Fakultet dasturi nomi</b> — выберите <code>International Foundation Studies</code>\n"
            "• <b>Shartnoma Raqami</b> — оставьте пустым (номер договора не выдаётся для вступительного экзамена)\n"
            "• <b>Telefon raqami</b> — введите номер телефона, указанный в боте\n"
            "• <b>Uchun to'lov</b> — выберите <code>Admission 2026</code>\n"
            "• <b>To'lov summasi</b> — введите <code>200 000 so'm</code>\n\n"
            "✅ Заполните данные и завершите оплату.\n"
            "🚫 <b>Регистрационный взнос не возвращается!</b>\n\n"
            "После оплаты отправьте фото чека/квитанции в бот."
        ),

        "payment_payme_instruction": "",  # legacy
        "payment_receipt_ask": (
            "🧾 <b>Отправьте фото чека или квитанции об оплате через Payme</b>\n\n"
            "📋 Формат: jpg / png, макс 5 MB\n"
            "⚠️ Этот шаг обязателен."
        ),
        "payment_receipt_error": "❌ Пожалуйста, отправьте фото чека/квитанции (jpg/png, макс 5 MB).",

        "summary_title": "📋 <b>Проверьте ваши данные:</b>",
        "summary_field_name": "👤 Имя Фамилия",
        "summary_field_phone": "📱 Телефон",
        "summary_field_age": "🎂 Возраст",
        "summary_field_education": "🎓 Образование",
        "summary_field_direction": "📚 Направление",
        "summary_field_passport": "🪪 Паспорт",
        "summary_field_cert": "📜 Сертификат",
        "summary_field_exam_date": "📅 Дата экзамена",
        "summary_field_contact": "⏰ Время для связи",
        "summary_field_email": "📧 Email",
        "summary_field_payment": "💳 Оплата",
        "summary_payment_payme_short": "Payme (онлайн)",
        "summary_payment_onsite_short": "На месте (наличные / другое)",
        "summary_field_payment_receipt": "🧾 Чек Payme",
        "summary_payment_receipt_ok": "✅ Отправлен",
        "summary_confirm": "✅ Данные верны — Подтвердить",
        "summary_edit": "✏️ Изменить данные",
        "edit_choose_field": "✏️ <b>Какое поле хотите изменить?</b>",
        "edit_back_to_summary": "⬅️ Вернуться к проверке",
        "back_btn": "⬅️ Назад",
        "cancel_btn": "❌ Отмена",
        "text_reply_expected": "❌ Пожалуйста, отправьте текстовое сообщение.",
        "success": (
            "🎉 <b>Спасибо!</b>\n\n"
            "Вы успешно зарегистрированы.\n"
            "Мы свяжемся с вами в ближайшее время! 📞"
        ),
        "cancelled": (
            "❌ Регистрация отменена.\n"
            "Для повторного начала нажмите /start"
        ),
        "already_in_progress": (
            "⚠️ Вы уже в процессе регистрации.\n"
            "Для перезапуска нажмите /restart"
        ),
        "passport_type_photo": "📷 Фото загружено",
        "passport_type_photo_multi": "📷 Отправлено фото: {n}",
        "passport_type_number": "🔢",
        "no_cert": "❌ Нет",
    },

    # ═══════════════════════════════════════════
    #  ENGLISH
    # ═══════════════════════════════════════════
    "en": {
        "choose_language": "🌐 Tilni tanlang / Выберите язык / Choose language:",
        "welcome": (
            "Hello! 👋\n\n"
            "You are in the official Telegram bot of "
            "<b>Amity University Tashkent</b>.\n\n"
            "Please fill in the following details to submit your application.\n\n"
            "⚠️ <b>Note:</b> All fields are mandatory."
        ),
        "full_name_ask": (
            "👤 <b>Enter your full name</b>\n\n"
            "📋 Format: <code>First Last</code>\n"
            "📌 Example: <code>Ali Valiyev</code>"
        ),
        "full_name_error": (
            "❌ Invalid format!\n"
            "• Letters only\n"
            "• At least 2 words\n"
            "📌 Example: Ali Valiyev"
        ),
        "phone_ask": (
            "📱 <b>Send your phone number</b>\n\n"
            "📋 Format: <code>+998901234567</code>\n\n"
            "👇 Tap the button below or type manually:"
        ),
        "phone_btn": "📱 Share phone number",
        "phone_error": "❌ Invalid format!\n📌 Example: +998901234567",
        "phone_duplicate": (
            "❌ <b>This phone number is already registered!</b>\n\n"
            "If you think this is an error, please contact us:\n"
            "📞 +998 71 123-45-67\n"
            "🔄 Enter a different number to register."
        ),
        "age_ask": (
            "🎂 <b>Enter your age</b>\n\n"
            "📋 Format: <code>20</code>\n"
            "⚠️ Range: 16 – 35"
        ),
        "age_error": "❌ Age must be between 16 and 35!\n📌 Enter a whole number, e.g.: 20",
        "education_ask": "🎓 <b>Select your education status:</b>",
        "education_options": [
            "🏫 School student",
            "🏛 Lyceum / college",
            "🎓 University",
            "💼 Working",
            "📝 Other",
        ],
        "direction_ask": "📚 <b>Which direction are you interested in?</b>",
        "direction_options": [
            "💻 IT",
            "🤖 Artificial Intelligence & Data Science",
            "🔐 Cybersecurity & Blockchain",
            "💼 Business Administration",
            "📊 Economics",
            "✈️ Tourism",
            "🇬🇧 English Language",
        ],
        "passport_choice_ask": "🪪 <b>How would you like to send passport data?</b>",
        "passport_choice_options": ["📷 Upload photo", "🔢 Enter number"],
        "passport_photo_ask": (
            "📸 <b>Upload passport photo(s)</b>\n\n"
            "You may send one or more photos (jpg/png, up to 5 MB each).\n"
            "When you are finished, tap <b>«Done»</b>."
        ),
        "passport_photo_done_btn": "✅ Done — all photos sent",
        "passport_photo_need_one": "❌ Please send at least one passport photo.",
        "passport_photo_more": (
            "✅ Photo received. You can send another or tap «Done»."
        ),
        "passport_photo_error": "❌ Please send a photo! (jpg/png, max 5MB)",
        "passport_number_ask": (
            "🔢 <b>Enter your passport series and number</b>\n\n"
            "📋 Format: <code>AA1234567</code>\n"
            "📌 2 capital letters + 7 digits"
        ),
        "passport_number_error": "❌ Invalid format!\n📌 Example: AA1234567 (2 letters + 7 digits)",
        "cert_ask": "📜 <b>Do you have an English language certificate?</b>",
        "cert_options": ["📝 IELTS", "🇪🇺 CEFR", "📄 Other certificate", "❌ None"],
        "ielts_score_ask": (
            "📊 <b>Enter your IELTS score</b>\n\n"
            "📋 Format: <code>6.5</code>\n"
            "⚠️ Range: 0.0 – 9.0 | Step: 0.5"
        ),
        "ielts_score_error": (
            "❌ Invalid score!\n"
            "• From 0.0 to 9.0\n"
            "• Step: 0.5 (e.g. 6.0, 6.5, 7.0)"
        ),
        "ielts_send_type_ask": "📤 <b>How will you send the IELTS certificate?</b>",
        "cert_send_options": ["📷 Photo", "🆔 ID number"],
        "ielts_photo_ask": "📸 Upload IELTS certificate photo (jpg/png, max 5MB):",
        "ielts_id_ask": (
            "🆔 <b>Enter IELTS Certificate ID</b>\n\n"
            "📋 Example: <code>21UZ123456AB</code>\n"
            "⚠️ 6–20 characters, letters and digits only"
        ),
        "ielts_id_error": "❌ Invalid format! 6–20 characters, letters and digits only.",
        "cefr_level_ask": "🎯 <b>Select your CEFR level:</b>",
        "cefr_options": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "cefr_send_type_ask": "📤 <b>How will you send the CEFR certificate?</b>",
        "cefr_photo_ask": "📸 Upload CEFR certificate photo (jpg/png, max 5MB):",
        "cefr_id_ask": (
            "🆔 <b>Enter CEFR certificate ID</b>\n\n"
            "📋 Example: <code>CEFR123456</code>\n"
            "⚠️ 5–20 characters"
        ),
        "cefr_id_error": "❌ Invalid format! 5–20 characters, letters and digits only.",
        "other_name_ask": (
            "📝 <b>Write the name of the certificate</b>\n\n"
            "📌 Example: TOEFL, Duolingo, Cambridge"
        ),
        "other_name_error": "❌ Enter at least 3 characters!",
        "other_score_ask": (
            "📊 <b>Enter your result</b>\n\n"
            "📌 Example: 95 (TOEFL) or 120 (Duolingo)"
        ),
        "other_score_error": "❌ Result cannot be empty!",
        "other_send_type_ask": "📤 <b>How will you send the certificate?</b>",
        "other_photo_ask": "📸 Upload certificate photo (jpg/png, max 5MB):",
        "other_id_ask": (
            "🆔 <b>Enter certificate ID number</b>\n\n"
            "⚠️ 5–25 characters, letters and digits"
        ),
        "other_id_error": "❌ Invalid format! 5–25 characters, letters and digits only.",
        "photo_error": "❌ Please send a photo! (jpg/png, max 5MB)",
        "photo_upload_ok": "✅ Photo received successfully!",
        "exam_dates_raw": ["13.05.2026", "10.06.2026", "24.06.2026", "15.07.2026"],
        "contact_time_ask": (
            "⏰ <b>Write a convenient time to contact you</b>\n\n"
            "📌 Example: 09:00 – 10:00 (until 18:00)"
        ),
        "contact_time_error": "❌ Please specify a convenient time!",

        "email_ask": (
            "📧 <b>Enter your email address</b>\n\n"
            "📌 Example: <code>ali@gmail.com</code>"
        ),
        "email_error": "❌ Invalid email format!",
        "payment_ask": "💳 <b>Choose a payment method:</b>",
        "payment_options": [
            "💳 Online via Payme",
            "🏢 On-site — cash or other method",
        ],
        "payment_error": "❌ Please choose one of the options below.",

        # PayMe QR choice
        "payment_qr_choice_ask": "💳 <b>Choose your Payme payment method:</b>",
        "payment_qr_options": ["📷 Pay via QR code", "📱 Manual (without QR code)"],
        "payment_qr_error": "❌ Please choose one of the options below.",

        # PayMe via QR
        "payment_payme_qr_text": (
            "The applicant can pay online via the \"Payme\" service. "
            "No additional fee is charged for payment through \"Payme\".\n\n"
            "🚫 <b>Registration fees are non-refundable!</b>\n\n"
            "After payment, send a photo of your receipt to the bot."
        ),

        # PayMe manual instruction
        "payment_payme_manual": (
            "📱 <b>Manual Payme payment (without QR code)</b>\n\n"
            "1️⃣ Open the <b>Payme</b> app.\n"
            "2️⃣ Tap the <b>🔍 search</b> icon in the top right corner.\n"
            "3️⃣ Search for <b>«Amity»</b>.\n"
            "4️⃣ Select the provider <b>«AMITY UNIVERSITY in TASHKENT»</b>.\n\n"
            "📋 <b>Fill in the payment form:</b>\n\n"
            "• <b>F.I.Sh</b> — enter your first and last name\n"
            "• <b>Fakultet dasturi nomi</b> — select <code>International Foundation Studies</code>\n"
            "• <b>Shartnoma Raqami</b> — leave blank (no contract number is issued for the entrance exam)\n"
            "• <b>Telefon raqami</b> — enter the same phone number you provided in the bot\n"
            "• <b>Uchun to'lov</b> — select <code>Admission 2026</code>\n"
            "• <b>To'lov summasi</b> — enter <code>200 000 so'm</code>\n\n"
            "✅ Complete the form and confirm payment.\n"
            "🚫 <b>Registration fees are non-refundable!</b>\n\n"
            "After payment, send a photo of your receipt to the bot."
        ),

        "payment_payme_instruction": "",  # legacy
        "payment_receipt_ask": (
            "🧾 <b>Send a photo of your Payme payment receipt</b>\n\n"
            "📋 Format: jpg / png, max 5 MB\n"
            "⚠️ This step is mandatory."
        ),
        "payment_receipt_error": "❌ Please send a photo of the receipt (jpg/png, max 5 MB).",

        "summary_title": "📋 <b>Please check your information:</b>",
        "summary_field_name": "👤 Full Name",
        "summary_field_phone": "📱 Phone",
        "summary_field_age": "🎂 Age",
        "summary_field_education": "🎓 Education",
        "summary_field_direction": "📚 Direction",
        "summary_field_passport": "🪪 Passport",
        "summary_field_cert": "📜 Certificate",
        "summary_field_exam_date": "📅 Exam Date",
        "summary_field_contact": "⏰ Contact Time",
        "summary_field_email": "📧 Email",
        "summary_field_payment": "💳 Payment",
        "summary_payment_payme_short": "Payme (online)",
        "summary_payment_onsite_short": "On-site (cash / other)",
        "summary_field_payment_receipt": "🧾 Payme receipt",
        "summary_payment_receipt_ok": "✅ Sent",
        "summary_confirm": "✅ Information is correct — Confirm",
        "summary_edit": "✏️ Edit information",
        "edit_choose_field": "✏️ <b>Which field would you like to edit?</b>",
        "edit_back_to_summary": "⬅️ Back to review",
        "back_btn": "⬅️ Back",
        "cancel_btn": "❌ Cancel",
        "text_reply_expected": "❌ Please send a text message.",
        "success": (
            "🎉 <b>Thank you!</b>\n\n"
            "You have successfully registered.\n"
            "We will contact you soon! 📞"
        ),
        "cancelled": (
            "❌ Registration cancelled.\n"
            "Type /start to begin again."
        ),
        "already_in_progress": (
            "⚠️ You are already in the registration process.\n"
            "Type /restart to start over."
        ),
        "passport_type_photo": "📷 Photo uploaded",
        "passport_type_photo_multi": "📷 {n} photos uploaded",
        "passport_type_number": "🔢",
        "no_cert": "❌ None",
    },
}


def t(lang: str, key: str) -> Any:
    """Get text by language and key. Falls back to 'uz' if key not found."""
    return TEXTS.get(lang, TEXTS["uz"]).get(key, TEXTS["uz"].get(key, key))