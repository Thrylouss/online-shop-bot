from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import config

# Старт: выбор языка
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Русский"), KeyboardButton("O‘zbekcha")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "Выберите язык / Tilni tanlang:",
        reply_markup=reply_markup
    )

# Обработка выбора языка
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text.strip()
    if lang not in ["Русский", "O‘zbekcha"]:
        await update.message.reply_text("Пожалуйста, выберите язык кнопкой ниже.")
        return

    context.user_data["lang"] = "ru" if lang == "Русский" else "uz"

    # Кнопка отправки контакта
    contact_button = KeyboardButton(
        "📱 Отправить номер телефона" if lang == "Русский" else "📱 Telefon raqamini yuborish",
        request_contact=True
    )
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)

    msg = (
        "Пожалуйста, нажмите кнопку ниже, чтобы отправить номер телефона." if lang == "Русский"
        else "Iltimos, telefon raqamingizni yuborish uchun quyidagi tugmani bosing."
    )
    await update.message.reply_text(msg, reply_markup=reply_markup)

# Обработка контакта
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number
    lang = context.user_data.get("lang", "ru")

    try:
        response = requests.post(config.VERIFY_API_URL, json={"username": phone})
        data = response.json()

        if "code" in data:
            msg = {
                "ru": f"Каждые 5 минут код меняется.\nКод отправлен: {data['code']}",
                "uz": f"Har 5 daqiqada kod yangilanadi.\nKod yuborildi: {data['code']}"
            }[lang]
            await update.message.reply_text(msg)
        elif "detail" in data:
            await update.message.reply_text(data["detail"])
        elif isinstance(data, list):
            await update.message.reply_text(data[0])
        else:
            await update.message.reply_text("Неизвестный ответ от сервера." if lang == "ru" else "Nomaʼlum server javobi.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}" if lang == "ru" else f"Xatolik: {e}")

# Запрет ввода текста
async def reject_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    msg = {
        "ru": "Пожалуйста, используйте кнопку для отправки номера телефона 📱.",
        "uz": "Iltimos, raqam yuborish uchun faqat tugmadan foydalaning 📱."
    }[lang]
    await update.message.reply_text(msg)

# Инициализация
def create_bot():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(Русский|O‘zbekcha)$"), choose_language))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reject_text))

    return app