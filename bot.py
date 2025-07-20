from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
import requests
import logging
from flask import Flask, request
import os
import threading

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.environ.get('PORT', 8080))  # Render assigns PORT

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

app = Flask(__name__)
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Gemini handler (async for webhooks)
async def handle_message(update: Update, context):
    user_text = update.message.text
    logging.info(f"User said: {user_text}")

    payload = {"contents": [{"parts": [{"text": user_text}]}]}

    try:
        response = requests.post(GEMINI_URL, json=payload)
        result = response.json()
        gemini_reply = result['candidates'][0]['content']['parts'][0]['text']
        await update.message.reply_text(gemini_reply, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Error contacting Gemini API.")

# Add handler
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask route for webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return 'OK'

# Set webhook on startup
def set_webhook():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"  # Use Render's env var
    application.bot.set_webhook(webhook_url)

# Run Flask
def run_flask():
    app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    set_webhook()
    run_flask()
