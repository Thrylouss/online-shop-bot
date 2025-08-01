from flask import Flask, request
from bot import create_bot
import config

flask_app = Flask(__name__)
bot_app = create_bot()

@flask_app.route(f"/webhook/{config.BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = request.get_json(force=True)
        bot_app.update_queue.put(update)
        return "ok"
