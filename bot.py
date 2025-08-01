from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправьте номер телефона для верификации.")


async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()

    try:
        response = requests.post(config.VERIFY_API_URL, json={"username": phone})
        data = response.json()

        if "code" in data:
            await update.message.reply_text(f"Код отправлен: {data['verification_code']}")
        elif "detail" in data:
            await update.message.reply_text(f"Ошибка: {data['detail']}")
        elif isinstance(data, list):
            await update.message.reply_text(data[0])
        else:
            await update.message.reply_text("Неизвестный ответ от сервера.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


def create_bot():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    return app
