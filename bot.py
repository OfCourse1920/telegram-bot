import os
import logging
from flask import Flask
from telegram.ext import Updater, MessageHandler, Filters
import requests
import threading

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_API_KEY}"

# Logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Flask app for keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Gemini handler
def handle_message(update, context):
    user_text = update.message.text
    logging.info(f"User said: {user_text}")
    payload = {"contents": [{"parts": [{"text": user_text}]}]}
    try:
        response = requests.post(GEMINI_URL, json=payload)
        response.raise_for_status()
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
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    logging.info("Bot started...")
    updater.idle()

if __name__ == "__main__":
    # Start Telegram bot in a separate thread
    threading.Thread(target=start_bot, daemon=True).start()
    # Run Flask app on Render's specified port
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
