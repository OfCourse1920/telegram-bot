import os
from telegram.ext import Updater, MessageHandler, Filters
import requests
import logging
from flask import Flask
import threading

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_API_KEY}"

# Logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


# Gemini handler
def handle_message(update, context):
    user_text = update.message.text
    logging.info(f"User said: {user_text}")

    payload = {"contents": [{"parts": [{"text": user_text}]}]}

    try:
        response = requests.post(GEMINI_URL, json=payload)
        result = response.json()
        gemini_reply = result['candidates'][0]['content']['parts'][0]['text']
        update.message.reply_text(gemini_reply, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error: {e}")
        update.message.reply_text("Error contacting Gemini API.")


# Telegram bot setup
def start_bot():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(
        MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    logging.info("Bot started...")
    updater.idle()


# Keep-alive web server for UptimeRobot
app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running!"


def run_web():
    app.run(host='0.0.0.0', port=8080)


# Start both Flask and Bot in threads
threading.Thread(target=run_web).start()
threading.Thread(target=start_bot).start()
