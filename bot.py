import os
import google.generativeai as genai

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = model.generate_content(user_message)

        await update.message.reply_text(response.text)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
)

print("Gemini bot started 🚀")

app.run_polling(close_loop=False)
