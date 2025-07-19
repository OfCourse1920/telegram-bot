import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from flask import Flask
import threading

# ENV variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini URL
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Flask app to keep Render service alive
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

# Gemini + Telegram handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": user_message
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload)
        result = response.json()
        reply_text = result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        logging.error(f"Error from Gemini: {e}")
        reply_text = "Sorry, something went wrong with Gemini AI."

    await update.message.reply_text(reply_text)

# Start the Telegram bot
async def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    await application.run_polling()

# Entry point
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()

    import asyncio
    asyncio.run(main())
