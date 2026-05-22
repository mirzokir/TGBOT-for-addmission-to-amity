# 🎓 Amity University Tashkent — Registration Bot

Telegram бот для регистрации абитуриентов.  
Python 3.11+ · aiogram 3 · SQLite

---

## 📁 Структура проекта

```
amity_bot/
├── bot.py                  ← точка входа
├── config.py               ← настройки из .env
├── database.py             ← SQLite (aiosqlite)
├── states.py               ← FSM-состояния
├── locales.py              ← тексты на 3 языках (uz / ru / en)
├── validators.py           ← валидация всех полей
├── keyboards.py            ← все клавиатуры
├── handlers/
│   ├── __init__.py
│   └── registration.py     ← основной FSM-обработчик
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Установка

### 1. Клонировать / скопировать папку

```bash
cd amity_bot
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать `.env` файл

```bash
cp .env.example .env
```

Откройте `.env` и заполните:

```env
BOT_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_ID=123456789
```

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен от [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | Ваш Telegram user_id (получить у [@userinfobot](https://t.me/userinfobot)) |

### 5. Запустить

```bash
python bot.py
```

---

## 🤖 Команды бота

| Команда | Описание |
|---|---|
| `/start` | Начать регистрацию |
| `/restart` | Перезапустить (сбросить прогресс) |
| `/cancel` | Отменить регистрацию |
| `/help` | Список команд |

---

## 🗺️ Flow регистрации

```
/start
  └─ Выбор языка (uz / ru / en)
       └─ Имя и Фамилия
            └─ Телефон (+998XXXXXXXXX)
                 └─ Возраст (16–35)
                      └─ Статус образования
                           └─ Направление
                                └─ Паспорт
                                │    ├─ Фото (jpg/png, ≤5MB)
                                │    └─ Номер (AA1234567)
                                └─ Сертификат
                                │    ├─ IELTS → балл → фото/ID
                                │    ├─ CEFR  → уровень → фото/ID
                                │    ├─ Другой → название → балл → фото/ID
                                │    └─ Нет
                                └─ Дата экзамена (inline)
                                     └─ Удобное время для связи
                                          └─ SUMMARY
                                               ├─ ✅ Подтвердить → сохранить в DB + уведомить админа
                                               └─ ✏️ Изменить → выбрать поле → ввести заново → SUMMARY
```

---

## 🗄️ База данных

Файл: `registrations.db` (создаётся автоматически при первом запуске)

Таблица `registrations`:

| Колонка | Тип | Описание |
|---|---|---|
| `id` | INTEGER PK | Авто-ID |
| `user_id` | INTEGER | Telegram user ID |
| `username` | TEXT | @username |
| `lang` | TEXT | `uz` / `ru` / `en` |
| `full_name` | TEXT | Имя Фамилия |
| `phone` | TEXT UNIQUE | +998XXXXXXXXX |
| `age` | INTEGER | 16–35 |
| `education` | TEXT | Статус образования |
| `direction` | TEXT | Выбранное направление |
| `passport_type` | TEXT | `photo` / `number` |
| `passport_data` | TEXT | file_id или серия+номер |
| `cert_type` | TEXT | `ielts` / `cefr` / `other` / `none` |
| `cert_data` | TEXT | JSON с деталями сертификата |
| `exam_date` | TEXT | Выбранная дата |
| `contact_time` | TEXT | Удобное время |
| `created_at` | TIMESTAMP | Дата регистрации |

---

## 📋 Валидация полей

| Поле | Правило |
|---|---|
| Имя | Только буквы, ≥2 слова |
| Телефон | `^\+998\d{9}$` |
| Возраст | 16 – 35, целое число |
| Паспорт (номер) | `^[A-Z]{2}[0-9]{7}$` |
| IELTS балл | 0.0 – 9.0, шаг 0.5 |
| IELTS ID | `^[A-Za-z0-9]{6,20}$` |
| CEFR ID | `^[A-Za-z0-9]{5,20}$` |
| Другой ID | `^[A-Za-z0-9]{5,25}$` |
| Фото | jpg/png, ≤5 MB |

---

## 📬 Уведомления админу

После успешной регистрации админ получает:
1. Форматированное сообщение со всеми данными
2. Фото паспорта (если было загружено)
3. Фото сертификата (если было загружено)

---

## 🔧 Дополнительно

**Дубликаты:** Повторная регистрация по тому же номеру телефона заблокирована с объяснением.

**Кнопка «Назад»:** Работает на каждом шаге, в том числе внутри блоков паспорта/сертификата.

**Редактирование:** После заполнения всех полей пользователь видит итоговый экран и может изменить любое поле.

**Для production:** Замените `MemoryStorage()` на `RedisStorage` в `bot.py`, чтобы FSM-состояния сохранялись при перезапуске бота.
