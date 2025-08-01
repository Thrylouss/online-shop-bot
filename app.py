from flask import Flask, request
from bot import create_bot
import config
from telegram import Update
import asyncio

flask_app = Flask(__name__)
bot_app = create_bot()

# глобальный флаг для инициализации бота один раз
bot_initialized = False

@flask_app.route(f"/webhook/{config.BOT_TOKEN}", methods=["POST"])
def webhook():
    global bot_initialized

    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, bot_app.bot)

    async def handle():
        global bot_initialized
        if not bot_initialized:
            await bot_app.initialize()
            bot_initialized = True
        await bot_app.process_update(update)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(handle())

    return "ok"